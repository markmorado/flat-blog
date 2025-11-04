from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from datetime import datetime
import os, shutil, config
from utils.md import load_posts, read_document
from slugify import slugify

bp = Blueprint("admin", __name__, url_prefix="/admin")

USER = os.getenv("FLATADMIN_USER")
PASS = os.getenv("FLATADMIN_PASS")

def _auth_required():
    if not USER or not PASS:
        abort(503, "Admin disabled: set FLATADMIN_USER and FLATADMIN_PASS")
    if not session.get("auth"):
        return False
    return True

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("u","")
        p = request.form.get("p","")
        if USER and PASS and u == USER and p == PASS:
            session["auth"] = True
            return redirect(url_for("admin.dashboard"))
        return render_template("admin_login.html", error="Неверные данные")
    return render_template("admin_login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))

@bp.route("/")
def dashboard():
    if not _auth_required(): 
        return redirect(url_for("admin.login"))
    posts = load_posts(config.POSTS_DIR)
    return render_template("admin_list.html", posts=posts)

@bp.route("/new", methods=["GET","POST"])
def new_post():
    if not _auth_required(): 
        return redirect(url_for("admin.login"))
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        date  = (request.form.get("date") or datetime.utcnow().strftime("%Y-%m-%d")).strip()
        tags  = (request.form.get("tags") or "").strip()
        body  = (request.form.get("body") or "").strip()
        slug  = slugify((request.form.get("slug") or title).strip())
        tags_yaml = "[" + ",".join([t.strip() for t in tags.split(",") if t.strip()]) + "]" if tags else "[]"
        md = f"""---
title: "{title.replace('"','\\"')}"
date: {date}
tags: {tags_yaml}
---
{body}
"""
        path = config.POSTS_DIR / f"{datetime.utcnow().strftime('%Y-%m-%d')}-{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin_edit.html", mode="new", post=None)

@bp.route("/edit/<slug>", methods=["GET","POST"])
def edit_post(slug: str):
    if not _auth_required(): 
        return redirect(url_for("admin.login"))
    target = None
    for p in config.POSTS_DIR.glob("*.md"):
        doc = read_document(p, "post")
        if doc.slug == slug:
            target = p; break
    if not target:
        abort(404, "Пост не найден")

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        date  = (request.form.get("date") or "").strip()
        tags  = (request.form.get("tags") or "").strip()
        body  = (request.form.get("body") or "").strip()
        tags_yaml = "[" + ",".join([t.strip() for t in tags.split(",") if t.strip()]) + "]" if tags else "[]"
        md = f"""---
title: "{title.replace('"','\\"')}"
date: {date}
tags: {tags_yaml}
---
{body}
"""
        backup = target.with_suffix(".bak.md")
        shutil.copy2(target, backup)
        target.write_text(md, encoding="utf-8")
        return redirect(url_for("admin.dashboard"))

    # GET: open editor
    doc = read_document(target, "post")
    raw = target.read_text(encoding="utf-8")
    body = raw
    if raw.startswith("---\n"):
        _, rest = raw.split("---\n", 1)
        if "\n---\n" in rest:
            _, body = rest.split("\n---\n", 1)
    tags_str = ", ".join(doc.tags)
    return render_template("admin_edit.html", mode="edit", post=doc, date=(doc.date.date() if doc.date else ""), tags=tags_str, body=body)

@bp.route("/delete/<slug>", methods=["POST"])
def delete_post(slug: str):
    if not _auth_required(): 
        return redirect(url_for("admin.login"))
    target = None
    for p in config.POSTS_DIR.glob("*.md"):
        doc = read_document(p, "post")
        if doc.slug == slug:
            target = p; break
    if not target:
        abort(404)
    target.unlink(missing_ok=True)
    return redirect(url_for("admin.dashboard"))
