"""Wingato Open - sources layer.

Only pulls from libraries whose content is openly licensed or public
domain and whose APIs permit downloading:

  * Internet Archive  (archive.org)      - public domain / CC media
  * Wikimedia Commons (commons.wikimedia.org) - public domain / CC media

No scraping of YouTube / Instagram / etc. This is what keeps the site
within hosting terms and advertiser policies.
"""
import json
import urllib.parse
import urllib.request

USER_AGENT = "WingatoOpen/1.0 (open-media downloader)"

# Hosts we are willing to fetch from / stream through. Prevents the
# download endpoint being abused as an open proxy (SSRF).
ALLOWED_HOSTS = (
    "archive.org",
    "upload.wikimedia.org",
    "commons.wikimedia.org",
)

MEDIA_EXT = (
    ".mp4", ".webm", ".ogv", ".mov", ".mkv",
    ".mp3", ".ogg", ".oga", ".m4a", ".wav", ".flac",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".tif", ".tiff",
    ".pdf", ".srt", ".vtt", ".txt",
)


def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def is_allowed_url(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


# --------------------------------------------------------------------------
# Internet Archive
# --------------------------------------------------------------------------
def search_archive(query, rows=24):
    q = urllib.parse.quote(query)
    url = (
        "https://archive.org/advancedsearch.php"
        f"?q={q}"
        "&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=year"
        "&fl[]=mediatype&fl[]=downloads"
        f"&rows={rows}&page=1&output=json&sort[]=downloads+desc"
    )
    data = _get_json(url)
    out = []
    for doc in data.get("response", {}).get("docs", []):
        ident = doc.get("identifier")
        if not ident:
            continue
        out.append({
            "source": "archive",
            "id": ident,
            "title": doc.get("title") or ident,
            "creator": doc.get("creator"),
            "year": doc.get("year"),
            "mediatype": doc.get("mediatype"),
            "downloads": doc.get("downloads"),
            "thumb": f"https://archive.org/services/img/{ident}",
            "page": f"https://archive.org/details/{ident}",
        })
    return out


def archive_item(identifier):
    data = _get_json(f"https://archive.org/metadata/{identifier}")
    md = data.get("metadata", {}) or {}
    files = []
    for f in data.get("files", []):
        name = f.get("name", "")
        low = name.lower()
        if not low.endswith(MEDIA_EXT):
            continue
        # skip archive's generated thumbnails / sidecar junk
        if ".thumbs/" in low or "__ia_thumb" in low or low.startswith("._"):
            continue
        size = f.get("size")
        files.append({
            "name": name,
            "format": f.get("format"),
            "size": int(size) if str(size).isdigit() else None,
            "url": f"https://archive.org/download/{identifier}/{urllib.parse.quote(name)}",
        })
    files.sort(key=lambda x: (x["size"] or 0))
    return {
        "source": "archive",
        "id": identifier,
        "title": md.get("title") or identifier,
        "creator": md.get("creator"),
        "date": md.get("date") or md.get("year"),
        "licenseurl": md.get("licenseurl"),
        "rights": md.get("rights"),
        "description": (md.get("description") or "")[:1500],
        "page": f"https://archive.org/details/{identifier}",
        "thumb": f"https://archive.org/services/img/{identifier}",
        "files": files,
    }


# --------------------------------------------------------------------------
# Wikimedia Commons
# --------------------------------------------------------------------------
def search_commons(query, limit=24):
    url = (
        "https://commons.wikimedia.org/w/api.php?action=query&format=json"
        f"&list=search&srsearch={urllib.parse.quote(query)}"
        f"&srnamespace=6&srlimit={limit}"
    )
    data = _get_json(url)
    titles = [x["title"] for x in data.get("query", {}).get("search", [])]
    if not titles:
        return []

    t = urllib.parse.quote("|".join(titles))
    info_url = (
        "https://commons.wikimedia.org/w/api.php?action=query&format=json"
        f"&titles={t}&prop=imageinfo&iiprop=url|size|mime|extmetadata"
        "&iiurlwidth=320"
    )
    info = _get_json(info_url)
    out = []
    for page in info.get("query", {}).get("pages", {}).values():
        ii = (page.get("imageinfo") or [{}])[0]
        if not ii.get("url"):
            continue
        out.append({
            "source": "commons",
            "id": page["title"],
            "title": page["title"].replace("File:", ""),
            "creator": None,
            "year": None,
            "mediatype": (ii.get("mime") or "").split("/")[0] or "media",
            "downloads": None,
            "thumb": ii.get("thumburl") or ii.get("url"),
            "file_url": ii.get("url"),
            "size": ii.get("size"),
            "mime": ii.get("mime"),
            "page": ii.get("descriptionurl"),
        })
    return out


# --------------------------------------------------------------------------
# Unified search
# --------------------------------------------------------------------------
def search(query, source="all", limit=24):
    query = (query or "").strip()
    if not query:
        return []
    results = []
    if source in ("all", "archive"):
        try:
            results += search_archive(query, rows=limit)
        except Exception:
            pass
    if source in ("all", "commons"):
        try:
            results += search_commons(query, limit=limit)
        except Exception:
            pass
    return results
