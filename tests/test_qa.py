"""Each synthetic row is built to trip specific QA codes (see fixture)."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import qa_pipeline as q  # noqa: E402

SCHEMA = q.load_schema(ROOT / "docs" / "schema.yaml")
NOW = pd.Timestamp("2026-10-05", tz="UTC")


def flags():
    df = q.run_qa(q.load_csv(ROOT / "tests/fixtures/synthetic_observations.csv"), SCHEMA, now=NOW)
    return [set(f.split("|")) - {""} for f in df["qa_flag"]]


def test_expected_codes():
    f = flags()
    assert "DUPLICATE" in f[0] and "DUPLICATE" in f[1]
    assert "MISSING_REQ" in f[2]            # carcass without species
    assert {"NOT_APPLICABLE", "GPS_ACCURACY"} <= f[3]  # habitat with species, 22 m
    assert "OUT_OF_RANGE" in f[4]           # count 900
    assert "BAD_DOMAIN" in f[5]             # reach R5
    assert {"DATE_FUTURE", "DATE_WINDOW"} <= f[7]
    assert "PARENT_MISMATCH" in f[8]        # R3 station on an R1 record
    assert not any("PARENT_MISMATCH" in x for x in f[:8])  # R5 row is BAD_DOMAIN only


def test_visit_inconsistency_flags_whole_visit():
    f = flags()
    assert all("VISIT_INCONSISTENT" in x for x in f[:7])   # one record says flow=high
    assert "VISIT_INCONSISTENT" not in f[7]


def test_every_code_documented():
    used = set().union(*flags())
    assert used <= set(SCHEMA["qa_flags"])
