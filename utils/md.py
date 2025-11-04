from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from slugify import slugify
import markdown
import yaml
import re
import sys

DATE_KEYS = ("date", "published", "created")

@dataclass
class Document:
    source_path: Path
    slug: str
    title: str
    html: str
    summary: str
    date: datetime | None
    tags: list[str] = field(default_factory=list)
    type: str = "post"

    def url(self) -> str:
        return f"/post/{self.slug}" if self.type == "post" else f"/{self.slug}"

FM_START = '---\n'
FM_END = '\n---\n'

def _safe_yaml_load(text: str, src: Path) -> dict:
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        fixed = re.sub(r'^(title:\s*)(.+)$', lambda m: m.group(1) + '"' + m.group(2).replace('"','\\"') + '"', text, flags=re.MULTILINE)
        if fixed != text:
            try:
                return yaml.safe_load(fixed) or {}
            except Exception:
                pass
        print(f"[WARN] YAML front matter parse failed in {src}: {e}", file=sys.stderr)
        return {}

def split_front_matter(text: str, src: Path) -> tuple[dict, str]:
    if text.startswith(FM_START):
        _, rest = text.split(FM_START, 1)
        if FM_END in rest:
            fm, body = rest.split(FM_END, 1)
            data = _safe_yaml_load(fm, src)
            return data, body
    return {}, text

def to_datetime(meta: dict) -> datetime | None:
    for k in DATE_KEYS:
        v = meta.get(k)
        if not v:
            continue
        if isinstance(v, datetime):
            return v
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(str(v), fmt)
            except Exception:
                pass
        try:
            return datetime.fromisoformat(str(v))
        except Exception:
            continue
    return None

def render_markdown(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["extra","smarty","toc","tables","fenced_code"])

def read_document(path: Path, doc_type: str) -> Document:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_front_matter(raw, path)
    title = meta.get("title") or path.stem
    slug = meta.get("slug") or slugify(title)
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    dt = to_datetime(meta)

    html = render_markdown(body)
    text_only = re.sub(r"<[^<]+?>", "", html)
    summary = (text_only[:220] + "…") if len(text_only) > 220 else text_only

    return Document(
        source_path=path,
        slug=slug,
        title=title,
        html=html,
        summary=summary,
        date=dt,
        tags=tags,
        type=doc_type,
    )

def load_posts(posts_dir: Path) -> list[Document]:
    docs = []
    if not posts_dir.exists():
        return docs
    for p in sorted(posts_dir.glob("*.md")):
        try:
            docs.append(read_document(p, "post"))
        except Exception as e:
            print(f"[WARN] Failed to read post {p}: {e}", file=sys.stderr)
    docs.sort(key=lambda d: d.date or datetime.min, reverse=True)
    return docs

def load_pages(pages_dir: Path) -> list[Document]:
    docs = []
    if not pages_dir.exists():
        return docs
    for p in sorted(pages_dir.glob("*.md")):
        try:
            docs.append(read_document(p, "page"))
        except Exception as e:
            print(f"[WARN] Failed to read page {p}: {e}", file=sys.stderr)
    return docs
