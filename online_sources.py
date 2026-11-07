"""
online_sources.py
Free online resources for Create Mode, chosen and filtered by ORBIT's own
Creative Feature Matching Algorithm (creative_match.py).

    Images      Unsplash (photos), Openverse (openly licensed images), Pixabay (photos and pattern illustrations)
    Music       Last.fm (songs by tag), MusicBrainz (checks that a song exists and adds its genre tags)
    Fonts       Google Fonts (the full list of families and categories)

Rules this file follows:
- Only ORBIT's own search phrases from the Creative Brief are sent, never the user's words.
- Nothing is fetched after a crisis check, in offline demo mode, or when "Online images and music"
  is switched off in Settings. Tests run with ORBIT_OFFLINE=1.
- Keys come from Streamlit Secrets or environment variables, never from the code.
- Every search is remembered for 24 hours (Pixabay requires this) and each service has a request
  budget below its free limit. If a service has no key, reaches its budget or fails, it is skipped
  and Create Mode carries on with the others (or with ORBIT's own resources).
- Safe-search filters are always on, and every image keeps its credit and licence.
"""
import os
import re
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st

import creative_match
import storage

TIMEOUT = 5
DAY = 24 * 60 * 60
USER_AGENT = "ORBIT-CreativeStudio/1.0 ( https://github.com/aanyajohorey-glitch/orbitttt )"
UTM = "utm_source=orbit_creative_studio&utm_medium=referral"
KEYS = {"unsplash": "UNSPLASH_ACCESS_KEY", "pixabay": "PIXABAY_API_KEY", "lastfm": "LASTFM_API_KEY",
        "googlefonts": "GOOGLE_FONTS_API_KEY"}
BUDGETS = {"unsplash": (40, 3600), "openverse": (15, 60), "pixabay": (80, 60), "lastfm": (60, 60),
           "musicbrainz": (1, 1.1), "googlefonts": (20, 3600)}
IMAGE_KEYWORD_POINTS = 0.6
IMAGE_COLOUR_POINTS = 0.3
SEARCH_POINTS = 0.1
AVOID_POINTS = -0.5
KEEP_SCORE = 0.3
KEEP_IMAGE = 0.5
MOODBOARD_SIZE = 9
PER_SEARCH = 3
NEVER_IN_MOODBOARD = ["car", "vehicle", "truck", "motorcycle", "logo", "screenshot", "diagram", "chart",
                      "advertisement", "sale", "price", "avatar", "render", "secondlife", "second life"]
DISCOVER_SIZE = 5


class SourceError(Exception):
    pass


def secret(name):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name)


def has_key(source):
    return source not in KEYS or bool(secret(KEYS[source]))


def enabled():
    """Online sources are used unless switched off, in demo mode, or while testing."""
    if os.environ.get("ORBIT_OFFLINE") == "1":
        return False
    try:
        import demo_mode
        if demo_mode.enabled():
            return False
    except Exception:
        pass
    return storage.get_setting("online_sources", "1") == "1"


_lock = threading.Lock()
_cache = {}
_calls = {name: deque() for name in BUDGETS}


def _allowed(source):
    """True if the source is still inside its request budget (e.g. Unsplash: 40 per hour)."""
    limit, seconds = BUDGETS[source]
    with _lock:
        recent = _calls[source]
        while recent and time.time() - recent[0] > seconds:
            recent.popleft()
        if len(recent) >= limit:
            return False
        recent.append(time.time())
        return True


def remembered(key, fetch, seconds=DAY):
    """Return a saved answer for this search if it is less than a day old, otherwise fetch it.
    Failures are not saved, so a service that was down is tried again next time."""
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < seconds:
            return hit[1]
    value = fetch()
    with _lock:
        _cache[key] = (time.time(), value)
    return value


def get_json(source, url, params=None, headers=None, counted=True):
    if counted and not _allowed(source):
        raise SourceError("limit reached")
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT,
                                headers={"User-Agent": USER_AGENT, **(headers or {})})
    except requests.RequestException as error:
        raise SourceError("unavailable") from error
    if response.status_code in (401, 403):
        raise SourceError("key not accepted")
    if response.status_code == 429:
        raise SourceError("limit reached")
    if response.status_code != 200:
        raise SourceError("unavailable")
    return response.json()


def stem(word):
    return word[:-1] if word.endswith("s") and len(word) > 3 else word


def words_in(text):
    return {stem(w) for w in re.findall(r"[a-z]+", (text or "").lower())}


def hex_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def colour_closeness(colour, palette_hexes):
    """1 when the image's main colour equals a palette colour, 0 when it is very far from all of them."""
    if not colour or not palette_hexes:
        return None
    r, g, b = hex_rgb(colour)
    distance = min(((r - x) ** 2 + (g - y) ** 2 + (b - z) ** 2) ** 0.5 for x, y, z in map(hex_rgb, palette_hexes))
    return max(0.0, 1 - distance / 200)


def unsplash(query):
    key = secret(KEYS["unsplash"])
    data = get_json("unsplash", "https://api.unsplash.com/search/photos",
                    {"query": query, "per_page": 12, "content_filter": "high"},
                    {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"})
    images = []
    for item in data.get("results", []):
        user = item.get("user", {})
        images.append({
            "id": "unsplash-" + item["id"], "source": "Unsplash", "query": query,
            "thumb": item["urls"]["small"], "link": f'{item["links"]["html"]}?{UTM}',
            "title": item.get("alt_description") or item.get("description") or "",
            "tags": [t.get("title", "") for t in item.get("tags", [])], "colour": item.get("color"),
            "author": user.get("name", "Unknown"), "author_link": f'{user.get("links", {}).get("html", "")}?{UTM}',
            "licence": "Unsplash License", "licence_link": f"https://unsplash.com/license?{UTM}",
            "credit": f'Photo by {user.get("name", "Unknown")} on Unsplash'})
    return images


def pixabay(query, kind="photo"):
    data = get_json("pixabay", "https://pixabay.com/api/",
                    {"key": secret(KEYS["pixabay"]), "q": query, "image_type": kind, "safesearch": "true",
                     "per_page": 12})
    images = []
    for item in data.get("hits", []):
        images.append({
            "id": f'pixabay-{item["id"]}', "source": "Pixabay", "query": query, "kind": kind,
            "thumb": item["webformatURL"], "link": item["pageURL"], "title": "",
            "tags": [t.strip() for t in item.get("tags", "").split(",")], "colour": None,
            "author": item.get("user", "Unknown"),
            "author_link": f'https://pixabay.com/users/{item.get("user", "")}-{item.get("user_id", "")}/',
            "licence": "Pixabay Content License", "licence_link": "https://pixabay.com/service/license-summary/",
            "credit": f'Image by {item.get("user", "Unknown")} from Pixabay'})
    return images


def openverse_token():
    """Optional: with free Openverse credentials (OPENVERSE_CLIENT_ID and OPENVERSE_CLIENT_SECRET) ORBIT
    gets a higher limit than anonymous use. The token is kept for 11 hours (it lasts about 12)."""
    client_id, client_secret = secret("OPENVERSE_CLIENT_ID"), secret("OPENVERSE_CLIENT_SECRET")
    if not (client_id and client_secret):
        return None

    def fetch():
        try:
            response = requests.post("https://api.openverse.org/v1/auth_tokens/token/", timeout=TIMEOUT,
                                     data={"grant_type": "client_credentials", "client_id": client_id,
                                           "client_secret": client_secret}, headers={"User-Agent": USER_AGENT})
        except requests.RequestException as error:
            raise SourceError("unavailable") from error
        if response.status_code != 200:
            raise SourceError("key not accepted")
        return response.json().get("access_token")
    try:
        return remembered(("openverse-token",), fetch, seconds=11 * 60 * 60)
    except SourceError:
        return None


def openverse(query):
    token = openverse_token()
    data = get_json("openverse", "https://api.openverse.org/v1/images/",
                    {"q": query, "page_size": 12, "mature": "false", "category": "photograph"},
                    {"Authorization": f"Bearer {token}"} if token else None)
    images = []
    for item in data.get("results", []):
        licence = f'CC {item.get("license", "").upper()} {item.get("license_version", "")}'.strip()
        if item.get("license") in ("cc0", "pdm"):
            licence = "Public domain" if item.get("license") == "pdm" else "CC0"
        images.append({
            "id": "openverse-" + item["id"], "source": "Openverse", "query": query,
            "thumb": item.get("thumbnail") or item.get("url"), "link": item.get("foreign_landing_url") or item.get("url"),
            "title": item.get("title") or "", "tags": [t.get("name", "") for t in item.get("tags") or []],
            "colour": None, "author": item.get("creator") or "Unknown", "author_link": item.get("creator_url") or "",
            "licence": licence, "licence_link": item.get("license_url") or "",
            "credit": item.get("attribution") or f'"{item.get("title", "")}" by {item.get("creator", "Unknown")}'})
    return images


def score_image(image, keywords, avoid, palette_hexes):
    """ORBIT's image score:
        +0.6 x (brief keywords found in the title and tags / 3, at most 1)
        +0.3 x colour closeness to the palette (when the source gives a colour; otherwise half marks)
        +0.1 because it came from an on-brief search
        -0.5 if a word the style avoids appears"""
    text = words_in(image["title"] + " " + " ".join(image["tags"]))
    hits = [k for k in keywords if stem(k) in text]
    closeness = colour_closeness(image.get("colour"), palette_hexes)
    score = IMAGE_KEYWORD_POINTS * min(1.0, len(hits) / 3)
    score += IMAGE_COLOUR_POINTS * (closeness if closeness is not None else 0.5)
    score += SEARCH_POINTS
    avoided = [a for a in list(avoid) + NEVER_IN_MOODBOARD if all(stem(w) in text for w in words_in(a))]
    if avoided:
        score += AVOID_POINTS
    return round(score, 3), hits, avoided


def pick_images(candidates, size=MOODBOARD_SIZE):
    """Best first, at most one image per photographer, no repeats, at most 3 images from each search,
    and taking turns between the searches so the moodboard is varied."""
    seen_ids, seen_authors, seen_titles = set(), set(), set()
    by_source = {}
    for image in sorted(candidates, key=lambda i: -i["score"]):
        if image["score"] < KEEP_IMAGE or image["id"] in seen_ids:
            continue
        title = " ".join(sorted(words_in(image["title"])))
        if image["author"] in seen_authors or (title and title in seen_titles):
            continue
        seen_ids.add(image["id"])
        seen_authors.add(image["author"])
        if title:
            seen_titles.add(title)
        group = by_source.setdefault((image["source"], image["query"]), [])
        if len(group) < PER_SEARCH:
            group.append(image)
    chosen = []
    while len(chosen) < size and any(by_source.values()):
        for group in sorted(by_source.values(), key=lambda g: -(g[0]["score"] if g else 0)):
            if group and len(chosen) < size:
                chosen.append(group.pop(0))
    return chosen


def _run(jobs):
    """Run several searches at the same time. Returns ({job name: results}, {source: status})."""
    results, status = {}, {}

    def one(job):
        name, source, key, fetch = job
        try:
            return name, source, remembered(key, fetch), None
        except SourceError as error:
            return name, source, [], str(error)
        except Exception:
            return name, source, [], "unavailable"
    with ThreadPoolExecutor(max_workers=6) as pool:
        for name, source, value, problem in pool.map(one, jobs):
            results[name] = value
            if problem:
                status[source] = problem
            else:
                status.setdefault(source, "used")
    return results, status


def visuals(brief, found, palette_result):
    """The moodboard images for a Creative Brief, plus a status line for each source."""
    status = {}
    jobs = []
    queries = brief["image_queries"]
    openverse_queries = queries[1:3] or queries[:1]
    if has_key("unsplash"):
        jobs += [(f"u{i}", "unsplash", ("unsplash", q), lambda q=q: unsplash(q)) for i, q in enumerate(queries[:2])]
    else:
        status["unsplash"] = "no key"
        openverse_queries = queries[:4]
    jobs += [(f"o{i}", "openverse", ("openverse", q), lambda q=q: openverse(q))
             for i, q in enumerate(openverse_queries)]
    if has_key("pixabay"):
        pattern_query = f'{brief["patterns"][0]} pattern' if brief["patterns"] else queries[0]
        jobs += [("p0", "pixabay", ("pixabay", queries[-1], "photo"), lambda: pixabay(queries[-1], "photo")),
                 ("p1", "pixabay", ("pixabay", pattern_query, "illustration"),
                  lambda: pixabay(pattern_query, "illustration"))]
    else:
        status["pixabay"] = "no key"
    results, run_status = _run(jobs)
    status.update(run_status)
    keywords = creative_match.image_keywords(found)
    palette_hexes = [c["hex"] for c in palette_result.get("story", palette_result["colours"])]
    candidates = []
    for images in results.values():
        for image in images:
            score, hits, avoided = score_image(image, keywords, brief["avoid"], palette_hexes)
            candidates.append({**image, "score": score, "hits": hits, "avoided": avoided})
    return {"images": pick_images(candidates), "status": status, "checked": len(candidates)}


def lastfm_tag(tag):
    data = get_json("lastfm", "https://ws.audioscrobbler.com/2.0/",
                    {"method": "tag.gettoptracks", "tag": tag, "api_key": secret(KEYS["lastfm"]),
                     "format": "json", "limit": 30})
    tracks = []
    for item in data.get("tracks", {}).get("track", []):
        artist = item.get("artist", {})
        tracks.append({"title": item.get("name", ""), "artist": artist.get("name", "") if isinstance(artist, dict)
                       else str(artist), "lastfm_link": item.get("url", ""), "tag": tag})
    return tracks


_musicbrainz_lock = threading.Lock()


def musicbrainz(title, artist):
    """Check a song exists and read its genre tags. At most one request per second (MusicBrainz's rule)."""
    with _musicbrainz_lock:
        while not _allowed("musicbrainz"):
            time.sleep(0.2)
        query = f'recording:"{title}" AND artist:"{artist}"'
        data = get_json("musicbrainz", "https://musicbrainz.org/ws/2/recording/",
                        {"query": query, "fmt": "json", "limit": 1}, counted=False)
    found = (data.get("recordings") or [None])[0]
    if not found or int(found.get("score", 0)) < 85:
        return None
    tags = [t.get("name", "") for t in found.get("tags", [])]
    release = (found.get("first-release-date") or "")[:4]
    return {"tags": tags, "year": release, "link": f'https://musicbrainz.org/recording/{found["id"]}'}


def same_song(a_title, a_artist, b_title, b_artist):
    key = lambda title, artist: (re.sub(r"[^a-z0-9]", "", title.lower().split("(")[0]),
                                 re.sub(r"[^a-z0-9]", "", artist.lower()))
    return key(a_title, a_artist) == key(b_title, b_artist)


def score_track(track, tag_hits, tag_count, check, style_words, avoid):
    """ORBIT's song score:
        +0.6 x (brief tags this song appears under / tags searched)
        +0.4 if MusicBrainz confirms the song and one of its genre tags fits the style
        -0.5 if a word the style avoids appears in the title, artist or genre tags"""
    score = 0.6 * tag_hits / max(1, tag_count)
    fits = []
    if check:
        fits = [t for t in check["tags"] if words_in(t) & style_words]
        if fits:
            score += 0.4
    text = words_in(f'{track["title"]} {track["artist"]} {" ".join(check["tags"] if check else [])}')
    if any(all(stem(w) in text for w in words_in(a)) for a in avoid):
        score += AVOID_POINTS
    return round(score, 3), fits


def discover_music(brief, found, curated):
    """Extra songs from Last.fm for the brief's music tags, checked with MusicBrainz, without repeating
    ORBIT's own playlist. Returns {"tracks": [...], "status": {...}}."""
    if not has_key("lastfm"):
        return {"tracks": [], "status": {"lastfm": "no key"}}
    tags = brief["lastfm_tags"][:2]
    results, status = _run([(tag, "lastfm", ("lastfm", tag), lambda tag=tag: lastfm_tag(tag)) for tag in tags])
    counts = {}
    for tag in tags:
        for track in results.get(tag, []):
            key = (track["title"].lower(), track["artist"].lower())
            entry = counts.setdefault(key, {**track, "tags": []})
            entry["tags"].append(tag)
    candidates = [t for t in counts.values()
                  if not any(same_song(t["title"], t["artist"], c["title"], c["artist"]) for c in curated)]
    candidates.sort(key=lambda t: -len(t["tags"]))
    style_words = set()
    for field in ("music_tags", "music_genres", "lastfm_tags", "atmosphere"):
        for phrase in creative_match.merged(found, field):
            style_words |= words_in(phrase)
    chosen, artists = [], set()
    for track in candidates[:12]:
        if track["artist"].lower() in artists:
            continue
        check = None
        if len(chosen) < 4:
            try:
                check = remembered(("musicbrainz", track["title"], track["artist"]),
                                   lambda t=track: musicbrainz(t["title"], t["artist"]))
                status.setdefault("musicbrainz", "used")
            except SourceError as error:
                status["musicbrainz"] = str(error)
        score, fits = score_track(track, len(track["tags"]), len(tags), check, style_words, brief["avoid"])
        if score >= KEEP_SCORE:
            artists.add(track["artist"].lower())
            chosen.append({**track, "score": score, "verified": bool(check), "fits": fits,
                           "year": check["year"] if check else "", "musicbrainz_link": check["link"] if check else ""})
        if len(chosen) == DISCOVER_SIZE:
            break
    return {"tracks": chosen, "status": status}


CATEGORY_FOR_TAG = {
    "serif": {"elegant", "classic", "literary", "bookish", "victorian", "roman", "historic", "scholarly", "editorial"},
    "display": {"blackletter", "medieval", "art-deco", "neon", "poster", "bold", "retro-futurist", "pixel", "epic",
                "dramatic", "futuristic", "sci-fi", "groovy", "disco", "festive", "loud", "grunge"},
    "handwriting": {"romantic", "wedding", "handwritten", "calligraphic", "delicate", "cosy", "journal", "doodle"},
    "sans-serif": {"clean", "minimal", "modern", "tech", "geometric", "rounded", "friendly", "neutral", "urban"},
    "monospace": {"code", "terminal", "typewriter"},
}


def google_fonts():
    data = get_json("googlefonts", "https://www.googleapis.com/webfonts/v1/webfonts",
                    {"key": secret(KEYS["googlefonts"]), "sort": "popularity"})
    return [{"family": f["family"], "category": f.get("category", "")} for f in data.get("items", [])]


def more_fonts(found, known_families, size=4):
    """Popular Google Fonts in the categories the style's typography asks for, that ORBIT's own list
    doesn't have yet. Score = 0.6 x category fit + 0.4 x popularity."""
    if not has_key("googlefonts"):
        return {"fonts": [], "status": {"googlefonts": "no key"}}
    try:
        families = remembered(("googlefonts",), google_fonts)
    except SourceError as error:
        return {"fonts": [], "status": {"googlefonts": str(error)}}
    wanted = {}
    for tag in creative_match.merged(found, "font_tags"):
        for category, tags in CATEGORY_FOR_TAG.items():
            if tag in tags:
                wanted[category] = wanted.get(category, 0) + 1
    if not wanted:
        return {"fonts": [], "status": {"googlefonts": "used"}}
    best = max(wanted.values())
    known = {k.lower() for k in known_families}
    scored = []
    for rank, font in enumerate(families[:400]):
        if font["family"].lower() in known or font["category"] not in wanted:
            continue
        score = 0.6 * wanted[font["category"]] / best + 0.4 * (1 - rank / 400)
        scored.append({**font, "score": round(score, 3)})
    scored.sort(key=lambda f: -f["score"])
    return {"fonts": scored[:size], "status": {"googlefonts": "used"}}


def gather(brief, found, palette_result, curated_music, known_fonts):
    """Everything online for one creative universe. Never raises: problems become status notes."""
    empty = {"images": [], "status": {}, "checked": 0}
    try:
        images = visuals(brief, found, palette_result)
    except Exception:
        images = {**empty, "status": {"images": "unavailable"}}
    try:
        music = discover_music(brief, found, curated_music)
    except Exception:
        music = {"tracks": [], "status": {"lastfm": "unavailable"}}
    try:
        fonts = more_fonts(found, known_fonts)
    except Exception:
        fonts = {"fonts": [], "status": {"googlefonts": "unavailable"}}
    return {"images": images["images"], "checked": images["checked"], "tracks": music["tracks"],
            "fonts": fonts["fonts"], "status": {**images["status"], **music["status"], **fonts["status"]}}
