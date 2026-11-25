from datetime import datetime, timezone

import httpx

from src.weather_alert.alerts import build_alerts
from src.weather_alert.config import settings
from src.weather_alert.schemas import ForecastDay, HourlyForecast, WeatherReport

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


async def _json(client: httpx.AsyncClient, url: str, params: dict) -> dict:
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def fetch_weather(city: str) -> WeatherReport:
    if settings.weather_mode.lower() == "demo":
        return demo_report(city)
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        geo = await _json(client, GEOCODING_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
        results = geo.get("results") or []
        if not results:
            raise ValueError(f"No matching location found for '{city}'.")
        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        label = ", ".join(p for p in [place.get("name"), place.get("admin1"), place.get("country")] if p)
        tz = place.get("timezone") or "auto"
        forecast_data = await _json(client, FORECAST_URL, {
            "latitude": lat, "longitude": lon, "timezone": tz,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,uv_index",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset,uv_index_max",
            "hourly": "temperature_2m,weather_code,precipitation_probability",
            "forecast_days": 7,
        })
        air = None
        try:
            air_data = await _json(client, AIR_URL, {"latitude": lat, "longitude": lon, "timezone": tz,
                                                       "current": "us_aqi,european_aqi,pm2_5,pm10"})
            air = air_data.get("current")
        except (httpx.HTTPError, KeyError, ValueError):
            pass  # AQI availability varies by location/provider response.

    now = forecast_data.get("current", {})
    current = {
        "temperature_c": now.get("temperature_2m"), "feels_like_c": now.get("apparent_temperature"),
        "humidity_percent": now.get("relative_humidity_2m"), "precipitation_mm": now.get("precipitation"),
        "weather_code": now.get("weather_code"), "wind_speed_kmh": now.get("wind_speed_10m"),
        "uv_index": now.get("uv_index"),
    }
    daily = forecast_data.get("daily", {})
    sunrises = daily.get("sunrise", [])
    sunsets = daily.get("sunset", [])
    uv_maxes = daily.get("uv_index_max", [])

    days = [ForecastDay(date=daily["time"][i], weather_code=daily["weather_code"][i],
                        temperature_max_c=daily["temperature_2m_max"][i], temperature_min_c=daily["temperature_2m_min"][i],
                        precipitation_probability_max=daily["precipitation_probability_max"][i] or 0,
                        wind_speed_max_kmh=daily["wind_speed_10m_max"][i],
                        sunrise=sunrises[i] if i < len(sunrises) else None,
                        sunset=sunsets[i] if i < len(sunsets) else None,
                        uv_index_max=uv_maxes[i] if i < len(uv_maxes) else None)
            for i in range(len(daily.get("time", [])))]
    air_current = air if air else None
    day_dicts = [day.model_dump() for day in days]

    # Hourly forecast: next 12 hours from current observation time
    hourly_raw = forecast_data.get("hourly", {})
    h_times = hourly_raw.get("time", [])
    h_temps = hourly_raw.get("temperature_2m", [])
    h_codes = hourly_raw.get("weather_code", [])
    h_precips = hourly_raw.get("precipitation_probability", [])
    hourly_entries: list[HourlyForecast] = []
    if h_times:
        now_iso = now.get("time", "")
        start_idx = 0
        if now_iso:
            prefix = now_iso[:13]
            for idx, ht in enumerate(h_times):
                if ht.startswith(prefix):
                    start_idx = idx
                    break
        for i in range(start_idx, min(start_idx + 12, len(h_times))):
            hourly_entries.append(HourlyForecast(
                time=h_times[i],
                temperature_c=float(h_temps[i]) if i < len(h_temps) and h_temps[i] is not None else 0.0,
                weather_code=int(h_codes[i]) if i < len(h_codes) and h_codes[i] is not None else 0,
                precipitation_probability=int(h_precips[i]) if i < len(h_precips) and h_precips[i] is not None else None,
            ))

    return WeatherReport(location=label, latitude=lat, longitude=lon, timezone=tz,
                         observed_at=datetime.now(timezone.utc), source="Open-Meteo",
                         current=current, air_quality=air_current, forecast=days,
                         hourly=hourly_entries,
                         alerts=build_alerts(current, day_dicts, air_current))


def demo_report(city: str) -> WeatherReport:
    """Deterministic, clearly-labelled simulation for offline demos."""
    # Presets tuple format: (lat, lon, temp, humidity, wind, rain, aqi, weather_code, uv_index, sunrise, sunset)
    presets = {
        "mumbai": (19.076, 72.878, 32.4, 72, 18, 78, 126, 3, 6.2, "06:48", "18:02"),
        "delhi": (28.614, 77.209, 39.2, 31, 12, 64, 174, 3, 7.8, "06:49", "17:26"),
        "london": (51.507, -0.128, 18.1, 68, 22, 28, 42, 3, 2.4, "07:32", "16:05"),
        "new york": (40.713, -74.006, 27.0, 58, 20, 44, 58, 3, 5.1, "06:55", "16:40"),
        # Dedicated demo scenarios for thunderstorm and humidity verification
        "storm-demo": (25.761, -80.191, 26.0, 82, 45, 85, 35, 95, 3.5, "06:38", "17:35"),
        "severe-storm-demo": (29.974, -90.076, 24.0, 84, 65, 90, 40, 99, 2.1, "06:30", "17:05"),
        "humidity-demo": (1.352, 103.820, 31.0, 92, 10, 30, 45, 2, 8.4, "06:58", "19:02"),
    }
    presets["storm"] = presets["storm-demo"]
    presets["humidity"] = presets["humidity-demo"]

    key = city.strip().lower()
    entry = presets.get(key, (0.0, 0.0, 26.0, 55, 15, 25, 62, 3, 5.0, "06:30", "18:00"))
    lat, lon, temp, humidity, wind, rain, aqi = entry[:7]
    w_code = entry[7] if len(entry) > 7 else 3
    uv_val = entry[8] if len(entry) > 8 else 5.0
    sunrise_str = entry[9] if len(entry) > 9 else "06:30"
    sunset_str = entry[10] if len(entry) > 10 else "18:00"

    forecast = [ForecastDay(date=f"Day +{i+1}",
                            weather_code=w_code if i < 2 and w_code in {95, 96, 99} else (61 if rain > 50 else 2),
                            temperature_max_c=temp + (i % 3), temperature_min_c=temp - 6,
                            precipitation_probability_max=max(10, rain - i * 9), wind_speed_max_kmh=wind + i * 2,
                            sunrise=f"2026-11-2{1+i}T{sunrise_str}",
                            sunset=f"2026-11-2{1+i}T{sunset_str}",
                            uv_index_max=uv_val)
                for i in range(7)]
    current = {"temperature_c": temp, "feels_like_c": temp + 1, "humidity_percent": humidity,
               "precipitation_mm": 0.0, "weather_code": w_code, "wind_speed_kmh": wind,
               "uv_index": uv_val}
    air = {"us_aqi": aqi, "european_aqi": None, "pm2_5": None, "pm10": None}

    # Simulate realistic hourly progression for demo
    hourly_hours = ["1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"]
    hourly = [
        HourlyForecast(
            time=hourly_hours[i],
            temperature_c=round(temp + (1.5 if i < 3 else -1.0 * (i - 2)), 1),
            weather_code=w_code if i in {0, 1} else (2 if w_code != 95 else 95),
            precipitation_probability=max(5, rain - i * 8),
        )
        for i in range(len(hourly_hours))
    ]

    return WeatherReport(location=f"{city.title()} (simulated)", latitude=lat, longitude=lon,
                         timezone="simulation", observed_at=datetime.now(timezone.utc), source="Built-in simulation",
                         current=current, air_quality=air, forecast=forecast,
                         hourly=hourly,
                         alerts=build_alerts(current, [d.model_dump() for d in forecast], air))
