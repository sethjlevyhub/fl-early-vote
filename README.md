# FL early/mail vote dashboard (prototype, local only)
- `python3 build.py` -> data.csv + site/data.js (reads /workspace/fl-earlyvote/2026/snapshots + raw/*.pdf)
- site/ is fully static (Chart.js vendored) -> GitHub Pages: push site/ to a repo, Pages from /site or gh-pages.
- Capture: /workspace/fl-earlyvote/capture.sh, looped by capture_loop.sh at 09:30/12:30/15:30/18:30 ET.

## Multi-state (Ohio added 2026-10-16)
- site/index.html = Florida (unchanged except a Florida/Ohio nav pill). site/ohio.html = Ohio page.
- `python3 build_ohio.py` -> site/ohio-data.csv + site/ohio-data.js from ohio_sources.csv (hand-curated, URL per row).
- Ohio capture: /workspace/oh-earlyvote/capture_ohio.sh (called at end of fl capture.sh). SOS currently 403s the box.
- County files (2026-10-16): /workspace/oh-earlyvote/county/capture_county.py (Cuyahoga, Franklin, Butler; `--hist` = Cuyahoga 2018/2022/2024 once), called from fl capture.sh 4x/day; dedup by md5, gzipped.
- `python3 build_ohio_county.py` -> site/ohio-county-data.csv/.js (partial 3-county aggregate, party by last primary; Cuyahoga past cycles).
- NC (2026-10-16): site/nc.html + nc-data.js/csv via `python3 build_nc.py` (reads /workspace/nc-earlyvote/agg/*.csv made by aggregate_nc.py). Capture: /workspace/nc-earlyvote/capture_nc.sh (called from fl capture.sh), saves each new S3 Last-Modified version and re-aggregates 2026.
