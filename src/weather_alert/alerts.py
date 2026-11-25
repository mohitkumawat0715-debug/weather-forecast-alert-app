from src.weather_alert.schemas import Alert
from src.weather_alert.config import settings

# WMO Weather Interpretation Codes for Thunderstorms (per Open-Meteo documentation)
# 95: Thunderstorm: Slight or moderate
# 96: Thunderstorm with slight hail
# 99: Thunderstorm with heavy hail
THUNDERSTORM_CODES = {95, 96, 99}
SEVERE_THUNDERSTORM_CODES = {96, 99}


def build_alerts(current: dict, forecast: list[dict], air: dict | None) -> list[Alert]:
    """Apply transparent, configurable starter thresholds; these are not official warnings."""
    alerts: list[Alert] = []

    # 1. Storm alert (Open-Meteo WMO thunderstorm interpretation codes)
    current_code = int(current["weather_code"]) if current.get("weather_code") is not None else None
    near_term_codes = [int(d.get("weather_code")) for d in forecast[:2] if d.get("weather_code") is not None]
    all_storm_codes = [c for c in ([current_code] if current_code is not None else []) + near_term_codes if c in THUNDERSTORM_CODES]

    if any(c in SEVERE_THUNDERSTORM_CODES for c in all_storm_codes):
        severe_code = max(c for c in all_storm_codes if c in SEVERE_THUNDERSTORM_CODES)
        timing = "currently observed or forecast in the next 48 hours" if current_code in SEVERE_THUNDERSTORM_CODES else "forecast in the next 48 hours"
        alerts.append(Alert(severity="critical", type="storm", value=severe_code,
                            message=f"Severe thunderstorm with hail ({timing}, WMO Code {severe_code}). Seek secure indoor shelter."))
    elif any(c == 95 for c in all_storm_codes):
        timing = "currently observed" if current_code == 95 else "forecast in the next 48 hours"
        alerts.append(Alert(severity="warning", type="storm", value=95,
                            message=f"Thunderstorm activity {timing} (WMO Code 95). Be prepared for lightning and sudden downpours."))

    # 2. Rain risk alert
    rain = max((int(d.get("precipitation_probability_max", 0)) for d in forecast[:2]), default=0)
    if rain >= 70:
        alerts.append(Alert(severity="warning", type="rain", value=rain,
                            message=f"High chance of rain in the next 48 hours ({rain}%). Carry rain protection."))
    elif rain >= 40:
        alerts.append(Alert(severity="info", type="rain", value=rain,
                            message=f"Rain is possible in the next 48 hours ({rain}%)."))

    # 3. Heat risk alert
    heat = float(current.get("temperature_c") or 0)
    if heat >= 40:
        alerts.append(Alert(severity="critical", type="heat", value=heat,
                            message=f"Very high temperature ({heat:.1f}°C). Limit strenuous outdoor activity."))
    elif heat >= 35:
        alerts.append(Alert(severity="warning", type="heat", value=heat,
                            message=f"High temperature ({heat:.1f}°C). Stay hydrated and seek shade."))

    # 4. Humidity risk alert
    humidity = float(current.get("humidity_percent") or 0)
    if humidity >= settings.humidity_high_threshold:
        alerts.append(Alert(severity="warning", type="humidity", value=humidity,
                            message=f"Very high relative humidity ({humidity:.0f}%). Expect oppressive, muggy conditions."))
    elif humidity >= settings.humidity_elevated_threshold:
        alerts.append(Alert(severity="info", type="humidity", value=humidity,
                            message=f"Elevated relative humidity ({humidity:.0f}%)."))

    # 5. Wind risk alert
    wind = float(current.get("wind_speed_kmh") or 0)
    if wind >= 60:
        alerts.append(Alert(severity="critical", type="wind", value=wind,
                            message=f"Very strong winds ({wind:.0f} km/h). Secure loose outdoor items."))
    elif wind >= 40:
        alerts.append(Alert(severity="warning", type="wind", value=wind,
                            message=f"Strong winds ({wind:.0f} km/h) may affect outdoor plans."))

    # 6. Air Quality risk alert
    if air and air.get("us_aqi") is not None:
        aqi = int(air["us_aqi"])
        if aqi >= 151:
            alerts.append(Alert(severity="critical", type="air_quality", value=aqi,
                                message=f"Unhealthy air quality (US AQI {aqi}). Reduce prolonged outdoor exertion."))
        elif aqi >= 101:
            alerts.append(Alert(severity="warning", type="air_quality", value=aqi,
                                message=f"Air may affect sensitive groups (US AQI {aqi})."))
    if not alerts:
        alerts.append(Alert(severity="info", type="status", message="No risks crossed the configured alert thresholds."))
    return alerts
