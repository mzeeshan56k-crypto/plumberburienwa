# Burien Plumbers – plumberburienwa.com

Static site (HTML/CSS, one tiny JS file). No build step.

## Deploy on Cloudflare Pages (from GitHub)
1. Push this folder to a GitHub repo (files at the repo root).
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git → pick the repo.
3. Build settings: Framework preset **None**, Build command **(empty)**, Output directory **/**.
4. Deploy, then Custom domains → add `plumberburienwa.com` (and redirect `www`).

## Update the phone number
Find and replace `(833) 710-2588` and `+18337102588` across all files.

## Files
- `index.html` – homepage (Plumber in Burien, WA)
- `emergency-plumber/`, `drain-cleaning/`, `water-heater-repair/`, `leak-detection/`, `sewer-line-repair/`, `repiping/` – services
- `seahurst/`, `gregory-heights/`, `three-tree-point/`, `normandy-park/`, `white-center/` – areas
- `about/`, `contact/`, `404.html`
- `sitemap.xml`, `robots.txt`, `_headers`, `logo.svg`, `favicon.svg`, `og-image.png`, `styles.css`, `main.js`

After launch, submit `https://plumberburienwa.com/sitemap.xml` in Google Search Console.
