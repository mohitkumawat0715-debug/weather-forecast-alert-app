# Project Explanation: Weather Forecast & Alert Application

## Tech stack options

All three options can use a weather provider's HTTP API and JSON responses. OpenWeatherMap and WeatherAPI are alternatives to this repository's Open-Meteo integration. Review each provider's current plan, limits, and API key requirements before choosing one. Keep keys in environment variables and never commit them to GitHub.

| Option | Tools and libraries | Difficulty | Expected output |
| --- | --- | --- | --- |
| **A — Easy: command-line report** | Python, `requests`, JSON, `datetime`; one API provider such as OpenWeatherMap or WeatherAPI | Beginner | A script asks for a city, fetches current weather and a short forecast, prints a readable report, and evaluates a few basic alert conditions. This is the quickest way to learn API requests, JSON parsing, and error handling. |
| **B — Intermediate: student dashboard (recommended)** | Python, `requests` or `httpx`, JSON, `datetime`, Pandas, Matplotlib, Streamlit, one weather provider; optional email alert integration | Beginner to intermediate | A small dashboard supports several cities, displays current conditions and forecast tables, plots temperature or precipitation, and shows rule-based alerts. Optional email can send a summary when an alert is raised. |
| **C — Advanced: service-oriented application** | FastAPI, Pydantic, async `httpx`, Pandas, Plotly or Matplotlib, Streamlit or Next.js, database such as SQLite/PostgreSQL, scheduler/worker, structured logging; optional email/SMS provider | Intermediate to advanced | A separately deployable API and dashboard with normalized data models, saved locations and report history, background refresh, configurable alert thresholds, delivery tracking, and deployment/monitoring. SMS and email require external services and should be added only with consent, secrets management, and appropriate rate limits. |

### Best option for students

**Option B is the best starting target for most students.** It demonstrates the core Python skills employers can review—API integration, JSON processing, dates, tabular data, visualization, and decision rules—without requiring a database, background job system, or paid messaging service. Build the command-line flow from Option A first if these tools are new, then add the dashboard. Option C is a good extension once the core project works.

This repository currently implements an **Option C-style API plus a lightweight Streamlit dashboard**, while keeping setup and usage suitable for a student project. It uses FastAPI, Pydantic, `httpx`, and Plotly; it does not currently use Pandas for API processing or Matplotlib, and it has no email/SMS delivery. Those are optional stack choices rather than requirements. To match Option B more closely, the dashboard could use Pandas for forecast tables and Matplotlib for plots, and the backend could use synchronous `requests` instead of asynchronous `httpx`.

## Project architecture

### Inputs

- **City name(s):** Entered in the dashboard and sent to the API. The backend supports one to ten city query values per request.
- **Weather API key:** The current Open-Meteo integration does not require a key for this learning project. If the provider is changed to OpenWeatherMap or WeatherAPI, store its key in an environment variable such as `WEATHER_API_KEY`; never put a secret in dashboard code, a URL committed to Git, or a public screenshot.
- **Alert thresholds:** Rain, heat, wind, and AQI starter thresholds are defined in `src/weather_alert/alerts.py`. Humidity thresholds are configurable in `.env` through `HUMIDITY_ELEVATED_THRESHOLD` and `HUMIDITY_HIGH_THRESHOLD` (defaults 75% and 85%). They are not user inputs in the dashboard.
- **Mode/configuration:** `WEATHER_MODE` selects live provider data or built-in demo simulation.

### Processing components

1. **API request:** Streamlit sends the selected city names to FastAPI. In live mode, the backend resolves each name using geocoding and calls the forecast endpoint. It also attempts an air-quality request.
2. **JSON response parsing:** The backend parses provider JSON and maps relevant fields into Pydantic report and forecast models. Missing optional AQI is allowed.
3. **Temperature analysis:** Current temperature is checked against heat thresholds. Forecast high/low temperatures are included for display.
4. **Humidity analysis:** Current relative humidity is checked against configurable elevated (75%) and high (85%) starter thresholds and displayed.
5. **Rain/storm check:** The rules check precipitation probability and WMO thunderstorm codes in current conditions and the next two forecast days. Code 95 creates a thunderstorm warning; codes 96 and 99 create a critical hail-storm alert.
6. **Alert generation:** Matching rules create severity-labelled messages. Wind and available US AQI are also checked. If no rule matches, the API returns an informational message.
7. **Output:** FastAPI returns current weather, a seven-day forecast summary, alerts, coordinates, source, and observation time. Streamlit displays the information and offers the full report JSON in an expander.

### Text-based architecture diagram

```text
+----------------------+       HTTP request        +-------------------------+
| User / Streamlit UI  | ------------------------> | FastAPI /weather        |
| city names           |   repeated cities values  | validates 1–10 cities  |
+----------------------+                            +------------+------------+
                                                                  |
                                            +---------------------+------------------+
                                            |                                        |
                                     WEATHER_MODE=live                       WEATHER_MODE=demo
                                            |                                        |
                                +-----------v-----------+                 +----------v----------+
                                | Geocoding API         |                 | Built-in simulator  |
                                | city -> coordinates   |                 | repeatable samples  |
                                +-----------+-----------+                 +----------+----------+
                                            |                                        |
                                 +----------v-----------+                            |
                                 | Forecast API         |                            |
                                 | current + 7 days     |                            |
                                 +----------+-----------+                            |
                                            |                                        |
                                 +----------v-----------+                            |
                                 | Air-quality API      | (optional)                 |
                                 +----------+-----------+                            |
                                            +--------------------+-------------------+
                                                                 |
                                                    +------------v------------+
                                                    | Parse and normalize JSON|
                                                    | Pydantic report models  |
                                                    +------------+------------+
                                                                 |
                                                    +------------v------------+
                                                    | Analyze thresholds      |
                                                    | rain / heat / humidity  |
                                                    | wind / storm / AQI      |
                                                    +------------+------------+
                                                                 |
                                  +------------------------------v-----------------------+
                                  | FastAPI JSON response: current, forecast, alerts     |
                                  +------------------------------+-----------------------+
                                                                 |
                                                    +------------v------------+
                                                    | Streamlit metrics,      |
                                                    | charts, map, alerts     |
                                                    +------------+------------+
                                                                 |
                                                    +------------v------------+
                                                    | Inspect report JSON     |
                                                    | persistence: future work|
                                                    +-------------------------+
```

### Data flow explanation

The user chooses locations in Streamlit. The dashboard sends their names to the FastAPI endpoint. For live requests, the backend first converts each name into coordinates, then fetches current and forecast conditions and attempts the optional air-quality lookup. For demo requests, it uses deterministic sample records instead of network calls.

Next, the backend parses the JSON and normalizes the fields so that API clients receive one consistent report format. The alert function compares available measurements with the configured starter thresholds, then adds alert objects to the report. FastAPI serializes the result as JSON; Streamlit reads it to draw the current-condition cards, forecast charts, location map, and alert messages.

The current application does **not** persist a report after the request ends. The user can inspect its JSON in the dashboard, but database storage and downloadable report files are future extensions. Likewise, API keys and user-adjustable thresholds are architecture options for alternate providers or future versions, not inputs needed by the current Open-Meteo setup.

## Implementation plan: ten phases

Follow the phases in order. Each phase should leave you with something visible or verifiable before moving on.

### Phase 1: Setup

- **What to do:** Install a supported Python version, open a terminal in the project folder, create and activate a virtual environment, then install `requirements.txt`.
- **Why:** A virtual environment isolates project libraries from other Python work and makes setup reproducible.
- **Expected output:** The dependencies install into `.venv`, and `python --version` reports the interpreter you intend to use.
- **Common beginner mistakes:** Running commands from the wrong folder, forgetting to activate the environment, using a different Python executable to install packages, or committing `.venv` to Git.

### Phase 2: Project folder creation

- **What to do:** Create the `src/weather_alert/` package and files for configuration, schemas, provider integration, alert rules, API routes, and the dashboard. Keep documentation and dependency files at the project root.
- **Why:** Separating responsibilities makes the code easier to understand, debug, and extend than placing everything in one large script.
- **Expected output:** A recognizable project structure like the one in this repository, with modules that have clear roles.
- **Common beginner mistakes:** Missing package `__init__.py` files, inconsistent file names/imports, putting all logic inside the dashboard, or mixing example data into live provider responses without labeling it.

### Phase 3: API key setup

- **What to do:** Choose a provider. If using OpenWeatherMap or WeatherAPI, create an account, obtain an API key, and load it from an ignored `.env` file or environment variable. For this repository's Open-Meteo default, no key setup is required; copy `.env.example` to `.env` and set `WEATHER_MODE` instead.
- **Why:** Some providers require authentication, and environment variables keep credentials out of source code and Git history.
- **Expected output:** The app can read provider configuration without embedding secrets in Python files. For this Open-Meteo build, it can run in live or demo mode.
- **Common beginner mistakes:** Committing a real key, including the key in screenshots or error logs, confusing an API key with the base URL, or assuming every weather provider has the same authentication and free-use policy.

### Phase 4: Weather data fetching

- **What to do:** Send a request to the geocoding service, then use the returned coordinates with the current-weather and forecast endpoints. Add sensible timeouts and handle unsuccessful HTTP responses. Make AQI optional.
- **Why:** City names can be ambiguous; coordinates give the weather provider a precise location to query.
- **Expected output:** A successful request returns provider JSON for the selected location, or a useful error when lookup/network access fails.
- **Common beginner mistakes:** Sending a city name to an endpoint that expects coordinates, overlooking HTTP status errors, using no timeout, and assuming AQI is available everywhere.

### Phase 5: JSON data parsing

- **What to do:** Inspect a real provider response and map only the needed fields into stable names and types. Handle absent or null fields and validate the resulting report model.
- **Why:** The dashboard should consume a predictable format even if provider payloads contain extra fields or optional values.
- **Expected output:** A normalized report with location, observation time, current conditions, forecast entries, and optional air quality.
- **Common beginner mistakes:** Treating JSON as a Python object with attributes instead of dictionaries, assuming every key exists, confusing units, and mixing provider-specific key names throughout the UI.

### Phase 6: Forecast analysis

- **What to do:** Decide which time window and measurements matter, convert values into clearly labeled units, and compute summaries such as daily highs/lows and near-term rain probability.
- **Why:** Raw forecasts have many rows and fields; a concise summary helps users focus on conditions relevant to plans.
- **Expected output:** A readable seven-day forecast plus values that alert rules can evaluate consistently.
- **Common beginner mistakes:** Comparing values from different units, using the wrong time period, confusing precipitation amount with probability, or presenting a forecast as a guarantee.

### Phase 7: Alert condition logic

- **What to do:** Define explicit thresholds, compare the normalized values against them, and return severity plus a clear message. Keep rules in a separate function. Handle unavailable measurements without crashing.
- **Why:** Centralized rules are easier to explain, revise, and test; a clear message tells the user what condition triggered it.
- **Expected output:** One or more risk alerts for matching conditions, or an informational message when no configured threshold is crossed.
- **Common beginner mistakes:** Using arbitrary thresholds without documenting them, mixing Celsius and Fahrenheit, generating duplicate/conflicting alerts, treating missing AQI as zero, or implying educational alerts are official warnings.

### Phase 8: Visualization

- **What to do:** Build the dashboard after the API response shape is stable. Show current metrics, forecast plots, location markers, source/time labels, and alert messages with severity styling.
- **Why:** Visual summaries make trends and comparisons easier to interpret than a raw JSON payload.
- **Expected output:** A dashboard that can compare chosen cities and inspect forecast trends, while retaining a way to view the underlying data.
- **Common beginner mistakes:** Forgetting axis labels and units, plotting dates as unordered strings, hiding where data came from, making alerts hard to distinguish, or assuming an empty chart means the weather is zero.

### Phase 9: Report generation

- **What to do:** First show a complete report in the interface. Then, if useful, add a CSV/JSON download; add a database only if persistent history is required. Include location, time, source, units, forecast summary, and triggered alerts.
- **Why:** A report lets users keep or share a snapshot, while timestamps and source make it interpretable later.
- **Expected output:** In the current version, the dashboard's JSON expander shows the report. A downloadable file or stored report is a planned extension, not implemented yet.
- **Common beginner mistakes:** Calling an on-screen response “saved” when it is not persisted, omitting timestamps/timezones, overwriting previous files unexpectedly, or storing unnecessary personal data.

### Phase 10: GitHub upload

- **What to do:** Review `.gitignore`, remove secrets and local artifacts, write setup and limitations in README, capture genuine screenshots from a running app, then initialize/commit/push to a repository you own. The commands are in the README.
- **Why:** A clean repository lets reviewers reproduce the project and understand its scope without exposing credentials.
- **Expected output:** A public or course-approved repository containing source, documentation, dependency list, and optional screenshots, with no API keys or virtual environment.
- **Common beginner mistakes:** Pushing `.env`, `.venv`, or large generated files; forgetting to replace the example remote URL; uploading mock screenshots as real app output; and omitting the installation/run steps.

## What is the application?

### Simple explanation

It is an application where someone chooses one or more cities and sees the weather now and over the coming days. It can point out conditions that may affect plans, such as a high chance of rain, unusually high temperature, strong wind, or unhealthy air quality.

### Technical explanation

The application is a small data integration and decision-support system. It accepts city names, resolves them to geographic coordinates, retrieves current and forecast observations from a weather provider, normalizes provider responses into a stable internal format, evaluates configurable rules, and returns structured reports through a FastAPI service. A Streamlit client calls that service and renders metrics, charts, a location map, and alerts.

## What problem does it solve?

Weather information is often spread across maps, forecasts, and air-quality pages. People may also overlook a condition that matters to a particular plan. This project brings selected locations and a few easy-to-understand risk signals into one view. It helps users notice relevant forecast conditions sooner and make more informed plans.

It is a learning and planning aid, not an official warning service. The example thresholds are deliberately simple and should not be treated as locally validated safety guidance.

## Who can find it useful?

| User | Example use |
| --- | --- |
| Everyday users | Decide whether to carry rain gear or plan outdoor activities. |
| Businesses | Check conditions near offices, stores, worksites, or customer locations. |
| Travelers | Compare weather across destinations and travel dates. |
| Farmers | Keep an eye on forecast rain, heat, and wind when planning field work. Forecasts do not replace local agronomic advice. |
| Logistics companies | Review weather along operating areas that may affect timing or outdoor loading. A route-level system would need additional mapping and routing data. |
| Event planners | Review rain, heat, and wind forecasts before scheduling outdoor events. |

These are examples of possible use. The current project compares named locations; it does not calculate route weather or provide specialized agricultural forecasts.

## How weather APIs provide live data

### Simple explanation

The app sends a city name to a location lookup service. The service returns coordinates, such as latitude and longitude. The app uses those coordinates to ask a weather API for current conditions and forecast values. The API replies with structured data, commonly JSON, which the app displays.

### Technical explanation

In live mode, this project uses Open-Meteo's geocoding endpoint to resolve a city name. It passes the selected result's coordinates and timezone to the forecast endpoint for current observations and daily forecasts. It makes a separate request to the air-quality endpoint; because air-quality coverage can vary, failure or missing data does not prevent the weather report from being returned.

The provider response is parsed and mapped to the project's Pydantic response models. This normalization keeps the dashboard and API consumers from depending directly on every provider field name. The API returns JSON over HTTP, and FastAPI also publishes an interactive schema at `/docs`.

## How alerts are generated

### Simple explanation

After receiving the forecast, the application checks a few rules. For example, if the chance of rain is high, it shows a rain alert. If the temperature or wind speed passes a configured threshold, it shows a heat or wind alert. If AQI is present and high, it shows an air-quality alert. If no rule matches, it reports that none of the configured thresholds were reached.

### Technical explanation

The `build_alerts` function in `src/weather_alert/alerts.py` receives normalized current conditions, forecast records, and optional AQI values. It compares them with starter thresholds and weather codes, then returns typed alerts with severity, category, message, and, where useful, the measured value. Humidity thresholds are loaded from settings and can be overridden in `.env`; storm rules use Open-Meteo WMO weather codes. AQI checks run only when AQI data exists.

The current implementation has rules for rain probability, temperature, relative humidity, wind speed, thunderstorm weather codes, and US AQI. These starter thresholds are educational examples, not official, locally validated warnings; production versions should use well-defined regional criteria and communicate uncertainty.

## End-to-end workflow

```text
User enters city
       ↓
Dashboard sends city to FastAPI
       ↓
Geocoding API resolves city to coordinates (live mode)
       ↓
Weather and optional air-quality APIs return JSON
       ↓
Application validates and normalizes the data
       ↓
Forecast values are analyzed against alert rules
       ↓
FastAPI returns a structured report
       ↓
Dashboard displays metrics, charts, map, and notifications
       ↓
User can inspect the report JSON or save/export it (future extension)
```

### Workflow step by step

1. **User enters a city.** In the dashboard, the user can enter a comma-separated list of locations.
2. **Dashboard requests data.** It sends an HTTP request to the FastAPI `/weather` endpoint. FastAPI accepts repeated `cities` query parameters.
3. **Location lookup.** In live mode, the backend asks Open-Meteo Geocoding for a matching place and coordinates. In demo mode, the built-in simulator supplies deterministic sample data.
4. **Weather API fetch.** The backend uses latitude, longitude, and timezone to request current conditions and a seven-day forecast. It separately attempts to retrieve AQI and particulate matter.
5. **Data processing.** Provider fields are mapped into the application's stable response structure. Optional or unavailable air-quality data is represented as missing.
6. **Forecast analysis.** The alert rules inspect near-term rain probability and thunderstorm codes, plus current heat, humidity, wind, and AQI values.
7. **Alert condition check.** Each matching rule creates an alert with a severity and plain-language message. If nothing crosses a threshold, an informational status is returned.
8. **Display output.** FastAPI sends JSON to the dashboard, which presents the current conditions, alert messages, temperature and rain charts, and a map of the chosen locations.
9. **Save report.** The current version allows users to inspect the complete report in an on-screen JSON expander, but it does **not** persist reports to a database or download them as files. Saving history or exporting CSV/PDF is a clear future enhancement.

## Where to explore the implementation

- `src/weather_alert/weather.py` — geocoding, provider requests, normalization, and simulation.
- `src/weather_alert/alerts.py` — risk rules and thresholds.
- `src/weather_alert/api.py` — FastAPI routes and error responses.
- `src/weather_alert/schemas.py` — report and forecast response models.
- `dashboard.py` — user input and visual output.
