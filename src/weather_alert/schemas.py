from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Alert(BaseModel):
    severity: Literal["info", "warning", "critical"]
    type: str
    message: str
    value: float | None = None


class ForecastDay(BaseModel):
    date: str
    weather_code: int
    temperature_max_c: float
    temperature_min_c: float
    precipitation_probability_max: int
    wind_speed_max_kmh: float
    sunrise: str | None = None
    sunset: str | None = None
    uv_index_max: float | None = None


class HourlyForecast(BaseModel):
    time: str
    temperature_c: float
    weather_code: int
    precipitation_probability: int | None = None


class WeatherReport(BaseModel):
    location: str
    latitude: float
    longitude: float
    timezone: str
    observed_at: datetime
    source: str
    current: dict[str, float | int | str | None]
    air_quality: dict[str, float | int | str | None] | None = None
    forecast: list[ForecastDay] = Field(default_factory=list)
    hourly: list[HourlyForecast] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
