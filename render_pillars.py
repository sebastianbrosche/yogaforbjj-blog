#!/usr/bin/env python3
"""Render ebook pillar markdown into live blog.yogaforbjj.net HTML chrome."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_DIR = Path(r"C:\Users\Admin\claudecode\yogaforbjj\content\pillars")
OUT_DIR = ROOT

PILLARS = [
    ("stretching-for-jiu-jitsu.md", "12 min read", "2026-09-13",
     "https://network.yogaforbjj.net/pears-ebook", "Get the free recovery ebook"),
    ("mobility-for-bjj.md", "11 min read", "2026-09-13",
     "https://network.yogaforbjj.net/injury-ebook", "Get the free injury ebook"),
    ("do-bjj-for-life.md", "14 min read", "2026-09-13",
     "https://network.yogaforbjj.net/bjj4life", "Get Do BJJ for Life free"),
    ("why-you-keep-getting-injured-bjj.md", "14 min read", "2026-09-13",
     "https://network.yogaforbjj.net/injury-ebook", "Get the free injury ebook"),
    ("bjj-recovery-blueprint.md", "12 min read", "2026-09-13",
     "https://network.yogaforbjj.net/pears-ebook", "Get the PEARS recovery ebook"),
    ("how-to-teach-mobility.md", "10 min read", "2026-09-13",
     "https://network.yogaforbjj.net/yoga-coach", "Get the Yoga Coach ebook"),
]


def parse_front(md: str) -> tuple[dict, str]:
    meta = {}
    if md.startswith("---"):
        _, block, body = md.split("---", 2)
        for line in block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        return meta, body.strip()
    return {}, md


def embed_iframe(guid: str) -> str:
    src = f"https://iframe.mediadelivery.net/embed/215008/{guid}"
    return (
        f'<div class="video-embed"><iframe src="{src}" '
        f'title="Yoga for BJJ follow-along" frameborder="0" allowfullscreen '
        f'loading="lazy"></iframe></div>'
    )


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render_body(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m_emb = re.match(r"\[EMBED:.*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\]", line)
        if m_emb:
            out.append(embed_iframe(m_emb.group(1)))
            i += 1
            continue
        if line.startswith("# "):
            i += 1
            continue
        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:].strip())}</h3>")
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| ]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                rows.append(cells)
                i += 1
            header, body_rows = rows[0], rows[2:]
            thead = "".join(f"<th>{inline(c)}</th>" for c in header)
            tbody = ""
            for r in body_rows:
                tbody += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:].strip())}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                item_text = re.sub(r"^\d+\. ", "", lines[i]).strip()
                items.append(f"<li>{inline(item_text)}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if line.startswith("## FACT") or line.startswith("| Claim"):
            break
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("|") and not lines[i].startswith("- ") and not re.match(r"^\d+\. ", lines[i]) and not lines[i].startswith("[EMBED"):
            para.append(lines[i])
            i += 1
        text = " ".join(p.strip() for p in para)
        if text.startswith("## References") or text.startswith("## FACT"):
            break
        out.append(f"<p>{inline(text)}</p>")
    return "\n\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Yoga for BJJ</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="canonical" href="https://blog.yogaforbjj.net/{slug}.html" />
    <meta property="og:title" content="{title} | Yoga for BJJ" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="https://blog.yogaforbjj.net/{slug}.html" />
    <meta property="og:type" content="article" />
    <meta name="twitter:card" content="summary" />
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": {title_json},
      "description": {desc_json},
      "author": {{"@type": "Person", "name": "Sebastian Brosche"}},
      "publisher": {{"@type": "Organization", "name": "Yoga for BJJ", "url": "https://www.yogaforbjj.net"}},
      "datePublished": "{date}",
      "dateModified": "{date}",
      "url": "https://blog.yogaforbjj.net/{slug}.html"
    }}
    </script>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a href="/" class="logo">Yoga for BJJ</a>
            <nav>
                <a href="/">Articles</a>
                <a href="https://yogaforbjj.net">Programs</a>
                <a href="/about.html">About</a>
            </nav>
        </div>
    </header>
    <main>
<article class="post">
    <div class="container narrow">
        <header class="post-header">
            <h1>{title}</h1>
            <div class="post-meta">
                <span class="author">Sebastian Brosche</span>
                <span class="date">{date}</span>
                <span class="read-time">{read_time}</span>
            </div>
        </header>
        <div class="post-content">
{body}
        </div>
        <div class="lead-magnet">
            <h3>Free ebook for this topic</h3>
            <p>Read it on your phone. No popup. One email.</p>
            <a href="{magnet}" class="btn-primary">{magnet_label}</a>
        </div>
        <div class="post-footer">
            <div class="author-box">
                <img src="/images/sebastian.jpg" alt="Sebastian Brosche" class="author-img">
                <div>
                    <h4>Sebastian Brosche</h4>
                    <p>BJJ black belt. Judo black belt. 500hr yoga teacher. I help grapplers move better, hurt less, and train for decades.</p>
                </div>
            </div>
        </div>
    </div>
</article>
    </main>
    <footer class="site-footer">
        <div class="container">
            <p>Sebastian Brosche. BJJ black belt. Helping grapplers move better and train longer.</p>
        </div>
    </footer>
</body>
</html>
"""


def main() -> None:
    import json
    cards = []
    for name, read_time, date, magnet, magnet_label in PILLARS:
        path = MD_DIR / name
        meta, body = parse_front(path.read_text(encoding="utf-8"))
        title = meta.get("title", "").strip('"')
        slug = meta.get("slug") or path.stem
        desc = meta.get("title", title)
        # Prefer a short description from first paragraph if present
        description = {
            "stretching-for-jiu-jitsu": "Generic gym stretching does not prepare you for BJJ. Here is stretching for jiu jitsu that maps to guard, passing, and recovery, with follow-along video.",
            "mobility-for-bjj": "Mobility for BJJ is owning a range under load, not being bendy. A 10-minute grappler routine plus the off-mat rule.",
            "do-bjj-for-life": "Ten principles from the Do BJJ for Life ebook: tap, control over speed, warm-up, recovery, tribe. Stay on the mat.",
            "why-you-keep-getting-injured-bjj": "Ten fixable reasons you keep getting hurt in BJJ, from the injuries ebook. Warm-ups, ego, recovery, gym culture.",
            "bjj-recovery-blueprint": "PEARS recovery for hobbyists who train like athletes: sleep, active recovery, nutrition, and the hour after class.",
            "how-to-teach-mobility": "Ten teaching tips from the Yoga Coach ebook for running mobility classes athletes will actually attend.",
        }[slug]
        html_body = render_body(body)
        page = TEMPLATE.format(
            title=html.escape(title),
            description=html.escape(description),
            slug=slug,
            date=date,
            read_time=read_time,
            body=html_body,
            magnet=magnet,
            magnet_label=html.escape(magnet_label),
            title_json=json.dumps(title),
            desc_json=json.dumps(description),
        )
        out = OUT_DIR / f"{slug}.html"
        out.write_text(page, encoding="utf-8")
        print("wrote", out.name)
        cards.append((slug, title, description, date, read_time))

    index = (OUT_DIR / "index.html").read_text(encoding="utf-8")
    # Insert new cards after posts-grid opening tag
    card_html = ""
    for slug, title, description, date, read_time in cards:
        card_html += (
            f'<a href="/{slug}.html" class="post-card"><h2>{html.escape(title)}</h2>'
            f'<p class="excerpt">{html.escape(description)}</p>'
            f'<div class="meta">{date} · {read_time}</div></a>'
        )
    if "<!-- PILLARS -->" not in index:
        index = index.replace(
            '<div class="posts-grid">',
            '<div class="posts-grid"><!-- PILLARS -->' + card_html,
            1,
        )
    else:
        index = re.sub(
            r"<!-- PILLARS -->.*?(?=<a href=\"/complete-bjj-injury-prevention)",
            "<!-- PILLARS -->" + card_html,
            index,
            count=1,
            flags=re.S,
        )
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    print("updated index.html")


if __name__ == "__main__":
    main()
