from fastapi import FastAPI, HTTPException, Query
from httpx import HTTPError

from src.weather_alert.config import settings
from src.weather_alert.schemas import WeatherReport
from src.weather_alert.weather import fetch_weather

app = FastAPI(title="Weather Forecast & Alert API", version="1.0.0",
              description="Current conditions, seven-day forecast and configurable risk alerts.")


@app.get("/health")
async def health():
    return {"status": "ok", "mode": settings.weather_mode}


@app.get("/weather", response_model=list[WeatherReport])
async def weather(cities: list[str] = Query(..., description="Repeat the parameter, e.g. ?cities=Delhi&cities=Mumbai")):
    if not 1 <= len(cities) <= 10:
        raise HTTPException(status_code=400, detail="Choose between 1 and 10 cities.")
    reports = []
    for city in cities:
        try:
            reports.append(await fetch_weather(city))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Weather provider request failed for '{city}'.") from exc
    return reports
