# Whatcom Creek Salmon Monitoring Pipeline — Project Plan

**Owner:** Carver Rasmussen
**Created:** Sept 30, 2026
**Build window:** Thu Oct 1 – Mon Oct 5, 2026 (main build on the weekend of Oct 3–4)
**Driving application:** Institute for Wildlife Studies, Assistant Data Scientist (NPS Inventory & Monitoring). Closes Oct 23, reviewed in order received. **Target send: Mon Oct 5 or Tue Oct 6.**
**Working repo name:** `whatcom-creek-salmon-monitoring`

---

## 1. Why this project

Esri has been the gatekeeper on three applications: City of Gresham, ODFW, and IWS. The recurring gaps are Survey123, Field Maps, ArcGIS Online, ArcGIS Pro, and raster/LiDAR work. This project closes them with one end-to-end build that mirrors a real ecological monitoring data lifecycle:

**field collection → QA/QC → database → analysis → dashboard → documented data release**

It's built around the IWS duty list but stays general enough for NPS, WDFW, ODFW, tribal fisheries, forestry, and municipal GIS roles. The subject is a real salmon survey on Whatcom Creek in Bellingham during the fall run. That makes the story better than a tutorial, and it lines up with the fish & wildlife target.

**Honest framing to use everywhere:** "Built an end-to-end field-to-dashboard monitoring workflow in ArcGIS." Not "proficient in ArcGIS." It's project-based experience, and it helps most where Esri is preferred or one of several platforms. It won't beat a hard "2+ years of ArcGIS" knockout.

---

## 2. Coverage map: job requirements → project components

| IWS duty / qualification | Project component | Evidence artifact |
|---|---|---|
| Develop digital data-collection apps (Survey123, Field Maps) | Survey123 smart form + Field Maps habitat map | Public form link, XLSForm in repo, screenshots |
| Support field data acquisition (digital collection, GIS, GPS) | Two real creek surveys with GPS-tagged observations | Hosted feature layer, field photos |
| Processing into data systems (data entry, ETL) | Hosted layer → file geodatabase with domains; Python export pipeline | Geodatabase schema doc, ETL script |
| QA/QC at all stages of the lifecycle | Form-level validation + post-collection QA script with flags | QA report output (CSV + summary) |
| Metadata extraction and creation | ArcGIS Pro metadata records + script-generated metadata JSON | Metadata files in the data package |
| Scripts that produce data-release reports (DRRs) with data packages | Quarto report auto-generated from the QA'd data | `data_release_report.pdf/html` + data package folder |
| Database maintenance, development, migration (enterprise/cloud) | Schema design with domains; *stretch:* sync to PostgreSQL/PostGIS | Schema doc; *stretch:* migration script |
| Geospatial analysis for monitoring synthesis | Pro analysis: public layers + LiDAR DEM, reach gradients, spatial joins | Map layout PDF, analysis notebook |
| Data-visualization apps and dashboards | ArcGIS Dashboard | Public dashboard link |
| FAIR data, open formats, public repositories | CSV/GeoJSON exports, public GitHub repo, README, license | Repo |
| Proficient in multiple platforms and languages | ArcGIS Pro, AGOL, Survey123, Field Maps, Dashboards, Python, SQL | Repo + resume skills line |
| Natural resource / ecological knowledge (beneficial) | Salmon spawner survey design, habitat context | README "Background" section |
| Verbal and written communication | README, DRR, dashboard for non-technical users | All of the above |

**Deliberately out of scope:** Power BI, VBA, and Access/SQL Server. Name those honestly as gaps in the cover letter instead.

---

## 3. Scope

**In scope (must ship by Mon Oct 5)**
1. Survey123 form with validation rules (XLSForm version-controlled in GitHub)
2. At least one real field survey (two if the weekend allows)
3. Field Maps map for habitat/barrier points (can be collected on the same walk)
4. ArcGIS Pro project: file geodatabase with domains, public reference layers, one raster analysis, and one map layout
5. Python QA script plus data package export (CSV, GeoJSON, metadata)
6. Auto-generated data release report
7. ArcGIS Dashboard (public)
8. GitHub repo with README, screenshots, and links

**Stretch (only if ahead of schedule)**
- Sync the QA'd data to PostgreSQL/PostGIS. This ties it to WERAP and covers the "migration" duty directly.
- A third survey later in October to build a time series
- ModelBuilder or ArcPy geoprocessing tool for the reach summary

**Cut order if behind:** stretch items → Field Maps map → raster analysis → second survey. **Never cut:** the Survey123 form, the QA script, the data release report, or the README. Those carry the most job value.

---

## 4. Setup and data sources

**Licensing:** ArcGIS for Personal Use (~$100/yr). Non-commercial use only, and a portfolio project fits that. It avoids the 21-day trial, which requires a business or government email (don't use the WWU address). **Before buying, confirm it includes Survey123, Field Maps, Dashboards, and the ArcGIS API for Python access you need.**

**Public reference data (verify availability in Phase 0):**
- Stream flowlines: USGS NHDPlus HR or WA DNR hydrography
- Salmon distribution: WDFW SalmonScape
- Fish passage barriers: WDFW Fish Passage & Diversion Screening Inventory
- Elevation: WA DNR LiDAR Portal (bare-earth DEM for Whatcom Creek)
- Flow context: nearest USGS or City of Bellingham stream gage, if one exists for Whatcom Creek (confirm)
- Basemap: Esri imagery/topographic

---

## 5. Data model (Survey123 form)

**Survey design:** split the walkable length of Whatcom Creek into 3–4 reaches using clear landmarks. Define them in Phase 0 and store them as a polygon or line layer. Each observation is one point.

| Field | Type | Rules |
|---|---|---|
| `survey_date` | date/time | Required, defaults to now, can't be in the future |
| `observer` | text | Required, defaults to the user |
| `reach` | select_one domain (R1–R4) | Required |
| `location` | geopoint | Required, warn if accuracy > 15 m |
| `obs_type` | select_one: live fish / carcass / redd / habitat / no fish seen | Required |
| `species` | select_one: chum / coho / chinook / pink / unknown salmonid | Required if obs_type is live fish, carcass, or redd |
| `count` | integer | 0–500, required if obs_type is live fish or carcass |
| `redd_count` | integer | 0–100, shown only if obs_type = redd |
| `water_clarity` | select_one: clear / slightly turbid / turbid | Required once per survey |
| `flow` | select_one: low / normal / high | Required once per survey |
| `weather` | select_one | Optional |
| `photo` | image | Optional (encouraged) |
| `notes` | text | Optional, 250 characters max |
| `qa_flag` | hidden, filled by the QA script | Blank at entry |

**Zero counts are valid data.** Early October may be before the peak chum run, so "no fish seen" records still build the dataset. Monitoring programs record absences too, and saying so in an interview is a plus.

**Field conduct:** stay on banks and trails, don't walk on or near redds, don't handle fish or carcasses, and only use public access points.

---

## 6. Phases and time boxes (~16–20 hrs total)

### Phase 0: Setup (Thu Oct 1 evening, ~1.5 hrs)
- [ ] Buy/activate ArcGIS for Personal Use and confirm the apps are included
- [ ] Create the GitHub repo with folder structure: `/form`, `/data/raw`, `/data/release`, `/scripts`, `/report`, `/docs`, `/screenshots`
- [ ] Define reaches from imagery and save them as a layer
- [ ] Confirm public data sources and download the DEM tile(s)

### Phase 1: Survey123 form (Thu/Fri, ~2–3 hrs)
- [ ] Build the form as an XLSForm (Survey123 Connect) or in the web designer, then export the XLSForm to the repo
- [ ] Add domains, required and conditional fields, and constraints (section 5)
- [ ] Test on your phone: 5 fake records, then delete them
- [ ] Screenshot the form

### Phase 2: Field survey (Sat Oct 3 morning, ~2–3 hrs incl. travel)
- [ ] Walk the reaches and log observations in Survey123
- [ ] Log habitat/barrier points in Field Maps (culverts, woody debris, bank erosion)
- [ ] Take photos for the README
- [ ] *If possible:* a second walk on Sun morning, for two survey dates

### Phase 3: ArcGIS Pro analysis (Sat afternoon, ~3–4 hrs)
- [ ] Create a file geodatabase with domains that match the form
- [ ] Bring in the hosted observations and public layers; clip to the watershed or reaches
- [ ] **Raster:** derive slope from the LiDAR DEM and calculate mean gradient per reach (Zonal Statistics)
- [ ] Spatial join observations to reaches and summarize counts by reach and species
- [ ] Overlay fish passage barriers and SalmonScape distribution
- [ ] Fill in metadata (Pro metadata editor) for each output layer
- [ ] Export one clean map layout as a PDF

### Phase 4: QA script + data release (Sun, ~3–4 hrs)
- [ ] Python (ArcGIS API for Python) pulls the hosted feature layer
- [ ] QA checks: out-of-range counts, missing required fields, duplicate records (same point and time), GPS accuracy, dates outside the survey window, species/obs_type conflicts
- [ ] Write `qa_flag` values back or into a separate QA table, and output a QA summary CSV
- [ ] Export the data package: `observations.csv`, `observations.geojson`, `reaches.geojson`, `metadata.json`, and a data dictionary
- [ ] Auto-generate the data release report with Quarto (Python): purpose, methods, QA results, summary tables and map, data package contents, and a citation. *Option:* do the report in R/Quarto instead to mirror NPS's R-based reporting and show R. Pick one language, not both.

### Phase 5: Dashboard (Sun evening, ~2 hrs)
- [ ] ArcGIS Dashboard with a map of observations by species, counts by reach and species, observations over time, a QA status indicator (records passed/flagged), and the latest survey date
- [ ] Share publicly and test in an incognito window

### Phase 6: Package and apply (Mon Oct 5, ~1–2 hrs)
- [ ] README: background, workflow diagram, methods, links (form, dashboard, map PDF, report), how to rerun the scripts, limitations
- [ ] **Test every link in an incognito window**
- [ ] Update the IWS resume and cover letter (section 8), then send

---

## 7. Deliverables checklist (definition of done)

- [ ] Public GitHub repo with README, XLSForm, scripts, data package, report, and screenshots
- [ ] Public Survey123 form link (view only, or a copy with submissions closed)
- [ ] Public ArcGIS Dashboard link
- [ ] Map layout PDF
- [ ] Data release report (PDF/HTML)
- [ ] At least one real survey date of data, with QA results
- [ ] All links verified in incognito

---

## 8. Outcomes: application language (fill in only once it's true)

**Resume project entry (draft):**

**Whatcom Creek Salmon Monitoring Pipeline | Oct 2026**
github.com/MegaDeadCowboy/whatcom-creek-salmon-monitoring
- Built an end-to-end ecological monitoring workflow in ArcGIS: Survey123 and Field Maps data collection with validation rules, ArcGIS Pro analysis, and a public ArcGIS Dashboard
- Wrote a Python QA pipeline that flags out-of-range, missing, and duplicate records and exports an open-format data package (CSV, GeoJSON, metadata) with an auto-generated data release report
- Integrated field observations with WDFW fish passage and salmon distribution data and a LiDAR-derived stream gradient analysis

**Skills line update:** add "ArcGIS Pro, ArcGIS Online, Survey123, Field Maps, Dashboards, ArcGIS API for Python" under Geospatial.

**Cover letter swap (IWS gap paragraph):** replace the "open-source rather than Esri" framing with something like: "To close my Esri gap, I built a field-to-dashboard salmon monitoring workflow on Whatcom Creek: a Survey123 form with validation rules, ArcGIS Pro analysis, a public dashboard, and a Python script that QA-checks the data and generates a data release report."

**Supplemental question answers (NEOGOV-style):** describe the project as hands-on, project-based ArcGIS experience with specific tools named. Don't claim years.

**Interview talking points:**
- Why validation at the form level *and* post-collection QA
- How zero counts and absences are handled
- Designing domains so field data matches the database
- What you'd change for a multi-observer program (training, protocol doc, observer ID in QA)
- Open vs. proprietary: the same concepts as WERAP (PostGIS/Leaflet), different stack

---

## 9. Reuse for other applications

| Role type | Lead with |
|---|---|
| NPS I&M, ecological monitoring (IWS) | The whole pipeline, especially Survey123 and the data release report |
| State fish & wildlife (ODFW, WDFW) | Field collection + fish passage barrier analysis |
| Tribal fisheries (Lummi, NWIFC, CRITFC) | Spawner survey design + field apps |
| Forestry / fire | Field Maps + LiDAR raster work |
| Municipal GIS (Gresham-type) | Pro analysis, geodatabase domains, dashboard |
| Data management (PSMFC, EIM-type) | QA script, data dictionary, metadata, data package |

---

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Personal Use license lacks an app or API access | Check before buying. Fall back to the Learn ArcGIS org for lessons, and document the limitation |
| Few or no fish in early October | Zero counts are valid data. Log habitat points, and add a mid-to-late October survey later |
| Weather or high flow | Stay on the bank; move the survey to Sunday |
| Weekend overruns | Follow the cut order in section 3 |
| IWS fills before Monday (they review in order received) | Accepted trade-off. The project pays off across every Esri-gated posting regardless |
| Links break after publishing | Test in incognito before sending, as with the fire weather repo |

---

## 11. Open decisions

- [ ] Report language: Python or R (Quarto either way)
- [ ] One survey date or two
- [ ] Attempt the PostGIS sync stretch or not
- [ ] Final reach boundaries
