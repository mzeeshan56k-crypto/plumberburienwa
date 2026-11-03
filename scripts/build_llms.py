"""Regenerate _data/llms-base.txt, llms-full.txt and _data/sitemap-pages.json from the site pages.
Run from the repo root after page content changes:  python3 scripts/build_llms.py
"""
import re, html, os
D = "https://plumberburienwa.com"
ORDER = ["", "services/", "services/emergency-plumber/", "services/drain-cleaning/", "services/water-heater-repair/",
 "services/leak-detection/", "services/sewer-line-repair/", "services/pipe-repair/", "service-areas/",
 "seatac/", "white-center/", "normandy-park/", "seahurst/", "boulevard-park/", "about/", "contact/", "privacy/", "terms/"]

def meta(s, pat):
    m = re.search(pat, s); return html.unescape(m.group(1)) if m else ""

def to_md(s):
    m = s[s.find("<main"):s.find("</main>")]
    m = re.sub(r"<(script|style|svg|noscript)[^>]*>.*?</\1>", " ", m, flags=re.S)
    m = re.sub(r"<img[^>]*>", " ", m)
    m = re.sub(r"<figcaption[^>]*>.*?</figcaption>", " ", m, flags=re.S)
    m = re.sub(r'<nav class="crumbs".*?</nav>', " ", m, flags=re.S)
    m = re.sub(r'<p class="eyebrow">.*?</p>', " ", m, flags=re.S)
    m = re.sub(r'<div class="glass.*?</div>', " ", m, flags=re.S)
    m = re.sub(r'<a class="btn[^"]*"[^>]*>.*?</a>', " ", m, flags=re.S)
    m = re.sub(r"<h1[^>]*>(.*?)</h1>", lambda x: "\n\n# " + x.group(1) + "\n\n", m, flags=re.S)
    m = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda x: "\n\n## " + x.group(1) + "\n\n", m, flags=re.S)
    m = re.sub(r"<h3[^>]*>(.*?)</h3>", lambda x: "\n\n### " + x.group(1) + "\n\n", m, flags=re.S)
    m = re.sub(r"<summary[^>]*>(.*?)</summary>", lambda x: "\n\n**Q: " + x.group(1) + "**\n\n", m, flags=re.S)
    m = re.sub(r"<(th|td)[^>]*>", " | ", m)
    m = re.sub(r"</tr>", " |\n", m)
    m = re.sub(r"<li[^>]*>", "\n- ", m)
    m = re.sub(r"</(p|ul|ol|table|div|section|details)>", "\n\n", m)
    m = re.sub(r"<br\s*/?>", "\n", m)
    m = re.sub(r"<[^>]+>", " ", m)
    m = html.unescape(m)
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in m.split("\n")]
    out, prev = [], None
    for l in lines:
        if l in ("-", "|", "| |", "See costs and signs", "Get emergency help", "24/7 emergency line"): continue
        if l.startswith("| | "): l = l[2:]
        if l == "" and prev == "": continue
        out.append(l); prev = l
    return "\n".join(out).strip()

pages = []
for p in ORDER:
    s = open(os.path.join(p, "index.html")).read()
    title = meta(s, r"<title>([^<]*)</title>")
    desc = meta(s, r'<meta name="description" content="([^"]*)"')
    pages.append((p, title, desc, to_md(s)))

# llms-full.txt
full = ["# Burien Plumbers — full site content", "",
        f"> Complete text of every page on {D}/, for AI assistants and search agents. Phone: (833) 710-2588. Open 24/7.", ""]
for p, t, d, body in pages:
    full += ["---", "", f"URL: {D}/{p}", f"Title: {t}", f"Summary: {d}", "", body, ""]
open("llms-full.txt", "w").write("\n".join(full).strip() + "\n")

# llms.txt
def link(p):
    t = next(x for x in pages if x[0] == p)
    return f"- [{t[1]}]({D}/{p}): {t[2]}"
L = f"""# Burien Plumbers

> Burien Plumbers is a local, 24/7 plumbing service for homes and small businesses in Burien, Washington (King County) and nearby communities. Call (833) 710-2588 any time; a real person answers, gives a price range on the call, and a firm written price is given before any work starts.

Key facts:
- Business: Burien Plumbers
- Website: {D}/
- Phone: (833) 710-2588 (tel:+18337102588)
- Hours: Open 24 hours a day, 7 days a week, including emergencies
- Service area: Burien, WA (ZIP 98146, 98148, 98166, 98168) plus SeaTac, White Center, Normandy Park, Seahurst and Boulevard Park
- Burien neighborhoods covered: Downtown Burien, Gregory Heights, Lake Burien, Three Tree Point, Shorewood, Manhattan, Cedarhurst, North Burien
- Services: emergency plumbing, drain cleaning and hydro jetting, water heater repair and replacement (gas, electric, tankless), leak detection, sewer line repair (camera inspection, trenchless), pipe repair and whole-house repiping
- Pricing: free quote and price range by phone; firm written price before work starts. Prices shown on the site are typical Burien-area ranges, not binding quotes.

## Main page
{link("")}

## Services
{link("services/")}
{link("services/emergency-plumber/")}
{link("services/drain-cleaning/")}
{link("services/water-heater-repair/")}
{link("services/leak-detection/")}
{link("services/sewer-line-repair/")}
{link("services/pipe-repair/")}

## Service areas
{link("service-areas/")}
{link("seatac/")}
{link("white-center/")}
{link("normandy-park/")}
{link("seahurst/")}
{link("boulevard-park/")}

## Company
{link("about/")}
{link("contact/")}

## Optional
- [Full site content]({D}/llms-full.txt): The complete text of every page in one plain-text file.
- [Sitemap]({D}/sitemap.xml): List of all pages.
- [Blog]({D}/blog/): Plumbing tips and guides for homeowners.
{link("privacy/")}
{link("terms/")}
"""
open("_data/llms-base.txt", "w").write(L)

# sitemap page list (api/blog.js renders sitemap.xml and appends live blog posts)
import json
TODAY = "2026-11-03"
PRI = {"": "1.0", "services/": "0.9", "service-areas/": "0.9"}
json.dump([{"path": "/" + p, "lastmod": TODAY, "priority": PRI.get(p, "0.3" if p in ("privacy/", "terms/") else "0.8")} for p in ORDER],
          open("_data/sitemap-pages.json", "w"), indent=1)
print(len(L), os.path.getsize("llms-full.txt"))
