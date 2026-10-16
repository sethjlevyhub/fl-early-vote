# FL early/mail vote dashboard (prototype, local only)
- `python3 build.py` -> data.csv + site/data.js (reads /workspace/fl-earlyvote/2026/snapshots + raw/*.pdf)
- site/ is fully static (Chart.js vendored) -> GitHub Pages: push site/ to a repo, Pages from /site or gh-pages.
- Capture: /workspace/fl-earlyvote/capture.sh, looped by capture_loop.sh at 09:30/12:30/15:30/18:30 ET.
