import asyncio
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx

from .models import Location, CurrentForecast, HourlyForecast, HourlyRow, WeekForecast, DailyRow

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

CURRENT_FIELDS = ",".join([
    "is_day",
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "uv_index",
    "weather_code",
    "cloud_cover",
    "visibility",
])

HOURLY_FIELDS = ",".join([
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation_probability",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "uv_index",
    "weather_code",
    "cloud_cover",
    "visibility",
])

DAILY_FIELDS = ",".join([
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_probability_max",
    "precipitation_sum",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant",
    "wind_gusts_10m_max",
    "uv_index_max",
    "sunrise",
    "sunset",
])


async def geocode(city: str) -> list[Location]:
    async with httpx.AsyncClient() as client:
        r = await client.get(GEOCODING_URL, params={
            "name": city,
            "count": 5,
            "language": "en",
            "format": "json",
        })
        r.raise_for_status()
        results = r.json().get("results", [])
        return [Location(
            id=result["id"],
            city_name=result["name"],
            state=result.get("admin1", ""),
            country=result.get("country_code", ""),
            lat=result["latitude"],
            lon=result["longitude"],
            timezone=result["timezone"],
        ) for result in results]


async def get_now(loc: Location) -> CurrentForecast:
    async with httpx.AsyncClient() as client:
        weather, aqi = await asyncio.gather(
            client.get(FORECAST_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "current": CURRENT_FIELDS,
                "temperature_unit": "celsius",
                "wind_speed_unit": "mph",
                "timezone": loc.timezone,
            }),
            client.get(AIR_QUALITY_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "hourly": "us_aqi",
                "timezone": loc.timezone,
                "forecast_days": 1,
            }),
        )
        weather.raise_for_status()
        aqi.raise_for_status()

    return _parse_now(weather.json(), aqi.json()["hourly"], loc.timezone)


async def get_hourly(loc: Location, target_date: date) -> HourlyForecast:
    today_loc = datetime.now(ZoneInfo(loc.timezone)).date()
    days_ahead = (target_date - today_loc).days + 1

    async with httpx.AsyncClient() as client:
        weather, aqi = await asyncio.gather(
            client.get(FORECAST_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "hourly": HOURLY_FIELDS,
                "daily": "sunrise,sunset",
                "temperature_unit": "celsius",
                "wind_speed_unit": "mph",
                "timezone": loc.timezone,
                "forecast_days": days_ahead,
            }),
            client.get(AIR_QUALITY_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "hourly": "us_aqi",
                "timezone": loc.timezone,
                "forecast_days": min(days_ahead, 7),  # AQI API caps at 7 days
            }),
        )
        weather.raise_for_status()
        aqi.raise_for_status()
        aqi_hourly = aqi.json()["hourly"]
    return _parse_hourly(weather.json(), aqi_hourly, target_date)


async def get_week(loc: Location) -> WeekForecast:
    async with httpx.AsyncClient() as client:
        weather, aqi = await asyncio.gather(
            client.get(FORECAST_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "daily": DAILY_FIELDS,
                "temperature_unit": "celsius",
                "wind_speed_unit": "mph",
                "timezone": loc.timezone,
                "forecast_days": 7,
            }),
            client.get(AIR_QUALITY_URL, params={
                "latitude": loc.lat,
                "longitude": loc.lon,
                "hourly": "us_aqi",
                "timezone": loc.timezone,
                "forecast_days": 7,
            }),
        )
        weather.raise_for_status()
        aqi.raise_for_status()

    return _parse_week(weather.json(), aqi.json()["hourly"])


# --- Parsers ---

def _parse_time(dt_str):
    return datetime.fromisoformat(dt_str).time()


def _make_hourly_row(hourly, aqi_by_time, i):
    ts = hourly["time"][i]
    return HourlyRow(
        temp=hourly["temperature_2m"][i],
        feels=hourly["apparent_temperature"][i],
        humidity=hourly["relative_humidity_2m"][i],
        wmo_code=hourly["weather_code"][i],
        cloud=hourly["cloud_cover"][i],
        visibility=hourly["visibility"][i],
        rain_prob=hourly["precipitation_probability"][i],
        rain_mm=hourly["precipitation"][i],
        wind=hourly["wind_speed_10m"][i],
        wind_direction=hourly["wind_direction_10m"][i],
        gusts=hourly["wind_gusts_10m"][i],
        uv=hourly["uv_index"][i],
        aqi=aqi_by_time.get(ts),
    )


def _parse_now(data, aqi_hourly, timezone) -> CurrentForecast:
    current = data["current"]
    dt = datetime.fromisoformat(current["time"]).replace(tzinfo=ZoneInfo(timezone))
    now_hour = dt.strftime("%Y-%m-%dT%H:00")
    aqi_by_time = dict(zip(aqi_hourly["time"], aqi_hourly["us_aqi"]))
    return CurrentForecast(
        dt=dt,
        is_day=bool(current["is_day"]),
        temp=current["temperature_2m"],
        feels=current["apparent_temperature"],
        humidity=current["relative_humidity_2m"],
        wmo_code=current["weather_code"],
        cloud=current["cloud_cover"],
        visibility=current["visibility"],
        rain_mm=current["precipitation"],
        wind=current["wind_speed_10m"],
        wind_direction=current["wind_direction_10m"],
        gusts=current["wind_gusts_10m"],
        uv=current["uv_index"],
        aqi=aqi_by_time.get(now_hour),
    )


def _parse_hourly(data, aqi_hourly, target_date):
    hourly = data["hourly"]
    daily = data["daily"]
    date_str = target_date.isoformat()
    day_idx = daily["time"].index(date_str)
    aqi_by_time = dict(zip(aqi_hourly["time"], aqi_hourly["us_aqi"]))
    rows = {}
    for i, ts in enumerate(hourly["time"]):
        if not ts.startswith(date_str):
            continue
        rows[datetime.fromisoformat(ts)] = _make_hourly_row(hourly, aqi_by_time, i)
    return HourlyForecast(
        date=target_date,
        sunrise=_parse_time(daily["sunrise"][day_idx]),
        sunset=_parse_time(daily["sunset"][day_idx]),
        rows=rows,
    )


def _parse_week(data, aqi_hourly):
    daily = data["daily"]
    aqi_by_time = dict(zip(aqi_hourly["time"], aqi_hourly["us_aqi"]))

    # aggregate hourly AQI to daily max
    daily_aqi = {}
    for ts, aqi in aqi_by_time.items():
        if aqi is None:
            continue
        d = ts[:10]
        if d not in daily_aqi or aqi > daily_aqi[d]:
            daily_aqi[d] = aqi

    rows = {}
    for i, date_str in enumerate(daily["time"]):
        rows[date.fromisoformat(date_str)] = DailyRow(
            wmo_code=daily["weather_code"][i],
            temp_high=daily["temperature_2m_max"][i],
            temp_low=daily["temperature_2m_min"][i],
            feels_high=daily["apparent_temperature_max"][i],
            feels_low=daily["apparent_temperature_min"][i],
            rain_prob=daily["precipitation_probability_max"][i],
            rain_mm=daily["precipitation_sum"][i],
            wind=daily["wind_speed_10m_max"][i],
            wind_direction=daily["wind_direction_10m_dominant"][i],
            wind_gusts=daily["wind_gusts_10m_max"][i],
            uv=daily["uv_index_max"][i],
            aqi=daily_aqi.get(date_str),
            sunrise=_parse_time(daily["sunrise"][i]),
            sunset=_parse_time(daily["sunset"][i]),
        )
    return WeekForecast(rows=rows)
