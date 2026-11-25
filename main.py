"""ASGI entry point for the Weather Forecast & Alert API."""

from src.weather_alert.api import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
