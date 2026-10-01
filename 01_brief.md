# Whatcom Creek Salmon Monitoring — Brief

Condensed from the full plan (archived in repo `docs/plan.md`). Field schema lives in `02_schema.yaml`. Progress lives in `03_status.md`.

## Goal
Close the Esri gap (Survey123, Field Maps, AGOL, Pro, raster) with one real end-to-end monitoring workflow: **field collection → QA/QC → database → analysis → dashboard → documented data release**. Driving application: IWS Assistant Data Scientist (NPS I&M). Closes Oct 23, reviewed in order received. **Send Mon Oct 5 or Tue Oct 6.**

Repo: `github.com/MegaDeadCowboy/whatcom-creek-salmon-monitoring`
Folders: `/form /data/raw /data/release /scripts /report /docs /screenshots`

**Honest framing everywhere:** "Built an end-to-end field-to-dashboard monitoring workflow in ArcGIS." Never "proficient in ArcGIS" or years of experience.

## Schedule (~16–20 hrs)
| When | Phase | Output |
|---|---|---|
| Thu Oct 1 eve | 0 Setup | License confirmed, repo, reaches layer, DEM downloaded |
| Thu/Fri | 1 Form | XLSForm generated from schema, published, phone-tested, screenshots |
| Sat Oct 3 AM | 2 Field | Survey123 walk + Field Maps habitat points + photos (Sun AM 2nd walk optional) |
| Sat PM | 3 Pro | gdb + domains, public layers, slope → Zonal Stats gradient per reach, spatial join summary, metadata, layout PDF |
| Sun | 4 QA + DRR | qa_pipeline.py → data package → Quarto DRR |
| Sun eve | 5 Dashboard | Map by species, counts by reach×species, over time, QA passed/flagged, latest date; public, incognito-tested |
| Mon Oct 5 | 6 Ship | README, all links tested in incognito, resume/cover letter updated, send |

## Scope rules
**Must ship:** Survey123 form, ≥1 real survey, Field Maps map, Pro project (gdb + domains + 1 raster analysis + 1 layout), QA script + data package, DRR, public Dashboard, README.
**Stretch (only if ahead):** PostGIS sync (ties to WERAP + "migration" duty), 3rd survey later in Oct, ModelBuilder/ArcPy reach summary tool.
**Cut order if behind:** stretch → Field Maps → raster → 2nd survey.
**Never cut:** Survey123 form, QA script, DRR, README.
**Out of scope:** Power BI, VBA, Access/SQL Server. Name them honestly as gaps in the cover letter.

## Setup facts
- License: ArcGIS for Personal Use (~$100/yr, non-commercial). Confirm it includes Survey123, Field Maps, Dashboards, and API for Python **before** buying. Don't use the WWU email for trials.
- Public data (verify Phase 0): NHDPlus HR or WA DNR hydro · WDFW SalmonScape · WDFW Fish Passage inventory · WA DNR LiDAR Portal bare-earth DEM · USGS/City of Bellingham gage if one exists · Esri basemaps.
- Survey design: 3–4 reaches split at clear landmarks, stored as a layer. One point per observation. Zero counts are valid data.
- Field conduct: banks and trails only, stay off and away from redds, no handling fish or carcasses, public access points only.

## Evidence map (IWS duty → artifact)
Data-collection apps → Survey123 form + XLSForm + Field Maps · Field acquisition → real GPS survey · ETL → hosted layer → gdb + Python export · QA/QC all stages → form rules + qa_pipeline flags · Metadata → Pro metadata + metadata.json · DRR scripts → Quarto report + package · DB dev/migration → gdb domains (stretch: PostGIS) · Geospatial analysis → LiDAR gradient + spatial joins + WDFW overlays · Dashboards → public ArcGIS Dashboard · FAIR/open → CSV/GeoJSON, public repo, license · Multi-platform → Pro, AGOL, Survey123, Field Maps, Dashboards, Python, SQL · Ecology → spawner survey design, README background.

## Application language (use only once true)
**Resume entry — Whatcom Creek Salmon Monitoring Pipeline | Oct 2026**
- Built an end-to-end ecological monitoring workflow in ArcGIS: Survey123 and Field Maps data collection with validation rules, ArcGIS Pro analysis, and a public ArcGIS Dashboard
- Wrote a Python QA pipeline that flags out-of-range, missing, and duplicate records and exports an open-format data package (CSV, GeoJSON, metadata) with an auto-generated data release report
- Integrated field observations with WDFW fish passage and salmon distribution data and a LiDAR-derived stream gradient analysis

**Skills line:** add ArcGIS Pro, ArcGIS Online, Survey123, Field Maps, Dashboards, ArcGIS API for Python under Geospatial.
**Cover letter gap paragraph:** replace "open-source rather than Esri" with the field-to-dashboard Whatcom Creek build (form with validation rules, Pro analysis, public dashboard, Python QA + DRR).
**Supplementals:** hands-on, project-based ArcGIS experience, tools named, no years claimed.
**IWS application mechanics:** single PDF (cover letter + resume + 3 references with phone, email, work address) to iwsjobs@iws.org, subject "Assistant Data Analyst".

**Interview talking points:** form validation *and* post-collection QA · zero counts and absences · domains so field data matches the database · multi-observer changes (training, protocol doc, observer ID in QA, event/observation model) · open vs. proprietary (same concepts as WERAP on PostGIS/Leaflet).

## Reuse
NPS I&M → whole pipeline, Survey123 + DRR · ODFW/WDFW → field collection + fish passage · Tribal fisheries → spawner design + field apps · Forestry/fire → Field Maps + LiDAR · Municipal GIS → Pro, domains, dashboard · Data management (PSMFC/EIM) → QA, dictionary, metadata, package.

## Risks
License missing an app/API → check first; fall back to Learn ArcGIS org and document it · No fish → zero counts are valid, log habitat, add a late-Oct survey · Weather/high flow → stay on the bank, move to Sunday · Overruns → cut order · IWS fills early → accepted, the project pays off across every Esri-gated posting · Broken links → incognito test before sending.
