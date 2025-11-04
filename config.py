from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

SITE_TITLE = "Flat-Blog"
SITE_TAGLINE = "Лёгкий блог на Flask + Markdown"
SITE_URL = "http://localhost:8000"

CONTENT_DIR = BASE_DIR / "content"
POSTS_DIR = CONTENT_DIR / "posts"
PAGES_DIR = CONTENT_DIR / "pages"

POSTS_PER_PAGE = 6
TIMEZONE = "Asia/Tashkent"
DATE_FMT = "%Y-%m-%d"

THEME = os.getenv("FLATCMS_THEME", "clean")
