# Weather Data Reference

## APIs Used

| API | Docs | Endpoint |
|---|---|---|
| Forecast | [open-meteo.com/en/docs](https://open-meteo.com/en/docs) | `https://api.open-meteo.com/v1/forecast` |
| Air Quality | [open-meteo.com/en/docs/air-quality-api](https://open-meteo.com/en/docs/air-quality-api) | `https://air-quality-api.open-meteo.com/v1/air-quality` |
| Geocoding | [open-meteo.com/en/docs/geocoding-api](https://open-meteo.com/en/docs/geocoding-api) | `https://geocoding-api.open-meteo.com/v1/search` |

---

## WMO Weather Codes (Open-Meteo subset)

Open-Meteo returns only 27 of the ~100 WMO codes. The rest (dust storms, volcanic ash, etc.) are not output by forecast models.

| Code | Condition | Emoji |
|---|---|---|
| 0 | Clear sky | ☀️ |
| 1 | Mainly clear | 🌤 |
| 2 | Partly cloudy | ⛅ |
| 3 | Overcast | ☁️ |
| 45 | Fog | 🌫 |
| 48 | Depositing rime fog | 🌫 |
| 51 | Light drizzle | 🌦 |
| 53 | Moderate drizzle | 🌧 |
| 55 | Dense drizzle | 🌧 |
| 56 | Light freezing drizzle | 🌧 |
| 57 | Moderate or dense freezing drizzle | 🌧 |
| 61 | Slight rain | 🌦 |
| 63 | Moderate rain | 🌧 |
| 65 | Heavy rain | 🌧 |
| 66 | Light freezing rain | 🌧 |
| 67 | Moderate or heavy freezing rain | 🌧 |
| 71 | Slight snowfall | 🌨 |
| 73 | Moderate snowfall | 🌨 |
| 75 | Heavy snowfall | 🌨 |
| 77 | Snow grains | ❄️ |
| 80 | Slight rain showers | 🌦 |
| 81 | Moderate rain showers | 🌧 |
| 82 | Heavy rain showers | 🌧 |
| 85 | Slight snow showers | 🌨 |
| 86 | Heavy snow showers | 🌨 |
| 95 | Thunderstorm (no hail) | ⛈ |
| 96 | Thunderstorm with slight/moderate hail | ⛈🧊 |
| 99 | Thunderstorm with heavy hail | ⛈🧊 |

### Notes
- Codes 95/96/99 are differentiated by **hail**, not intensity: 95 = rain/snow storm (no hail), 96/99 = hail storm
- Codes not listed (dust, sand, ice crystals, volcanic ash) are never returned by Open-Meteo

---

## UV Index Labels

| Value | Label |
|---|---|
| 0–2 | Low |
| 3–5 | Moderate |
| 6–7 | High |
| 8–10 | Very High |
| 11+ | Extreme |

---

## Wind Speed — Beaufort Scale

| Speed (mph) | Label |
|---|---|
| 0–1 | Calm |
| 1–7 | Light |
| 8–12 | Gentle |
| 13–18 | Moderate |
| 19–24 | Fresh |
| 25–31 | Strong |
| 32–38 | Near gale |
| 39+ | Gale+ |

---

## Air Quality Index (AQI)

US EPA scale. Open-Meteo returns `us_aqi` directly — see [Air Quality API docs](https://open-meteo.com/en/docs/air-quality-api).

| AQI | Label |
|---|---|
| 0–50 | Good |
| 51–100 | Moderate |
| 101–150 | Unhealthy for sensitive groups |
| 151–200 | Unhealthy |
| 201–300 | Very unhealthy |
| 301+ | Hazardous |
