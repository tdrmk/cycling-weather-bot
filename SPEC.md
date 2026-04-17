# Cycling Weather Bot — Spec

## Location Management

### Storage
Locations are stored per-user. Each location is resolved to coordinates at add time — no repeated geocoding on every weather request.

---

### /add [city]

Resolves city via Open-Meteo Geocoding API. Also available as `/addlocation`.

**No argument → prompt**
```
User: /add
Bot:  Which city?
User: Sunnyvale
Bot:  Added Sunnyvale ✅
```

**Single result → add immediately**
```
User: /add Sunnyvale
Bot:  Added Sunnyvale ✅
```

**Multiple results → show inline buttons, one per row**
```
User: /add Springfield
Bot:  Found multiple matches, pick one:
      [Springfield, IL, US]
      [Springfield, MO, US]
      [Springfield, OH, US]
User: taps Springfield, IL, US
Bot:  Added Springfield ✅
```

**No results**
```
User: /add Xyzabc
Bot:  No locations found for "Xyzabc". Try a different name.
```

**Already added**
```
User: /add Sunnyvale
Bot:  Sunnyvale is already in your locations.
```

---

### /remove

Shows saved locations as inline buttons, one per row. Also available as `/removelocation`.

**Normal flow**
```
User: /remove
Bot:  Which location to remove?
      [Sunnyvale]
      [Santa Clara]
User: taps Santa Clara
Bot:  Removed Santa Clara ✅
```

**No locations set**
```
Bot:  You have no locations set. Add one with /add <city>
```

---

### /locations

Lists saved locations as plain text.

**Has locations**
```
Bot:  Your locations:
      • Sunnyvale
      • Mountain View
```

**No locations**
```
Bot:  You have no locations set. Add one with /add <city>
```

---

### /start

Logs user details to terminal (name, username, user ID).

**First time / no locations**
```
Bot:  Welcome! Add your first location with /add <city>
```

**Has locations**
```
Bot:  Welcome back! Use /now, /today, /forecast, /week, or /cycle to get started.
```

---

## Weather Commands

All weather commands accept an optional city name argument. If provided, shows only that saved location. If omitted, shows the first saved location.

```
/now              → first saved location
/now Sunnyvale    → Sunnyvale (must be in saved locations)
```

**No locations set (all weather commands)**
```
Bot:  No locations set. Add one with /add <city>
```

**City not found in saved locations**
```
Bot:  "Sunnyvale" not in your locations. Use /locations to see what's saved.
```

---

### /now [city] — Current conditions

```
📍 Sunnyvale, CA
🌤 Mainly clear (12% clouds)
🌡 18°C  (feels 16°C)
💧 Humidity 65%
☀️ UV 3 (Moderate)
🌧 Rain 10% / 0mm
💨 8mph NW Light (gusts 12mph)
👁 14km
😷 AQI 42 (Good)
```

---

### /today [city] — Today's hourly forecast

Current hour until midnight.

```
📍 Sunnyvale, CA
Today (Mon Apr 14)
🌅 6:32AM   🌇 7:54PM

      °C    %/mm mph UV
12PM 18/14 🌤 10/0  8  3
 2PM 19/15 🌤  5/0  9  4
 4PM 18/14 ⛅  5/0  7  3
 5PM 17/13 ☁️ 20/0  6  2
 6PM 16/12 🌧 70/1  8  1

[Show extended ▼]
```

Tapping [Show extended ▼] edits the message in place to show the extended view and swaps the button to [Show compact ▲]. Tapping again collapses back.

---

### /today extended view

Same hours as compact, each hour as its own block with full detail.

```
📍 Sunnyvale, CA
Today (Mon Apr 14)
🌅 6:32AM   🌇 7:54PM

*2PM*
🌡 18°C (feels 14°C)  💧 65%
🌤 Mainly clear (12% clouds)  👁 16km
🌧 Rain 10% / 0mm
💨 8mph NW Light (gusts 12mph)
☀️ UV 3 (Moderate)
😷 AQI 42 (Good)

*3PM*
🌡 19°C (feels 15°C)  💧 62%
🌤 Mainly clear (8% clouds)  👁 18km
🌧 Rain 5% / 0mm
💨 9mph NW Light (gusts 14mph)
☀️ UV 4 (Moderate)
😷 AQI 44 (Good)

[Show compact ▲]
```

---

### /forecast [city] [day] — Hourly forecast

No argument defaults to tomorrow. Optionally accepts a city name and/or a day name (in either order).

```
/forecast           → tomorrow, first saved location
/forecast friday    → the coming Friday (always strictly future — if today is Friday, means next week)
/forecast next friday → the Friday after the coming one
/forecast Sunnyvale friday → Sunnyvale, coming Friday
```

Up to 16 days ahead supported (Open-Meteo limit).

Same format as `/today` (compact table + [Show extended ▼] toggle), full 24 hours (midnight to midnight).

The scheduled 8 PM daily send uses compact format with the [Show extended ▼] button.

---

### /week [city] — 7-day daily summary

7 days starting today.

```
📍 Sunnyvale, CA
Apr 14–20
🌅 6:32AM   🌇 7:54PM

             °C %/mm mph UV
Mon 14 🌤 22/12 10/ 5  8  6
Tue 15 🌧 18/11 80/12 12  2
Wed 16 ☁️ 17/10 80/ 5 15  2
Thu 17 ☁️ 18/11 30/ 1 12  3
Fri 18 🌤 21/12  5/ 0  9  6
Sat 19 ☀️ 23/13  0/ 0  7  7
Sun 20 🌤 22/12  5/ 0  8  6

[Show extended ▼]
```

Tapping [Show extended ▼] edits the message in place to show the extended view and swaps the button to [Show compact ▲]. Tapping again collapses back.

---

### /week extended view

Each day as its own block with full detail.

```
📍 Sunnyvale, CA
Apr 14–20

*Mon Apr 14*
🌤 Mainly clear
🌡 22°C / 12°C (feels 20°C / 10°C)
🌧 Rain 10% / 5mm
💨 8mph NW (gusts 14mph)
☀️ UV 6 (High)
😷 AQI 42 (Good)
🌅 6:32AM   🌇 7:54PM

*Tue Apr 15*
🌧 Rain
🌡 18°C / 11°C (feels 16°C / 9°C)
🌧 Rain 80% / 12mm
💨 12mph SW (gusts 20mph)
☀️ UV 2 (Low)
😷 AQI 55 (Moderate)
🌅 6:31AM   🌇 7:55PM

[Show compact ▲]
```

---

### /cycle [city] [day] [morning|noon|evening|night] — Cycling conditions

Cycling-specific hourly breakdown for a time period. Each hour shows a verdict and the fields that matter for riding.

- `morning` → 8AM–12PM
- `noon` → 12PM–4PM
- `evening` → 4PM–8PM
- `night` → 8PM–12AM

No period arg defaults to the current period (morning before noon, noon before 4PM, etc.; midnight–7AM defaults to morning). No day arg defaults to today. No city arg defaults to first saved location. Args can be given in any order.

```
/cycle                      → current period, today, first location
/cycle evening              → evening, today, first location
/cycle friday morning       → morning, coming Friday, first location
/cycle Sunnyvale evening    → evening, today, Sunnyvale
/cycle next saturday noon   → noon, Saturday after next
```

---

#### Format

Date line has three variants:
- `Today (Wed Apr 16)` — when target date is today
- `Tomorrow (Thu Apr 17)` — when target date is tomorrow
- `Fri Apr 18` — all other dates (no prefix)

```
📍 Sunnyvale, CA
Today (Wed Apr 16)
Morning (8AM–12PM)

8AM — 🚴 Good
🌤 Mainly clear
🌡 16°C / feels 14°C
💨 8mph NW — Light
☔ 5% / 0mm
☀️ UV 3 — Moderate — sunscreen recommended
😷 AQI 35 — Good

9AM — 🚴 Good
🌤 Mainly clear
🌡 17°C / feels 15°C
💨 9mph NW — Light
☔ 5% / 0mm
☀️ UV 4 — Moderate — sunscreen recommended
😷 AQI 36 — Good

10AM — 🚴 Manageable — wind
⛅ Partly cloudy
🌡 18°C / feels 16°C
💨 18mph SW — Moderate
☔ 15% / 0mm
☀️ UV 5 — Moderate — sunscreen recommended
😷 AQI 38 — Good

11AM — 🚴 Tough — wind + rain
🌧 Moderate rain
🌡 19°C / feels 15°C
💨 26mph SW — Strong — gusty, expect sideways push (gusts 38mph)
☔ 40% / 3mm — bring a jacket
☀️ UV 4 — Moderate — sunscreen recommended
😷 AQI 40 — Good
```

#### Line-by-line breakdown

| Line | Format | Notes |
|---|---|---|
| Header | `8AM — 🚴 Good` | Verdict + optional reason |
| Condition | `🌤 Mainly clear` | WMO emoji + label; no cloud% |
| Temp | `🌡 19°C / feels 15°C` | Slash separator, no parentheses |
| Wind | `💨 18mph SW — Moderate` | speed + 8-dir cardinal + Beaufort label; append gusts when gust > sustained + 10mph |
| Rain | `☔ 5% / 0mm` | Uses ☔ (not 🌧) to avoid clash with rain WMO codes |
| UV | `☀️ UV 5 — Moderate — sunscreen recommended` | Only shown when UV ≥ 3; commentary added when Moderate+ |
| Visibility | `👁 2km — Mist — use lights` | Only shown when visibility < 5km |
| AQI | `😷 AQI 35 — Good` | Standard AQI label; skipped if unavailable |

**Key design choice:** Rain probability/amount uses `☔` to clearly distinguish from condition lines that use the WMO rain emoji (`🌧 Moderate rain`). Without this, `11AM` would show `🌧 Moderate rain` and `🌧 40% / 3mm` back-to-back — same emoji, visually confusing.

---

#### Verdict System

Four levels: **Good**, **Manageable**, **Tough**, **Don't ride**

Evaluated per hour. Checked top-down — first matching level wins.

**Rain hierarchy**

Rain uses three signals that can contradict each other. Priority order:

1. **`rain_mm`** — primary. Actual accumulated water on road. Drives the verdict.
2. **`rain_prob`** — secondary. Only elevates verdict when mm is also present or prob is very high (genuine uncertainty, not a trace).
3. **WMO rain codes** — display only. Not used in verdict (they reflect current conditions, not accumulation, and often show "rain" at 0mm). Exception: snow codes stay in verdict because surface danger applies regardless of mm.

**⛔ Don't ride (any of)**
- WMO code in {56, 57, 66, 67} (freezing drizzle, freezing rain — ice on road surface)
- WMO code in {95, 96, 99} (thunderstorm, thunderstorm + hail)
- AQI >= 201 (Very unhealthy or worse)
- Feels like < 2°C (ice risk)
- Feels like > 35°C (heat danger)
- Wind >= 35mph (near gale, bike control becomes unsafe)
- Wind gusts >= 40mph (sudden force can push rider sideways)
- Rain amount >= 10mm (roads flooded/slippery, braking unreliable)
- Visibility < 1km (dense fog, stopping distance for cars exceeds visibility)

**🚴 Tough (any of, if not Don't ride)**
- Wind 20–34mph
- Wind gusts 30–39mph
- Rain amount 3–9mm
- Rain prob >= 75% AND rain mm >= 1 (high-confidence rain incoming)
- AQI 151–200
- WMO code in {75, 77} (heavy snow, snow grains — road surface danger)
- Feels like 2–7°C (very cold)
- Feels like 30–35°C (heat risk)
- Visibility 1–2km (fog, risky on roads with traffic)

**🚴 Manageable (any of, if not already Tough)**
- Wind 13–19mph
- Wind gusts 20–29mph
- Rain amount 1–2mm
- Rain prob >= 60% (likely rain but amount uncertain)
- AQI 101–150
- WMO code in {71, 73} (light/moderate snow)
- Feels like 7–10°C (cold)
- Feels like 25–30°C (warm)
- Visibility 2–5km (mist/haze, use lights)

**🚴 Good**
- Everything else (feels like 10–25°C, low wind, low rain, good air)

---

#### Night Riding Downgrade

Applied **after** the base verdict is computed. An hour is considered dark if the datetime is after sunset or before sunrise.

**Trigger:** dark AND (`rain_mm > 0` OR `visibility < 5000m`)

Rain at night means wet roads + car headlights in your eyes. Poor visibility at night compounds the usual risk.

| Base verdict | After downgrade | Reason appended |
|---|---|---|
| Good | 🚴 Manageable | `low light` |
| Manageable | 🚴 Tough | `+ low light` |
| Tough | no change | (already serious) |
| Don't ride | no change | — |

If dark but dry with good visibility: no downgrade. Night riding with no rain and clear skies is fine with lights.

**Example:**
```
9PM — 🚴 Tough — rain + low light
🌧 Light rain
🌡 17°C / feels 15°C
💨 10mph NW — Gentle
☔ 55% / 1mm — light jacket recommended
👁 3km — Mist — use lights
```

---

#### Verdict Header Commentary

When a condition is notable, append a short reason to the verdict line:

```
8AM — 🚴 Good
10AM — 🚴 Manageable — wind
11AM — 🚴 Tough — wind + rain
12PM — ⛔ Don't ride — thunderstorm
 2PM — ⛔ Don't ride — AQI hazardous
```

**Reason vocabulary:**
| Trigger | Reason token |
|---|---|
| Thunderstorm WMO | `thunderstorm` |
| Freezing drizzle/rain WMO | `ice on road` |
| AQI >= 201 | `AQI hazardous` |
| Feels like < 2°C | `too cold` |
| Feels like > 35°C | `too hot` |
| Wind >= 35mph | `wind too strong` |
| Wind gusts >= 40mph | `gusts dangerous` |
| Rain mm >= 10mm | `too much rain` |
| Visibility < 1km | `dangerous fog` |
| Wind 20–34mph | `strong wind` |
| Wind gusts 30–39mph | `strong gusts` |
| Rain mm 3–9mm | `heavy rain` |
| Rain prob >= 75% + mm >= 1 | `rain` |
| AQI 151–200 | `AQI unhealthy` |
| WMO heavy snow | `heavy snow` |
| Feels like 2–7°C | `very cold` |
| Feels like 30–35°C | `heat risk` |
| Visibility 1–2km | `fog` |
| Wind 13–19mph | `wind` |
| Wind gusts 20–29mph | `gusty` |
| Rain mm 1–2mm | `rain` |
| Rain prob >= 60% | `rain likely` |
| AQI 101–150 | `poor air` |
| WMO light/moderate snow | `snow` |
| Feels like 7–10°C | `cold` |
| Feels like 25–30°C | `warm` |
| Visibility 2–5km | `low visibility` |
| Night downgrade | `low light` |

For Good: no reason appended. For Manageable/Tough/Don't ride: append the primary trigger. For Tough with two triggers, join with ` + ` (cap at two, e.g. `wind + rain`).

---

#### Rain Field Commentary

Append a short note after `☔ 40% / 3mm` when notable:

| Condition | Appended note |
|---|---|
| mm >= 5 AND prob >= 60% | `— bring a jacket` |
| prob >= 60% AND mm < 2 | `— possible light shower` |
| mm >= 2 OR prob >= 40% | `— light jacket recommended` |
| Everything else | *(no note)* |

---

#### Temperature Field

Always shown. Uses feels like for commentary since that's what you experience on the bike.

`🌡 19°C / feels 15°C`

| Feels like | Commentary |
|---|---|
| < 2°C | `— too cold, don't ride` |
| 2–7°C | `— very cold, full winter kit` |
| 7–10°C | `— cold, layer up` |
| 10–25°C | *(no note)* |
| 25–30°C | `— warm, stay hydrated` |
| 30–35°C | `— hot, shorten your ride` |
| > 35°C | `— too hot, don't ride` |

---

#### Wind Field

`💨 18mph SW — Moderate`

Format: speed + 8-dir cardinal + Beaufort label

| Speed | Beaufort label |
|---|---|
| 0–1mph | Calm |
| 1–7mph | Light |
| 8–12mph | Gentle |
| 13–18mph | Moderate |
| 19–24mph | Fresh |
| 25–31mph | Strong |
| 32–38mph | Near gale |
| 39+mph | Gale |

No headwind/tailwind commentary (rider's route direction is unknown).

When gusts are notably higher than sustained (gust > sustained + 10mph), append:

`💨 18mph SW — Moderate — gusty, expect sideways push (gusts 32mph)`

---

#### Visibility Field

Show only when visibility < 5km. Skip the line entirely when visibility >= 5km.

| Visibility | Output |
|---|---|
| >= 5km | *(line omitted)* |
| 2–5km | `👁 3km — Mist — use lights` |
| 1–2km | `👁 1.5km — Fog — stay off busy roads` |
| < 1km | `👁 0.5km — Dense fog — don't ride` |

---

#### UV Field

Skip the line entirely when UV < 3 — common at night and early morning.

| UV | Output |
|---|---|
| < 3 | *(line omitted)* |
| 3–5 | `☀️ UV 4 — Moderate — sunscreen recommended` |
| 6–7 | `☀️ UV 6 — High — sunscreen essential` |
| 8–10 | `☀️ UV 9 — Very High — full protection, cover up` |
| 11+ | `☀️ UV 11 — Extreme — reapply mid-ride` |

UV does not affect the verdict — informational only.

---

#### AQI Field

Show only when AQI is available. Skip the field entirely if unavailable.

`😷 AQI 42 — Good`

---

#### Arg Parsing

Tokens are lowercased and checked in three passes:

1. **Period** — pull out the first token that matches exactly one of `morning`, `noon`, `evening`, `night`
2. **Day** — pull out day keyword(s):
   - `today` → today's date
   - `tomorrow` → tomorrow
   - `monday` … `sunday` → next occurrence of that weekday (strictly future; if today matches, means next week)
   - `next monday` … → the occurrence after the coming one
3. **City** — remaining tokens joined, matched case-insensitively against saved location names

Unrecognized tokens (not period, not day, not a saved city) → reply with an error:
```
Unknown argument "foo". Usage: /cycle [city] [day] [morning|noon|evening|night]
```

If the requested period has already passed for today, the bot suggests the next available period:
```
That period has already passed. Try /cycle noon or /cycle evening.
```

---

## Appendix

### Data Sources

- Weather: Open-Meteo Forecast API (hourly + daily)
- Air quality: Open-Meteo Air Quality API (`us_aqi`)
- Geocoding: Open-Meteo Geocoding API

### /now — Fields

- Condition: WMO weather code → emoji + label + cloud cover %; night emoji (🌙/☁️) before sunrise and after sunset for clear/mainly clear/partly cloudy codes
- Temperature: `temperature_2m` + `apparent_temperature` (feels like); both formatted as integers
- Humidity: `relative_humidity_2m`
- UV: `uv_index` + label (Low / Moderate / High / Very High / Extreme)
- Rain: `precipitation_probability` % + `precipitation` mm (integer, no decimal)
- Wind: `wind_speed_10m` mph (integer) + 8-direction cardinal (N/NE/E/SE/S/SW/W/NW) + Beaufort label + `wind_gusts_10m` mph in parentheses
- Visibility: `visibility` m → km (integer); always shown
- AQI: `us_aqi` + label (Good / Moderate / Unhealthy for sensitive groups / Unhealthy / Very unhealthy / Hazardous)

### /today compact — Fields & layout

**Dropped:** humidity, AQI, wind direction, condition label, decimals

**Column budgets (monospace, target 29 display chars/row):**
- Time: 4 chars (`12PM`, ` 2PM`)
- Temp/feels: `18/14` (5 chars), `°C` in header
- Condition: 1 emoji (2 display cols); night variants before sunrise and after sunset
- Rain: `10/0` — probability + mm, `%/mm` in header; probability capped at 99, amount ≥100mm shown as `HVY`
- Wind: `wind_speed_10m`, 2 chars right-aligned, `mph` in header
- UV: `uv_index`, 2 chars right-aligned, `UV` in header

Each row must stay within **35 characters** to avoid wrapping on most phones.

### /today extended — Fields

- Temp: `temperature_2m` + `apparent_temperature` (feels like)
- Humidity: `relative_humidity_2m` %
- Condition: WMO code → emoji + label + `cloud_cover` %
- Visibility: `visibility` m → km (e.g. 16km)
- Rain: `precipitation_probability` % + `precipitation` mm
- Wind: `wind_speed_10m` mph + 8-direction cardinal + Beaufort label + `wind_gusts_10m` mph
- UV: `uv_index` + label
- AQI: `us_aqi` + label

### /week — Fields & layout

**Compact column budgets (monospace, target 27 display chars/row):**
- Day: 6 chars (`Mon 14`, `Sat  7`)
- Condition: 1 emoji (2 display cols); always day variant
- Temp: `temperature_2m_max` / `temperature_2m_min`, `°C` in header
- Rain: `precipitation_probability_max` / `precipitation_sum` — capped at 99; ≥100mm shown as `HV`; `%/mm` in header
- Wind: `wind_speed_10m_max`, 2 chars right-aligned, `mph` in header
- UV: `uv_index_max`, 2 chars right-aligned, `UV` in header

**Extended fields (per day):**
- Condition: `weather_code` → emoji + label
- Temp: `temperature_2m_max` / `temperature_2m_min` + `apparent_temperature_max` / `apparent_temperature_min` (feels like)
- Rain: `precipitation_probability_max` % + `precipitation_sum` mm
- Wind: `wind_speed_10m_max` mph + `wind_direction_10m_dominant` + `wind_gusts_10m_max` mph
- UV: `uv_index_max` + label
- AQI: daily max `us_aqi` (from Air Quality API hourly, aggregated) + label
- Sunrise/sunset: `sunrise` / `sunset` per day
