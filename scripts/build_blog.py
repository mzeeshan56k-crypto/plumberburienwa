#!/usr/bin/env python3
"""Build the blog from content/blog/*.md.

Writes pre-rendered post pages to _posts/<slug>.html, the blog index
template to _posts/_index.html and the schedule to _posts/manifest.json.
api/blog.js serves them and hides any post whose publish time has not
arrived yet, so posts go live on schedule without a redeploy.

Run from the repo root:  python3 scripts/build_blog.py
"""
import html
import json
import os
import re
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "blog")
OUT = os.path.join(ROOT, "_posts")
TEMPLATE = os.path.join(ROOT, "services", "drain-cleaning", "index.html")
DOMAIN = "https://plumberburienwa.com"
PHONE_ICON = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'
ARROW = '<svg class="i" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

# Publishing schedule: 10 posts a week, two each weekday at 9:00 and
# 15:00 Pacific (PST, UTC-8), starting Wednesday 4 November 2026.
START = datetime(2026, 11, 4, tzinfo=timezone.utc)
SLOTS_UTC = (17, 23)


def schedule(n):
    out, day = [], START
    while len(out) < n:
        if day.weekday() < 5:
            for h in SLOTS_UTC:
                if len(out) < n:
                    out.append(day.replace(hour=h))
        day += timedelta(days=1)
    return out


CLUSTERS = {
    "emergency": "Emergencies and Leaks",
    "drains": "Drains and Clogs",
    "sewer": "Sewer Lines",
    "water-heaters": "Water Heaters",
    "pipes": "Pipes and Water Pressure",
    "seasonal": "Seasonal Care",
    "guides": "Homeowner Guides",
}


def esc(s):
    return html.escape(s, quote=True)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    return s


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def parse(path):
    raw = open(path, encoding="utf-8").read()
    fm, body = raw.split("\n---\n", 1)
    meta = {}
    for line in fm.strip().lstrip("-").strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["body"] = body.strip()
    meta["order"] = int(os.path.basename(path).split("-", 1)[0])
    return meta


def render(md):
    """Small Markdown subset: ## / ###, paragraphs, - and 1. lists, tables."""
    blocks = re.split(r"\n\s*\n", md.strip())
    out, toc, faqs = [], [], []
    in_faq, cur_q, h2n = False, None, 0
    for b in blocks:
        lines = b.strip().splitlines()
        first = lines[0]
        if first.startswith("## "):
            text = first[3:].strip()
            h2n += 1
            hid = "faq" if text.lower().startswith("frequently asked") else f"s{h2n}"
            in_faq = hid == "faq"
            toc.append((hid, text))
            out.append(f'<h2 id="{hid}">{inline(text)}</h2>')
            rest = "\n".join(lines[1:]).strip()
            if rest:
                out.append(f"<p>{inline(rest)}</p>")
            continue
        if first.startswith("### "):
            text = first[4:].strip()
            out.append(f"<h3>{inline(text)}</h3>")
            rest = " ".join(lines[1:]).strip()
            if in_faq:
                cur_q = [text, rest]
                faqs.append(cur_q)
            if rest:
                out.append(f"<p>{inline(rest)}</p>")
            continue
        if first.startswith("|"):
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\|\s*:?-", l)]
            head, body = rows[0], rows[1:]
            t = '<div class="tw"><table><thead><tr>' + "".join(f'<th scope="col">{inline(c)}</th>' for c in head) + "</tr></thead><tbody>"
            for r in body:
                t += "<tr>" + f'<th scope="row">{inline(r[0])}</th>' + "".join(f"<td>{inline(c)}</td>" for c in r[1:]) + "</tr>"
            out.append(t + "</tbody></table></div>")
            continue
        if re.match(r"^(- |\d+\. )", first):
            tag = "ol" if re.match(r"^\d+\. ", first) else "ul"
            items, curi = [], None
            for l in lines:
                m = re.match(r"^(?:- |\d+\. )(.*)", l)
                if m:
                    items.append(m.group(1))
                else:
                    items[-1] += " " + l.strip()
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            continue
        para = " ".join(l.strip() for l in lines)
        if in_faq and cur_q is not None:
            cur_q[1] = (cur_q[1] + " " + para).strip()
        out.append(f"<p>{inline(para)}</p>")
    return "\n".join(out), toc, faqs


def words(md):
    return len(re.findall(r"[A-Za-z0-9$']+", md))


def page(tpl_head, tpl_header, tpl_footer, title, desc, canonical, ld, main, nav_current="Blog"):
    head = tpl_head
    head = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", head)
    head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*"', lambda m: m.group(1) + esc(title) + '"', head)
    head = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*"', lambda m: m.group(1) + esc(desc) + '"', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canonical}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canonical}">', head)
    head = re.sub(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="article">' if "/blog/" in canonical and canonical != DOMAIN + "/blog/" else '<meta property="og:type" content="website">', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>", head, count=1, flags=re.S)
    head = re.sub(r'<link rel="preload" as="image"[^>]*>', "", head)
    return head + tpl_header + main + tpl_footer


def main():
    tpl = open(TEMPLATE, encoding="utf-8").read().replace('"../../', '"/').replace(" ../../", " /")
    i_main, i_end = tpl.find("<main"), tpl.find("</main>") + 7
    i_body = tpl.find("<body")
    tpl_head, tpl_header, tpl_footer = tpl[:i_body], tpl[i_body:i_main], tpl[i_end:]
    tpl_header = tpl_header.replace(' aria-current="page"', "")
    if '<a href="/blog/">Blog</a>' not in tpl_header:
        tpl_header = tpl_header.replace('<a href="/about/">About</a>', '<a href="/blog/">Blog</a><a href="/about/">About</a>')
    tpl_header = tpl_header.replace('<a href="/blog/">Blog</a>', '<a href="/blog/" aria-current="page">Blog</a>', 1)
    final_cta = tpl[tpl.find('<div class="wave-top"', tpl.rfind("</section>", 0, tpl.find('<section class="cta final">'))):tpl.find("</main>")]
    final_cta = final_cta[final_cta.find('<div class="wave-top"'):]

    posts = [parse(os.path.join(SRC, f)) for f in sorted(os.listdir(SRC)) if f.endswith(".md")]
    posts.sort(key=lambda p: p["order"])
    when = schedule(len(posts))
    slugs = {p["slug"] for p in posts}
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    problems = []
    for p, at in zip(posts, when):
        p["publishAt"] = at.strftime("%Y-%m-%dT%H:%M:%SZ")
        body_html, toc, faqs = render(p["body"])
        links = re.findall(r'href="(/[^"]*)"', body_html)
        blog_links = [l for l in links if l.startswith("/blog/")]
        for l in blog_links:
            if l.strip("/").split("/")[-1] not in slugs:
                problems.append(f"{p['slug']}: broken link {l}")
        if links.count("/") != 1:
            problems.append(f"{p['slug']}: homepage links = {links.count('/')}")
        if not 3 <= len(set(blog_links)) <= 4:
            problems.append(f"{p['slug']}: blog links = {len(set(blog_links))}")
        if len(p["title"]) >= 60 or len(p["description"]) >= 150:
            problems.append(f"{p['slug']}: title {len(p['title'])} / desc {len(p['description'])}")
        wc = words(p["body"])
        mins = max(3, round(wc / 220))
        url = f"{DOMAIN}/blog/{p['slug']}/"
        date_h = at.astimezone(timezone(timedelta(hours=-8))).strftime("%B %-d, %Y")
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "BlogPosting", "@id": url + "#article", "headline": p["h1"], "description": p["description"],
             "datePublished": p["publishAt"], "dateModified": p["publishAt"], "inLanguage": "en-US",
             "mainEntityOfPage": url, "wordCount": wc, "articleSection": CLUSTERS[p["cluster"]],
             "about": p["keyword"], "image": DOMAIN + "/og-image.png",
             "author": {"@type": "Organization", "name": "Burien Plumbers", "url": DOMAIN + "/"},
             "publisher": {"@type": "Organization", "name": "Burien Plumbers", "url": DOMAIN + "/", "logo": {"@type": "ImageObject", "url": DOMAIN + "/logo.svg"}},
             "spatialCoverage": {"@type": "City", "name": "Burien", "containedInPlace": {"@type": "AdministrativeArea", "name": "King County, Washington"}}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": DOMAIN + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url}]}]}
        if faqs:
            ld["@graph"].append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", a)}} for q, a in faqs]})
        toc_html = "".join(f'<li><a href="#{i}">{inline(t)}</a></li>' for i, t in toc)
        hero = (f'<section class="hero hero-text"><div class="wrap hero-grid"><div><nav class="crumbs" aria-label="Breadcrumb"><ol>'
                f'<li><a href="/">Home</a></li><li><a href="/blog/">Blog</a></li><li aria-current="page">{esc(p["h1"])}</li></ol></nav>'
                f'<h1>{esc(p["h1"])}</h1><p class="lead">{inline(p["lead"])}</p>'
                f'<p class="post-meta"><span>{CLUSTERS[p["cluster"]]}</span> &middot; <time datetime="{p["publishAt"]}">{date_h}</time> &middot; {mins} min read</p>'
                f'<div class="hero-cta"><a class="btn btn-ac" href="tel:+18337102588" data-call="hero">{PHONE_ICON}<span>Call (833) 710-2588</span></a></div></div></div></section>')
        side = (f'<aside class="side" aria-label="Page tools"><div class="side-in"><nav class="toc" aria-label="On this page"><p class="eyebrow">On this page</p><ol class="toc-l">{toc_html}</ol></nav>'
                f'<div class="callcard"><p class="eyebrow">Call now, 24/7</p><a class="num" href="tel:+18337102588" data-call="sidebar-number">(833) 710-2588</a><p>Free price range on the phone. Firm price before work starts.</p>'
                f'<a class="btn btn-ac" href="tel:+18337102588" data-call="sidebar">{PHONE_ICON}<span>Call for a Free Quote</span></a></div></div></aside>')
        article = (f'<div class="doc"><div class="wrap doc-grid"><div class="doc-main"><article class="panel prose post bg-white">{body_html}</article></div>{side}</div></div>')
        main_html = f'<main id="main">{hero}{article}{final_cta}</main>'
        open(os.path.join(OUT, p["slug"] + ".html"), "w", encoding="utf-8").write(
            page(tpl_head, tpl_header, tpl_footer, p["title"], p["description"], url, ld, main_html))
        manifest.append({"slug": p["slug"], "h1": p["h1"], "title": p["title"], "description": p["description"],
                         "cluster": p["cluster"], "clusterName": CLUSTERS[p["cluster"]], "publishAt": p["publishAt"],
                         "date": date_h, "minutes": mins, "words": wc})

    # Blog index template; api/blog.js fills <!--POSTS--> with published posts.
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": DOMAIN + "/blog/#blog", "name": "Plumbing Tips and Guides", "url": DOMAIN + "/blog/", "inLanguage": "en-US"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": DOMAIN + "/blog/"}]}]}
    hero = ('<section class="hero hero-text"><div class="wrap hero-grid"><div><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">Blog</li></ol></nav>'
            '<h1>Plumbing <span class="hl">Tips and Guides</span></h1><p class="lead">Practical answers for homeowners in Burien and nearby towns: leaks, drains, sewer lines, water heaters, pipes, costs, and seasonal care.</p></div></div></section>')
    body = '<section class="sec bg-white"><div class="wrap"><!--POSTS--></div></section>'
    open(os.path.join(OUT, "_index.html"), "w", encoding="utf-8").write(
        page(tpl_head, tpl_header, tpl_footer, "Plumbing Tips and Guides | Homeowner Blog",
             "Plumbing advice for Burien area homeowners: leaks, clogs, sewer lines, water heaters, repiping, costs and seasonal care.",
             DOMAIN + "/blog/", ld, f'<main id="main">{hero}{body}{final_cta}</main>'))
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"built {len(manifest)} posts; first {manifest[0]['publishAt']} last {manifest[-1]['publishAt']}")
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
