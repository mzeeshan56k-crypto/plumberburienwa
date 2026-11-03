// Serves the blog, sitemap.xml and llms.txt.
// Posts are pre-built into _posts/ by scripts/build_blog.py. A post is only
// shown once its publishAt time has passed, so the weekly schedule runs
// without redeploying. Links to posts that are not live yet render as text.
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DOMAIN = "https://plumberburienwa.com";
const read = (...p) => fs.readFileSync(path.join(ROOT, ...p), "utf8");
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function published(now) {
  const all = JSON.parse(read("_posts", "manifest.json"));
  return all.filter((p) => Date.parse(p.publishAt) <= now);
}

function unlinkUnpublished(html, live) {
  return html.replace(/<a href="\/blog\/([a-z0-9-]+)\/">(.*?)<\/a>/g, (m, slug, text) => (live.has(slug) ? m : text));
}

function send(res, status, type, body, maxAge = 600) {
  res.statusCode = status;
  res.setHeader("Content-Type", type);
  res.setHeader("Cache-Control", `public, max-age=0, s-maxage=${maxAge}, stale-while-revalidate=60`);
  res.end(body);
}

function notFound(res) {
  let page = "<h1>Page not found</h1>";
  try { page = read("404.html"); } catch (e) {}
  send(res, 404, "text/html; charset=utf-8", page, 300);
}

function card(p) {
  return `<li class="post-card"><a href="/blog/${p.slug}/"><span class="pc-tag">${esc(p.clusterName)}</span><b>${esc(p.h1)}</b><span class="pc-desc">${esc(p.description)}</span><span class="pc-meta">${esc(p.date)} &middot; ${p.minutes} min read</span></a></li>`;
}

module.exports = (req, res) => {
  const url = new URL(req.url, DOMAIN);
  const now = Date.now();
  const live = published(now);
  const liveSet = new Set(live.map((p) => p.slug));
  const kind = url.searchParams.get("kind");

  if (kind === "post") {
    const slug = (url.searchParams.get("slug") || "").replace(/\/+$/, "");
    if (!/^[a-z0-9-]+$/.test(slug) || !liveSet.has(slug)) return notFound(res);
    return send(res, 200, "text/html; charset=utf-8", unlinkUnpublished(read("_posts", slug + ".html"), liveSet));
  }

  if (kind === "index") {
    const list = live.slice().sort((a, b) => b.publishAt.localeCompare(a.publishAt));
    const inner = list.length
      ? `<ul class="post-grid">${list.map(card).join("")}</ul>`
      : `<p class="ans">New articles are on the way. In the meantime, call (833) 710-2588 with any plumbing question.</p>`;
    return send(res, 200, "text/html; charset=utf-8", read("_posts", "_index.html").replace("<!--POSTS-->", inner));
  }

  if (kind === "sitemap") {
    const pages = JSON.parse(read("_data", "sitemap-pages.json"));
    const rows = pages.map((p) => `  <url><loc>${DOMAIN}${p.path}</loc><lastmod>${p.lastmod}</lastmod><priority>${p.priority}</priority></url>`);
    if (live.length) {
      const newest = live.map((p) => p.publishAt.slice(0, 10)).sort().pop();
      rows.push(`  <url><loc>${DOMAIN}/blog/</loc><lastmod>${newest}</lastmod><priority>0.7</priority></url>`);
      for (const p of live) rows.push(`  <url><loc>${DOMAIN}/blog/${p.slug}/</loc><lastmod>${p.publishAt.slice(0, 10)}</lastmod><priority>0.6</priority></url>`);
    }
    const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${rows.join("\n")}\n</urlset>\n`;
    return send(res, 200, "application/xml; charset=utf-8", xml);
  }

  if (kind === "llms") {
    let txt = read("_data", "llms-base.txt").trimEnd() + "\n";
    if (live.length) {
      txt += `\n## Blog\n- [Plumbing Tips and Guides](${DOMAIN}/blog/): Homeowner articles on leaks, drains, sewer lines, water heaters, pipes, costs and seasonal care.\n`;
      for (const p of live) txt += `- [${p.h1}](${DOMAIN}/blog/${p.slug}/): ${p.description}\n`;
    }
    return send(res, 200, "text/plain; charset=utf-8", txt);
  }

  return notFound(res);
};
