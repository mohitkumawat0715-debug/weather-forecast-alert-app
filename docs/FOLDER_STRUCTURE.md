# GitHub-ready folder structure

```text
Weather-Forecast-Alert-Application/
├── data/                  # Small sample inputs; no live data is stored here
├── src/weather_alert/     # FastAPI backend, API integration, models, and alert rules
├── outputs/               # Generated exports (planned; not written by current app)
├── images/                # Genuine screenshots and diagrams
├── reports/               # Report examples and project notes
├── docs/                  # Architecture and project documentation
├── dashboard.py           # Streamlit dashboard
├── main.py                # Exposes the FastAPI app for Uvicorn
├── README.md              # Project overview and run instructions
├── requirements.txt       # Python dependencies
├── .env.example            # Safe configuration template
└── .gitignore              # Excludes secrets, virtualenvs, and generated files
```

## Folder explanations

- **`data/`** — Use for small sample inputs, such as a curated CSV used in a demonstration. The current app fetches live weather or generates simulation values in code; it does not store provider data here.
- **`src/`** — Holds the Python source package. `src/weather_alert/` contains the FastAPI routes, Open-Meteo integration, Pydantic schemas, configuration, and alert rules.
- **`outputs/`** — Destination for generated downloads such as CSV or JSON reports if export is implemented. The current application does not write files here.
- **`images/`** — Genuine screenshots and diagrams linked from GitHub documentation. Screenshots should be captured from the running app.
- **`reports/`** — Space for report examples or analysis deliverables. Current project documentation is primarily under `docs/`; persistent forecast reports are not implemented.
- **`docs/`** — Longer explanations such as the architecture and project guide in `PROJECT_EXPLANATION.md`.

## Screenshot Instructions

- Save genuine screenshots and architectural diagrams directly inside the `images/` directory (e.g., `images/dashboard.png`, `images/api_docs.png`).
- Reference all screenshots in documentation and markdown files pointing to the `images/` folder path:
  ```markdown
  ![Dashboard overview](images/dashboard.png)
  ![API interactive docs](images/api_docs.png)
  ```
- **Important**: Do not add placeholder or fabricated mockups. All visual assets must be genuine captures taken from the running application (either in live mode or offline demo mode via `WEATHER_MODE=demo`).

## Root-level files

- **`README.md`** — Short project landing page with features, setup, API examples, and contribution or portfolio information.
- **`requirements.txt`** — Packages required to run the API and dashboard.
- **`.env.example`** — Safe names and defaults for local settings. Copy it to `.env`; never commit real credentials.
- **`.gitignore`** — Prevents local-only files such as `.env`, `.venv/`, and caches from being tracked.
- **`main.py`** — Imports and exposes the FastAPI application for `uvicorn main:app --reload`.
- **`dashboard.py`** — Starts the separate Streamlit user interface.
