"""Wingato Open - a downloader for openly-licensed / public-domain media.

Sources: Internet Archive and Wikimedia Commons. No scraping of
YouTube/Instagram/etc., which keeps the app within hosting terms and
advertiser policies.

Routes
------
GET  /            home (search)
GET  /search      results
GET  /item        an Internet Archive item's downloadable files
GET  /download    stream a file to the user (allowlisted hosts only)
GET  /about       about + licensing note
GET  /contact     contact / takedown
"""
import os
from urllib.parse import quote

import requests
from flask import (
    Flask, render_template, request, jsonify,
    Response, abort, stream_with_context,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import sources

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "60 per hour"],
)

CHUNK = 64 * 1024


@app.template_filter("filesize")
def filesize(size):
    if not size:
        return "?"
    size = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@app.template_filter("shortnum")
def shortnum(n):
    if not n:
        return "-"
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    for div, suf in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if n >= div:
            return f"{n / div:.1f}{suf}"
    return str(n)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
@limiter.limit("30 per minute")
def search():
    q = request.args.get("q", "").strip()
    source = request.args.get("source", "all")
    if source not in ("all", "archive", "commons"):
        source = "all"
    results = sources.search(q, source) if q else []
    return render_template("results.html", q=q, source=source, results=results)


@app.route("/item")
@limiter.limit("30 per minute")
def item():
    identifier = request.args.get("id", "").strip()
    if not identifier:
        abort(400)
    try:
        data = sources.archive_item(identifier)
    except Exception as e:
        return render_template("item.html", item=None, error=str(e)), 502
    return render_template("item.html", item=data, error=None)


@app.route("/download")
@limiter.limit("20 per minute")
def download():
    url = request.args.get("url", "").strip()
    name = request.args.get("name", "download").strip() or "download"
    if not url or not sources.is_allowed_url(url):
        abort(400)

    try:
        upstream = requests.get(
            url,
            stream=True,
            timeout=30,
            headers={"User-Agent": sources.USER_AGENT},
        )
        upstream.raise_for_status()
    except requests.RequestException:
        abort(502)

    content_type = upstream.headers.get("Content-Type", "application/octet-stream")
    length = upstream.headers.get("Content-Length")

    def generate():
        try:
            for chunk in upstream.iter_content(chunk_size=CHUNK):
                if chunk:
                    yield chunk
        finally:
            upstream.close()

    resp = Response(stream_with_context(generate()), content_type=content_type)
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(name)}"
    if length:
        resp.headers["Content-Length"] = length
    return resp


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html", error="Page not found."), 404


@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": "Too many requests. Wait a bit."}), 429


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
