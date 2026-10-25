"""Generate the grouped video gallery without JavaScript."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT / 'media.json').read_text())
stages = {stage['id'] for stage in json.loads((ROOT / 'wave-comparison.json').read_text())['stages']}
comparison = '''<div class="comparison">
<video controls loop muted playsinline preload="none" poster="assets/posters/wave-comparison-desktop.webp?v=2"
aria-label="Synchronized wave: SMPL, reshaped SMPL, retargeted robot, simulation, and real robot">
<source src="assets/videos/wave-comparison-mobile.mp4?v=2" media="(max-width:700px)" type="video/mp4">
<source src="assets/videos/wave-comparison-desktop.mp4?v=2" type="video/mp4">
</video></div>'''
sections = []
for category in ['Motion tracking', 'Locomotion', 'Drawing', 'Gallery']:
    videos = '\n'.join(
        f'<article><video controls playsinline preload="none" poster="{i["poster"]}" '
        f'src="{i["src"]}" aria-label="{html.escape(i["title"], quote=True)}"></video></article>'
        for i in items if i['id'] not in stages and i['category'] == category
    )
    photos = ''
    if category == 'Gallery':
        photos = ''.join(
            f'<figure><img src="assets/images/{name}.webp" alt="{alt}" loading="lazy"></figure>'
            for name, alt in [('gesture', 'Swenoid with its arms extended'),
                              ('sit', 'Swenoid sitting on a chair'),
                              ('sidesplit', 'Swenoid in a side split')]
        )
    grid_class = 'grid gallery' if category == 'Gallery' else 'grid'
    sections.append(f'<section><h2>{category}</h2>'
                    + (comparison if category == 'Motion tracking' else '')
                    + f'<div class="{grid_class}">' + photos + videos + '</div></section>')
(ROOT / 'video-index.html').write_text(
    '<!doctype html><html lang="en"><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>Swenoid — Videos</title><link rel="icon" href="assets/favicon.svg">'
    '<style>body{max-width:1100px;margin:40px auto;padding:0 24px;background:#f6f5f0;'
    'color:#202b2a;font:16px/1.6 system-ui}article{margin:0}h1,h2{line-height:1.2}'
    'section{margin-top:48px}h2{font-size:24px;font-weight:500;margin-bottom:20px}'
    'a{color:#294b43}video{display:block;width:100%;object-fit:contain;background:#e5e7df;'
    'aspect-ratio:4/3;border-radius:3px}.comparison{margin-bottom:24px}'
    '.comparison video{aspect-ratio:473/144;background:#f6f5f0}'
    '.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}'
    '.gallery{grid-template-columns:repeat(4,minmax(0,1fr))}.gallery figure{margin:0}'
    '.gallery img,.gallery video{width:100%;height:260px;object-fit:contain;background:#e5e7df}'
    '@media(max-width:1000px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}'
    '@media(max-width:700px){.grid{grid-template-columns:1fr}.comparison video{aspect-ratio:49/47}}'
    '</style><body><a href="index.html">← Back to Swenoid</a><h1>Videos</h1>'
    + '\n'.join(sections) + '</body></html>\n'
)
