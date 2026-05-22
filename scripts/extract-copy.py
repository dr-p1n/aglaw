#!/usr/bin/env python3
"""
Extract written content from every page in the site, in source order,
and emit a single COPY-REVIEW.md at the repo root for human review.

Run from the repo root:    python3 scripts/extract-copy.py

The output is a derived artifact — committed for convenience, but the
HTML files are the source of truth. Re-run this script after any copy
edits to refresh.
"""
import os
import re
from html import unescape

PAGES = [
    ("Page 1 · Home (ES) — /",                "index.html"),
    ("Page 2 · Práctica (ES) — /practica/",   "practica/index.html"),
    ("Page 3 · Red (ES) — /red/",             "red/index.html"),
    ("Page 4 · Recursos (ES) — /recursos/",   "recursos/index.html"),
    ("Page 5 · Perfil (ES) — /perfil/",       "perfil/index.html"),
    ("Page 1 · Home (EN) — /en/",             "en/index.html"),
    ("Page 2 · Practice (EN) — /en/practice/", "en/practice/index.html"),
    ("Page 3 · Network (EN) — /en/network/",   "en/network/index.html"),
    ("Page 4 · Resources (EN) — /en/resources/", "en/resources/index.html"),
    ("Page 5 · About (EN) — /en/about/",       "en/about/index.html"),
]


def inline_clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', s, flags=re.S | re.I)
    s = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = unescape(s)
    lines = [' '.join(line.split()) for line in s.split('\n')]
    return '\n'.join(l for l in lines if l).strip()


PATTERNS = [
    (re.compile(r'<(h[1-6])\b[^>]*>(.*?)</\1>', re.S | re.I), 'heading'),
    (re.compile(r'<p\b([^>]*)>(.*?)</p>', re.S | re.I), 'p'),
    (re.compile(r'<address\b[^>]*>(.*?)</address>', re.S | re.I), 'address'),
    (re.compile(r'<li\b[^>]*>(.*?)</li>', re.S | re.I), 'li'),
    (re.compile(r'<span\s+class="([^"]+)"[^>]*>(.*?)</span>', re.S | re.I), 'span'),
    (re.compile(
        r'<a\s+(?:[^>]*\s)?class="(?:[^"]*\s)?'
        r'(btn-primary|btn-secondary|btn-text|contact-cta|insight-cta|nav-cta)'
        r'(?:\s[^"]*)?"[^>]*>(.*?)</a>',
        re.S | re.I), 'cta'),
]

KEEP_SPAN_CLASSES = (
    'hero-eyebrow', 'page-hero-eyebrow', 'contact-label', 'contact-value',
    'network-tag', 'practice-number', 'practice-tag', 'insight-category',
    'wbc-badge-icon', 'years-big', 'years-text',
)


def class_of(attrs):
    m = re.search(r'class="([^"]+)"', attrs)
    return m.group(1) if m else ''


def collect(html):
    main = re.search(r'<main\b[^>]*>(.*?)</main>', html, re.S | re.I)
    main = main.group(1) if main else ''
    items = []
    for rx, kind in PATTERNS:
        for m in rx.finditer(main):
            pos = m.start()
            if kind == 'heading':
                tag = m.group(1).lower()
                txt = inline_clean(m.group(2))
                if txt:
                    items.append((pos, kind, tag, txt))
            elif kind == 'p':
                cls = class_of(m.group(1))
                txt = inline_clean(m.group(2))
                if txt:
                    items.append((pos, kind, cls, txt))
            elif kind == 'address':
                txt = inline_clean(m.group(1))
                if txt:
                    items.append((pos, kind, '', txt))
            elif kind == 'li':
                txt = inline_clean(m.group(1))
                # Skip honeypot field
                if txt and 'fill' not in txt.lower() and 'llenar' not in txt.lower():
                    items.append((pos, kind, '', txt))
            elif kind == 'span':
                cls, body = m.group(1), m.group(2)
                if not any(k in cls for k in KEEP_SPAN_CLASSES):
                    continue
                txt = inline_clean(body)
                if txt:
                    items.append((pos, kind, cls, txt))
            elif kind == 'cta':
                cls = m.group(1)
                txt = inline_clean(m.group(2))
                if txt:
                    items.append((pos, kind, cls, txt))
    items.sort(key=lambda x: x[0])
    return items


def md_for_page(name, path):
    with open(path) as f:
        html = f.read()
    title = inline_clean(re.search(r'<title>(.*?)</title>', html, re.S).group(1))
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = unescape(desc_m.group(1)) if desc_m else ''
    items = collect(html)
    footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', html, re.S | re.I)
    footer_text = inline_clean(footer.group(1)) if footer else ''

    out = [f'## {name}', '']
    out.append(f'**`<title>`**  {title}')
    out.append(f'**`<meta description>`**  {desc}')
    out.append('')

    i = 0
    while i < len(items):
        pos, kind, cls, txt = items[i]
        if kind == 'heading':
            level = int(cls[1])
            out.append('')
            out.append(f'{"#" * (level + 2)} {txt.replace(chr(10), " / ")}')
            out.append('')
        elif kind == 'span' and 'eyebrow' in cls:
            out.append(f'*{txt}*  ')
        elif kind == 'span' and 'contact-label' in cls:
            label = txt
            value = ''
            if i + 1 < len(items) and items[i + 1][1] == 'span' and 'contact-value' in items[i + 1][2]:
                value = items[i + 1][3].replace('\n', ', ')
                i += 1
            elif i + 1 < len(items) and items[i + 1][1] == 'address':
                value = items[i + 1][3].replace('\n', ', ')
                i += 1
            out.append(f'- **{label}** — {value}')
        elif kind == 'span' and 'network-tag' in cls:
            out.append(f'- {txt}')
        elif kind == 'span' and 'practice-number' in cls:
            if i + 1 < len(items) and items[i + 1][1] == 'heading':
                _, _, cls2, txt2 = items[i + 1]
                level = int(cls2[1])
                out.append('')
                out.append(f'{"#" * (level + 2)} {txt} · {txt2}')
                out.append('')
                i += 1
        elif kind == 'span' and 'practice-tag' in cls:
            out.append(f'> _Tag: {txt}_')
        elif kind == 'span' and 'insight-category' in cls:
            out.append(f'**Category:** _{txt}_  ')
        elif kind == 'span' and 'wbc-badge-icon' in cls:
            out.append(f'**{txt}**')
        elif kind == 'span' and 'years-big' in cls:
            yrs = txt
            unit = ''
            if i + 1 < len(items) and items[i + 1][1] == 'span' and 'years-text' in items[i + 1][2]:
                unit = items[i + 1][3].replace('\n', ' ')
                i += 1
            out.append(f'> **{yrs}** {unit}')
            out.append('')
        elif kind == 'p':
            for line in txt.split('\n'):
                if line.strip():
                    out.append(line.strip())
            out.append('')
        elif kind == 'address':
            for line in txt.split('\n'):
                if line.strip():
                    out.append(f'  {line.strip()}')
            out.append('')
        elif kind == 'li':
            out.append(f'- {txt}')
        elif kind == 'cta':
            out.append(f'`[CTA: {txt}]`')
            out.append('')
        i += 1

    out.append('')
    out.append('**Footer:**  ' + footer_text.replace('\n', '  ·  '))
    out.append('')
    out.append('---')
    out.append('')
    return '\n'.join(out)


def main():
    # Move to repo root if invoked from elsewhere
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    os.chdir(repo_root)

    doc = [
        '# AG Law — Copy Review',
        '',
        '_Auto-generated from the 10 HTML files. Re-run `scripts/extract-copy.py` to refresh._',
        '',
        'Every visible string on every page, in source order. Headings preserved.  ',
        '`[CTA: …]` markers are button labels.',
        '',
        '---',
        '',
    ]

    for name, path in PAGES:
        doc.append(md_for_page(name, path))

    with open('COPY-REVIEW.md', 'w') as f:
        f.write('\n'.join(doc))

    print(f'Wrote COPY-REVIEW.md ({os.path.getsize("COPY-REVIEW.md")} bytes)')


if __name__ == '__main__':
    main()
