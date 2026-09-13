#!/usr/bin/env python3
"""Strip em/en dashes from live blog HTML and inject related-reading blocks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RELATED = {
    "how-to-warm-up-bjj.html": [
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
    ],
    "bjj-recovery.html": [
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
    ],
    "complete-bjj-injury-prevention.html": [
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
        ("/bjj-bad-knees.html", "BJJ with bad knees"),
    ],
    "secrets-to-bjj-flexibility.html": [
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/how-to-warm-up-bjj.html", "How to warm up for BJJ"),
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
    ],
    "bjj-bad-knees.html": [
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
    ],
    "can-blue-belt-teach-bjj.html": [
        ("/how-to-teach-mobility.html", "How to teach mobility"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
    ],
    "is-yoga-good-for-martial-arts.html": [
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/how-to-teach-mobility.html", "How to teach mobility"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
    ],
    "lower-back-pain-bjj.html": [
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
    ],
    "how-often-train-bjj.html": [
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
    ],
    "about.html": [
        ("/do-bjj-for-life.html", "Do BJJ for Life"),
        ("/mobility-for-bjj.html", "Mobility for BJJ"),
        ("/stretching-for-jiu-jitsu.html", "Stretching for jiu jitsu"),
        ("/why-you-keep-getting-injured-bjj.html", "Why you keep getting injured"),
        ("/bjj-recovery-blueprint.html", "The recovery blueprint"),
    ],
}


def strip_dashes(text: str) -> str:
    text = text.replace("\u2014", ": ").replace("\u2013", "-")
    text = text.replace("Get it free:  20 min class", "Get it free (20 min class)")
    text = text.replace("Get it free: 20 min class", "Get it free (20 min class)")
    text = text.replace("Sebastian Brosche:  BJJ Black Belt", "Sebastian Brosche. BJJ black belt")
    text = text.replace("Sebastian Brosche: BJJ Black Belt", "Sebastian Brosche. BJJ black belt")
    text = re.sub(r":\s+:", ":", text)
    return text


def related_html(pairs: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{href}">{title}</a></li>' for href, title in pairs)
    return f'<div class="related"><h3>Keep reading</h3><ul>{items}</ul></div>\n'


def main() -> None:
    n = 0
    for path in ROOT.glob("*.html"):
        raw = path.read_text(encoding="utf-8")
        text = strip_dashes(raw)
        name = path.name
        if name in RELATED and 'class="related"' not in text:
            block = related_html(RELATED[name])
            if '<div class="lead-magnet">' in text:
                text = text.replace('<div class="lead-magnet">', block + '<div class="lead-magnet">', 1)
            elif "</article>" in text:
                text = text.replace("</article>", block + "</article>", 1)
        if name == "secrets-to-bjj-flexibility.html":
            text = text.replace(
                "Three big ones. One: stretching cold.",
                "The usual mistakes. First: stretching cold.",
            )
            text = text.replace("Two: bouncing.", "Then bouncing.")
            text = text.replace("Three: stretching the wrong area.", "Also stretching the wrong area.")
        if text != raw:
            path.write_text(text, encoding="utf-8")
            n += 1
            print("fixed", name)
    print("files", n)


if __name__ == "__main__":
    main()
