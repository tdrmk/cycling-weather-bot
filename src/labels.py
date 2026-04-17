WMO_CODES = {
    #                              day   night
    0:  ("Clear",                 "☀️",  "🌙"),
    1:  ("Mainly clear",          "🌤",  "🌙"),
    2:  ("Partly cloudy",         "⛅",  "☁️"),
    3:  ("Overcast",              "☁️",  "☁️"),
    45: ("Fog",                   "🌫",  "🌫"),
    48: ("Rime fog",              "🌫",  "🌫"),

    # Drizzle
    51: ("Drizzle",               "🌦",  "🌦"),
    53: ("Drizzle",               "🌦",  "🌦"),
    55: ("Heavy drizzle",         "🌧",  "🌧"),

    # Freezing drizzle
    56: ("Freezing drizzle",      "🌧",  "🌧"),
    57: ("Freezing drizzle",      "🌧",  "🌧"),

    # Rain
    61: ("Light rain",            "🌦",  "🌦"),
    63: ("Rain",                  "🌧",  "🌧"),
    65: ("Heavy rain",            "🌧",  "🌧"),

    # Freezing rain
    66: ("Freezing rain",         "🌧",  "🌧"),
    67: ("Freezing rain",         "🌧",  "🌧"),

    # Snow
    71: ("Light snow",            "🌨",  "🌨"),
    73: ("Snow",                  "🌨",  "🌨"),
    75: ("Heavy snow",            "🌨",  "🌨"),
    77: ("Snow grains",           "❄️",  "❄️"),

    # Showers
    80: ("Showers",               "🌦",  "🌦"),
    81: ("Showers",               "🌧",  "🌧"),
    82: ("Heavy showers",         "🌧",  "🌧"),

    # Snow showers
    85: ("Snow showers",          "🌨",  "🌨"),
    86: ("Heavy snow showers",    "🌨",  "🌨"),

    # Thunderstorms
    95: ("Thunderstorm",          "⛈️",  "⛈️"),
    96: ("Thunderstorm w/ hail", "⛈️",  "⛈️"),
    99: ("Thunderstorm w/ hail", "⛈️",  "⛈️"),
}


def wmo(code, is_night=False):
    entry = WMO_CODES.get(code, ("Unknown", "❓", "❓"))
    return entry[0], entry[2] if is_night else entry[1]


def wind_cardinal(degrees):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(degrees / 45) % 8]


def beaufort_label(mph):
    if mph <= 1:  return "Calm"
    if mph <= 7:  return "Light"
    if mph <= 12: return "Gentle"
    if mph <= 18: return "Moderate"
    if mph <= 24: return "Fresh"
    if mph <= 31: return "Strong"
    if mph <= 38: return "Near gale"
    return "Gale"


def uv_label(uv):
    if uv <= 2:  return "Low"
    if uv <= 5:  return "Moderate"
    if uv <= 7:  return "High"
    if uv <= 10: return "Very High"
    return "Extreme"


def aqi_label(aqi):
    if aqi <= 50:  return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for sensitive groups"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very unhealthy"
    return "Hazardous"
