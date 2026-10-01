"""Schema-driven QA + open data package export for the Whatcom Creek survey.

  python scripts/qa_pipeline.py --schema docs/schema.yaml --item <AGOL_ITEM_ID> --out data/release
  python scripts/qa_pipeline.py --schema docs/schema.yaml --csv data/raw/export.csv --out data/release

CSV input needs lon/lat columns (Survey123 CSV export uses x/y -- renamed automatically).
"""
import argparse
import datetime as dt
import json
from pathlib import Path

import pandas as pd
import yaml


# ---------- load ----------
def load_schema(path):
    return yaml.safe_load(open(path))


def load_from_agol(item_id, layer=0):
    """Pull the hosted layer. Uses ArcGIS API for Python (pip install arcgis)."""
    from arcgis.gis import GIS
    gis = GIS("home") if _in_pro() else GIS("https://www.arcgis.com", input("AGOL username: "))  # prompts for password
    fl = gis.content.get(item_id).layers[layer]
    sdf = fl.query(where="1=1", out_sr=4326, as_df=True)
    sdf["lon"] = sdf["SHAPE"].apply(lambda g: g.x if g is not None else None)
    sdf["lat"] = sdf["SHAPE"].apply(lambda g: g.y if g is not None else None)
    return pd.DataFrame(sdf.drop(columns="SHAPE"))


def _in_pro():
    try:
        import arcpy  # noqa: F401
        return True
    except ImportError:
        return False


def load_csv(path):
    df = pd.read_csv(path)
    return df.rename(columns={"x": "lon", "y": "lat"})


# ---------- QA ----------
def run_qa(df, schema, now=None):
    df = df.copy()
    tz = schema["timezone"]
    now = now or pd.Timestamp.now(tz="UTC")
    flags = {i: set() for i in df.index}

    def flag(mask, code):
        for i in df.index[mask.fillna(False)]:
            flags[i].add(code)

    ts = pd.to_datetime(df["survey_date"], utc=True, errors="coerce")
    df["local_date"] = ts.dt.tz_convert(tz).dt.date

    for f in schema["fields"]:
        name = f["name"]
        if f["type"] in ("geopoint", "image") or f.get("system") or name not in df:
            continue
        col = df[name]
        blank = col.isna() | (col.astype(str).str.strip() == "")

        if f.get("required"):
            flag(blank, "MISSING_REQ")
        if "required_if" in f:
            (cfield, cvals), = f["required_if"].items()
            applies = df[cfield].isin(cvals)
            flag(applies & blank, "MISSING_REQ")
            flag(~applies & ~blank, "NOT_APPLICABLE")
        if f["type"] == "select_one":
            flag(~blank & ~col.isin(schema["domains"][f["domain"]]), "BAD_DOMAIN")
        if "min" in f:
            num = pd.to_numeric(col, errors="coerce")
            flag(~blank & (num.isna() | (num < f["min"]) | (num > f["max"])
                           | (num % 1 != 0)), "OUT_OF_RANGE")
        if "max_length" in f:
            flag(col.astype(str).str.len().gt(f["max_length"]) & ~blank, "OUT_OF_RANGE")

    start = pd.Timestamp(schema["survey_window"]["start"]).date()
    end = pd.Timestamp(schema["survey_window"]["end"]).date()
    flag(ts > now, "DATE_FUTURE")
    flag(df["local_date"].notna() & ((df["local_date"] < start) | (df["local_date"] > end)),
         "DATE_WINDOW")

    if "gps_accuracy_m" in df:
        acc = pd.to_numeric(df["gps_accuracy_m"], errors="coerce")
        flag(acc.isna() | (acc > schema["gps_accuracy_warn_m"]), "GPS_ACCURACY")

    tol = schema["duplicate_tolerance"]
    key = pd.DataFrame({
        "lon": df["lon"].round(tol["coord_decimals"]),
        "lat": df["lat"].round(tol["coord_decimals"]),
        "t": ts.dt.floor(f"{tol['time_minutes']}min"),
        "o": df["obs_type"],
    })
    flag(key.duplicated(keep=False) & key.notna().all(axis=1), "DUPLICATE")

    for f in schema["fields"]:
        if f.get("per_visit") and f["name"] in df:
            n = df.groupby(["local_date", "observer"])[f["name"]].transform("nunique")
            flag(n > 1, "VISIT_INCONSISTENT")

    df["qa_flag"] = [("|".join(sorted(flags[i])) if flags[i] else "") for i in df.index]
    return df


def qa_summary(df, schema):
    rows = [{"check": "TOTAL_RECORDS", "n": len(df), "description": "Records evaluated"},
            {"check": "PASSED", "n": int((df["qa_flag"] == "").sum()),
             "description": "Records with no QA flags"}]
    for code, desc in schema["qa_flags"].items():
        rows.append({"check": code, "n": int(df["qa_flag"].str.contains(code).sum()),
                     "description": desc})
    return pd.DataFrame(rows)


# ---------- export ----------
def to_geojson(df, lon="lon", lat="lat"):
    feats = []
    for _, r in df.iterrows():
        props = {k: (None if pd.isna(v) else (v.isoformat() if hasattr(v, "isoformat") else v))
                 for k, v in r.drop([lon, lat]).items()}
        geom = (None if pd.isna(r[lon]) or pd.isna(r[lat])
                else {"type": "Point", "coordinates": [float(r[lon]), float(r[lat])]})
        feats.append({"type": "Feature", "geometry": geom, "properties": props})
    return {"type": "FeatureCollection", "features": feats}


def data_dictionary(schema):
    rows = []
    for f in schema["fields"]:
        rule = []
        if f.get("required"): rule.append("required")
        if "required_if" in f:
            (k, v), = f["required_if"].items()
            rule.append(f"required if {k} in {v}")
        if "min" in f: rule.append(f"{f['min']}-{f['max']}")
        if "max_length" in f: rule.append(f"max {f['max_length']} chars")
        dom = f.get("domain")
        rows.append({"field": f["name"], "type": f["type"], "label": f["label"],
                     "description": f["desc"], "rules": "; ".join(rule),
                     "domain": ("; ".join(f"{c}={l}" for c, l in schema["domains"][dom].items())
                                if dom else "")})
    rows.insert(4, {"field": "lon / lat", "type": "decimal", "label": "Longitude / latitude",
                    "description": f"Point coordinates, {schema['crs']}", "rules": "", "domain": ""})
    return pd.DataFrame(rows)


def export_package(df, schema, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    keep = ([f["name"] for f in schema["fields"]
             if f["type"] not in ("geopoint", "image") and f["name"] in df] + ["lon", "lat"])
    pkg = df[keep]
    pkg.to_csv(out / "observations.csv", index=False)
    (out / "observations.geojson").write_text(json.dumps(to_geojson(pkg), indent=1, default=str))
    summary = qa_summary(df, schema)
    summary.to_csv(out / "qa_summary.csv", index=False)
    data_dictionary(schema).to_csv(out / "data_dictionary.csv", index=False)
    ts = pd.to_datetime(df["survey_date"], utc=True, errors="coerce")
    meta = {
        "title": "Whatcom Creek Salmon Spawner Observations",
        "dataset": schema["dataset"], "schema_version": schema["version"],
        "created": dt.date.today().isoformat(),
        "temporal_extent": [str(ts.min()), str(ts.max())],
        "spatial_extent_wgs84": [float(df["lon"].min()), float(df["lat"].min()),
                                 float(df["lon"].max()), float(df["lat"].max())],
        "crs": schema["crs"], "record_count": len(df),
        "qa": summary.set_index("check")["n"].to_dict(),
        "files": sorted(p.name for p in out.iterdir()) + ["metadata.json"],
        "license": "CC-BY-4.0",  # decide + match repo LICENSE
        "contact": "FILL_IN",
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(summary.to_string(index=False))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--schema", required=True)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--item"); src.add_argument("--csv")
    p.add_argument("--out", default="data/release")
    a = p.parse_args()
    schema = load_schema(a.schema)
    raw = load_from_agol(a.item) if a.item else load_csv(a.csv)
    export_package(run_qa(raw, schema), schema, a.out)
