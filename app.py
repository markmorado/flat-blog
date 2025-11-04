from __future__ import annotations
from flask import Flask, render_template, abort, request, Response
from utils.md import load_posts, load_pages, Document
import config, os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "")

_posts: list[Document] = []
_pages: list[Document] = []

def refresh_content() -> None:
    global _posts, _pages
    _posts = load_posts(config.POSTS_DIR)
    _pages = load_pages(config.PAGES_DIR)

@app.context_processor
def inject_globals():
    return dict(
        SITE_TITLE=config.SITE_TITLE,
        SITE_TAGLINE=config.SITE_TAGLINE,
        ACTIVE_THEME=config.THEME
    )

@app.before_request
def _auto_reload():
    refresh_content()

@app.get("/favicon.ico")
def favicon():
    return ("", 204)

def t(name: str) -> str:
    return f"themes/{config.THEME}/{name}"

@app.get("/")
@app.get("/page/<int:n>")
def index(n: int = 1):
    total = len(_posts)
    per = config.POSTS_PER_PAGE
    pages = max(1, (total + per - 1) // per)
    if n < 1 or n > pages:
        abort(404)
    start = (n - 1) * per
    end = start + per
    items = _posts[start:end]
    return render_template(t("index.html"), posts=items, page=n, pages=pages)

@app.get("/post/<slug>")
def post(slug: str):
    for p in _posts:
        if p.slug == slug:
            return render_template(t("post.html"), post=p)
    abort(404)

@app.get("/<slug>")
def page(slug: str):
    for p in _pages:
        if p.slug == slug:
            return render_template(t("page.html"), page=p)
    abort(404)

@app.get("/tag/<tag>")
def by_tag(tag: str):
    items = [p for p in _posts if tag in p.tags]
    return render_template(t("tag.html"), tag=tag, posts=items)

@app.get("/search")
def search():
    q = (request.args.get("q") or "").strip().lower()
    items = []
    if q:
        for p in _posts:
            hay = f"{p.title}\n{p.summary}".lower()
            if q in hay:
                items.append(p)
    return render_template(t("search.html"), q=q, posts=items)

@app.get("/rss.xml")
def rss():
    xml = render_template(t("rss.xml"), posts=_posts)
    return Response(xml, mimetype="application/rss+xml")

@app.get("/sitemap.xml")
def sitemap():
    xml = render_template(t("sitemap.xml"), posts=_posts, pages=_pages)
    return Response(xml, mimetype="application/xml")

# Admin
from admin import bp as admin_bp
app.register_blueprint(admin_bp)

@app.errorhandler(404)
def not_found(e):
    return render_template(t("404.html")), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
