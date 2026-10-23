"""Generate the no-JavaScript video index from media.json."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT / 'media.json').read_text())
entries = '\n'.join(
    f'<article><h2>{html.escape(i["title"])}</h2>'
    f'<p>{html.escape(i["setting"])} · {html.escape(i["category"])}</p>'
    f'<video controls playsinline preload="none" poster="{i["poster"]}" '
    f'src="{i["src"]}" style="width:100%;max-height:440px;background:#182823"></video>'
    f'<p>{html.escape(i["description"])}</p>'
    f'<p><a href="{i["src"]}" download>Download video</a></p></article>'
    for i in items
)
(ROOT / 'video-index.html').write_text(
    '<!doctype html><html lang="en"><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>Swenoid — Complete video index</title><link rel="icon" href="assets/favicon.svg">'
    '<style>body{max-width:850px;margin:40px auto;padding:0 24px;background:#f6f5f0;'
    'color:#202b2a;font:16px/1.6 system-ui}article{margin:50px 0}h1,h2{line-height:1.2}'
    'a{color:#294b43}</style><body><a href="index.html">← Back to Swenoid</a>'
    f'<h1>All {len(items)} project videos</h1>' + entries + '</body></html>\n'
)
