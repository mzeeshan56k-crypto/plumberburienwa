# Burien Plumbers — static site

Plain HTML/CSS with a tiny bit of JS. No build step, no dependencies.

## 1. Upload to GitHub
1. Create a new empty repository on github.com (no README).
2. Unzip `burien-plumbers-site.zip`. `index.html` must be at the top level of the folder.
3. Either drag every file and folder into the repo with **Add file → Upload files** and commit, or use the command line:
   ```
   cd burien-plumbers-site
   git init && git add . && git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
   git push -u origin main
   ```

## 2. Deploy on Vercel
1. vercel.com → **Add New → Project** → import the GitHub repo.
2. Framework preset: **Other**. Build command: leave empty. Output directory: leave empty (root).
3. Click **Deploy**.
4. **Settings → Domains** → add `plumberburienwa.com` and `www.plumberburienwa.com`, then set DNS records as Vercel shows. Make one redirect to the other (non-www is the canonical used in this site).
5. Submit `https://plumberburienwa.com/sitemap.xml` in Google Search Console.

`vercel.json` turns on clean URLs, trailing slashes, long caching for CSS/JS/SVG, and security headers.

## 3. Change the phone number
The number appears in two formats. Find and replace across all files:
- Display: `(833) 710-2588`
- Links: `tel:+18337102588`
- Schema: `+1-833-710-2588`
Also regenerate `og-image.png` (it shows the number) or replace it with your own 1200×630 image.

## 4. Change the brand name
Find and replace `Burien Plumbers` across all files. The logo text is in the header/footer markup (`Burien <b>Plumbers</b>`) and in `logo.svg`.

## 5. Change the domain
Find and replace `https://plumberburienwa.com` across all `.html` files, `sitemap.xml`, and `robots.txt`.

## 6. After editing CSS or JS
`styles.css` and `main.js` are cached for a year. After changing them, bump `?v=1` to `?v=2` in every HTML file (find and replace `?v=1`). The above-the-fold CSS is also inlined in each page's `<style>` tag; keep it in sync with the top of `styles.css`.

## 7. Analytics
Each page has an `<!-- ANALYTICS -->` comment in `<head>`. Paste your GA4/GTM snippet there. Every phone link has a `data-call` attribute, and clicks push `{event: "call_click", call_location, page_path}` to `window.dataLayer`.

## 8. Fonts and design
Headings use Sora and body text uses Figtree, loaded from Google Fonts without blocking rendering. The design notes are in `STRATEGY.md`. Shared colors are CSS variables at the top of `styles.css` (`--p50` to `--p900`, `--ac`).

## Photos
Optimized WebP photos are in `img/`. To swap one, keep the same file name and a similar shape, or update the `IMG` list in the build notes. Every image has width/height set and lazy-loads below the fold.

## 9. Required before launch
- Add your Washington L&I contractor registration number in the footer (see the `REPLACE` comment). WA law requires it on advertising.
- Confirm hours (24/7), free quotes, and pricing ranges match how you operate.
