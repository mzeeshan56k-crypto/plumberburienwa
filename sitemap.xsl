<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="robots" content="noindex,follow"/>
<title>Sitemap | plumberburienwa.com</title>
<style>
body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;color:#0f1c30;background:#f7f8fb}
header{background:#0b2341;color:#fff;padding:32px 20px}
header div,main{max-width:960px;margin:0 auto}
h1{margin:0 0 6px;font-size:1.6rem}
header p{margin:0;color:#c9d5e6}
header a{color:#ff8a99}
main{padding:24px 20px 48px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dde3ec;border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:12px 14px;border-bottom:1px solid #dde3ec}
th{background:#eef3fa;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;color:#193a6c}
td a{color:#193a6c;text-decoration:none;word-break:break-all}
td a:hover{color:#c8102e;text-decoration:underline}
td.n{color:#4a5a70;white-space:nowrap;width:1%}
tr:last-child td{border-bottom:0}
</style>
</head>
<body>
<header><div>
<h1>Sitemap</h1>
<p><xsl:value-of select="count(s:urlset/s:url)"/> pages on plumberburienwa.com &#183; <a href="/">Back to homepage</a> &#183; <a href="/llms.txt">llms.txt</a></p>
</div></header>
<main>
<table>
<tr><th>#</th><th>Page URL</th><th>Last updated</th><th>Priority</th></tr>
<xsl:for-each select="s:urlset/s:url">
<tr>
<td class="n"><xsl:value-of select="position()"/></td>
<td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
<td class="n"><xsl:value-of select="s:lastmod"/></td>
<td class="n"><xsl:value-of select="s:priority"/></td>
</tr>
</xsl:for-each>
</table>
</main>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
