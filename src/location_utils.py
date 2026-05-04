import forecast


def loc_label(loc):
    return ", ".join(filter(None, [loc.city_name, loc.county, loc.state, loc.country]))


async def resolve_location(context, city_arg=None):
    locs = context.user_data.get("locations", [])
    if not city_arg:
        if not locs:
            return None, False, "No locations set. Add one with /locations"
        return locs[0], True, None
    results = await forecast.geocode(city_arg)
    if not results:
        return None, False, f'No location found for "{city_arg}".'
    # Prefer a geocoded result that the user already has saved; fall back to top result.
    saved_ids = {l.id for l in locs}
    loc = next((r for r in results if r.id in saved_ids), None)
    matched = loc is not None
    if not matched:
        loc = results[0]
        # Stash so toggle buttons (which look up by id) can still resolve this location.
        context.chat_data.setdefault("oneoff_locs", {})[loc.id] = loc
    return loc, matched, None


def lookup_location(context, loc_id):
    locs = context.user_data.get("locations", [])
    loc = next((l for l in locs if l.id == loc_id), None)
    if loc is None:
        loc = context.chat_data.get("oneoff_locs", {}).get(loc_id)
    return loc


def oneoff_note(loc):
    return f"\n\n_📍 {loc_label(loc)} · not saved — /locations to add it._"
