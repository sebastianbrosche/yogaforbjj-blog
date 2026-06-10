#!/usr/bin/env python3
"""
YogaForBJJ Blog Builder
Takes post data JSON and renders HTML files from template.
"""
import json, os, re, shutil
from datetime import date

BASE_DIR = os.path.expanduser("~/AppData/Local/hermes/yogaforbjj-blog")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "post.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "posts")

with open(TEMPLATE_FILE) as f:
    TEMPLATE = f.read()

def render_post(post):
    """Render a single post dict into HTML"""
    html = TEMPLATE
    
    slug = post["slug"]
    
    # Build FAQ schema
    faq_html = ""
    if "faq" in post:
        items = []
        for qa in post["faq"]:
            items.append(json.dumps({
                "@type": "Question",
                "name": qa["q"],
                "acceptedAnswer": {"@type": "Answer", "text": qa["a"]}
            }, ensure_ascii=False))
        faq_html = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{','.join(items)}]}}
</script>'''
    
    # Build content
    content_blocks = []
    for block in post["content"]:
        t = block["type"]
        if t == "h2":
            content_blocks.append(f"<h2>{block['text']}</h2>")
        elif t == "h3":
            content_blocks.append(f"<h3>{block['text']}</h3>")
        elif t == "p":
            content_blocks.append(f"<p>{block['text']}</p>")
        elif t == "blockquote":
            content_blocks.append(f"<blockquote>{block['text']}</blockquote>")
        elif t == "key-point":
            content_blocks.append(f'<div class="key-point"><h3>{block.get("title","")}</h3>{"".join(f"<p>{p}</p>" for p in block.get("points",[]))}</div>')
        elif t == "ul":
            items = "".join(f"<li>{i}</li>" for i in block["items"])
            content_blocks.append(f"<ul>{items}</ul>")
        elif t == "ol":
            items = "".join(f"<li>{i}</li>" for i in block["items"])
            content_blocks.append(f"<ol>{items}</ol>")
        elif t == "cta":
            content_blocks.append(f'<div class="cta-box"><h3>{block.get("title","Get the Full Program")}</h3><p>{block.get("text","")}</p><a href="{block.get("url","/membership")}">{block.get("button","Start Now")}</a></div>')
        elif t == "related":
            links = "".join(f"<li><a href=\"{l['url']}\">{l['title']}</a></li>" for l in block["links"])
            content_blocks.append(f'<div class="related"><h3>Read Next</h3><ul>{links}</ul></div>')
    
    content_html = "\n\n".join(content_blocks)
    
    # Replace tokens
    replacements = {
        "__TITLE__": post["title"],
        "__DESCRIPTION__": post["description"],
        "__SLUG__": slug,
        "__CATEGORY__": post["category"],
        "__DATE__": post.get("date", date.today().isoformat()),
        "__READ_TIME__": str(post.get("read_time", 8)),
        "__FAQ_SCHEMA__": faq_html,
        "__CONTENT__": content_html,
        "__LEDE__": post.get("lede", ""),
    }
    for key, val in replacements.items():
        html = html.replace(key, val)
    
    # Write file
    out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
    with open(out_path, "w") as f:
        f.write(html)
    
    print(f"✅ {slug}.html ({post['title'][:60]}...)")
    return out_path

def build_index(posts_meta):
    """Build a simple blog index page"""
    cards = []
    for p in posts_meta:
        cards.append(f'''
    <article>
      <span class="badge">{p['category']}</span>
      <h2><a href="/blog/{p['slug']}/">{p['title']}</a></h2>
      <p class="excerpt">{p['description'][:150]}...</p>
      <p class="meta">{p.get('date','')} · {p.get('read_time',8)} min read</p>
    </article>''')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <title>YogaForBJJ Blog — Mobility & Recovery for BJJ</title>
  <meta name="description" content="Expert guides on BJJ injury prevention, mobility, recovery, and longevity. Written by Sebastian Brosche — BJJ black belt, yoga teacher, and 15+ year grappler.">
  <link rel="canonical" href="https://www.yogaforbjj.net/blog/">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f0f; color: #e8e8e8; max-width: 800px; margin: 0 auto; padding: 24px; line-height: 1.6; }}
    h1 {{ font-size: 32px; margin-bottom: 8px; }}
    .subtitle {{ color: #999; margin-bottom: 48px; }}
    article {{ border-bottom: 1px solid #2a2a2a; padding: 24px 0; }}
    .badge {{ background: #e85d3a; color: #fff; font-size: 11px; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; }}
    h2 {{ font-size: 22px; margin: 8px 0; }}
    h2 a {{ color: #e8e8e8; text-decoration: none; }}
    h2 a:hover {{ color: #e85d3a; }}
    .excerpt {{ color: #999; font-size: 15px; }}
    .meta {{ color: #666; font-size: 13px; }}
    a {{ color: #e85d3a; }}
    .categories {{ margin-bottom: 32px; }}
    .categories a {{ color: #999; text-decoration: none; margin-right: 12px; font-size: 14px; }}
    .categories a:hover {{ color: #e85d3a; }}
  </style>
</head>
<body>
  <h1>YogaForBJJ Blog</h1>
  <p class="subtitle">Mobility, recovery & longevity for Brazilian Jiu-Jitsu athletes. Written by grapplers who understand what your body goes through.</p>
  
  <div class="categories">
    <a href="/blog/category/back-pain/">Lower Back Pain</a>
    <a href="/blog/category/hips/">Hip Mobility</a>
    <a href="/blog/category/knees/">Knee Health</a>
    <a href="/blog/category/injury-prevention/">Injury Prevention</a>
    <a href="/blog/category/beginners/">Beginners</a>
    <a href="/blog/category/bjj-longevity/">BJJ Longevity</a>
  </div>
  
  {''.join(cards)}
</body>
</html>'''
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(html)
    print(f"✅ index.html")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        for post in data["posts"]:
            render_post(post)
        if "posts" in data:
            posts_meta = [{"slug": p["slug"], "title": p["title"], "category": p["category"], "description": p["description"], "date": p.get("date", ""), "read_time": p.get("read_time", 8)} for p in data["posts"]]
            build_index(posts_meta)
        print(f"\n✅ Done! {len(data['posts'])} posts rendered.")
    else:
        print("Usage: build.py posts.json")
