"""Create file-geodatabase domains from docs/schema.yaml and (optionally) assign them.

Run in the ArcGIS Pro Python environment (needs arcpy + pyyaml):
  python make_gdb_domains.py docs/schema.yaml C:/path/whatcom.gdb [C:/path/whatcom.gdb/observations]

UNTESTED outside Pro -- run once on a scratch gdb first.
"""
import sys
import arcpy
import yaml

schema_path, gdb = sys.argv[1], sys.argv[2]
fc = sys.argv[3] if len(sys.argv) > 3 else None
schema = yaml.safe_load(open(schema_path))
existing = {d.name for d in arcpy.da.ListDomains(gdb)}
assign = {}  # field name -> domain name

# Coded-value domains
for dname, codes in schema["domains"].items():
    dom = f"d_{dname}"
    if dom not in existing:
        arcpy.management.CreateDomain(gdb, dom, f"{dname} codes", "TEXT", "CODED")
    for code, label in codes.items():
        arcpy.management.AddCodedValueToDomain(gdb, dom, code, label)

# Range domains for integer fields
for f in schema["fields"]:
    if f["type"] == "select_one":
        assign[f["name"]] = f"d_{f['domain']}"
    elif "min" in f and "max" in f:
        dom = f"d_{f['name']}_range"
        if dom not in existing:
            arcpy.management.CreateDomain(gdb, dom, f"{f['name']} range", "LONG", "RANGE")
        arcpy.management.SetValueForRangeDomain(gdb, dom, f["min"], f["max"])
        assign[f["name"]] = dom

if fc:
    fc_fields = {fld.name for fld in arcpy.ListFields(fc)}
    for field, dom in assign.items():
        if field in fc_fields:
            arcpy.management.AssignDomainToField(fc, field, dom)
            print(f"{field} -> {dom}")
print("Domains:", sorted({d.name for d in arcpy.da.ListDomains(gdb)}))
