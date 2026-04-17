from dataclasses import dataclass
from datetime import date, time


@dataclass
class Location:
    id: int
    city_name: str
    state: str
    country: str
    lat: float      # degrees
    lon: float      # degrees
    timezone: str = "America/Los_Angeles"


@dataclass
class HourlyRow:
    temp: float             # °C
    feels: float            # °C
    humidity: int           # %
    wmo_code: int
    cloud: int              # %
    visibility: float       # metres
    rain_prob: int          # %
    rain_mm: float          # mm
    wind: float             # mph
    wind_direction: float   # degrees
    gusts: float            # mph
    uv: float               # index
    aqi: int | None         # US AQI


@dataclass
class HourlyForecast:
    date: date
    sunrise: time
    sunset: time
    rows: dict          # datetime → HourlyRow


@dataclass
class DailyRow:
    wmo_code: int
    temp_high: float        # °C
    temp_low: float         # °C
    feels_high: float       # °C
    feels_low: float        # °C
    rain_prob: int          # %
    rain_mm: float          # mm
    wind: float             # mph
    wind_direction: float   # degrees
    wind_gusts: float       # mph
    uv: float               # index
    aqi: int | None         # US AQI
    sunrise: time
    sunset: time


@dataclass
class WeekForecast:
    rows: dict          # date → DailyRow
