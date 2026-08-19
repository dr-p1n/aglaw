#!/usr/bin/env python3
"""
Rebuild dist-multipage/ and dist-multipage.zip from the sources.

dist-multipage/ is a literal copy of the deployable files — no transform,
no inlining. It exists so Jaime can download one zip from GitHub and drop
its contents into public_html via cPanel File Manager.

Keeping the copy in sync by hand is how the zip went stale before, so the
file list lives here instead of in someone's head.

Run from repo root:  python3 scripts/build-dist-multipage.py
"""

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist-multipage"
ZIP = ROOT / "dist-multipage.zip"

# Everything that has to land on the server, relative to the repo root.
FILES = [
    # Spanish
    "index.html",
    "practica/index.html",
    "red/index.html",
    "recursos/index.html",
    "perfil/index.html",
    # English
    "en/index.html",
    "en/practice/index.html",
    "en/network/index.html",
    "en/resources/index.html",
    "en/about/index.html",
    # Assets
    "styles.css",
    "img/alberto.jpg",
    "img/alberto-retrato.jpg",
    "img/alberto-cmb.jpg",
    "favicon.ico",
    "favicon.svg",
    "apple-touch-icon.png",
    # Server config and crawler files
    ".htaccess",
    "robots.txt",
    "sitemap.xml",
]


def main():
    missing = [f for f in FILES if not (ROOT / f).exists()]
    if missing:
        raise SystemExit("missing source files: " + ", ".join(missing))

    if DIST.exists():
        shutil.rmtree(DIST)

    for rel in FILES:
        dest = DIST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)

    # Deterministic zip: fixed order, fixed timestamps, so an unchanged
    # site produces an unchanged zip instead of a noisy diff every build.
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in FILES:
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (ROOT / rel).read_bytes())

    print(f"Wrote {DIST}/ ({len(FILES)} files)")
    print(f"Wrote {ZIP} ({ZIP.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
