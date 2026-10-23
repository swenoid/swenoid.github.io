"""Check local references and complete coverage of the original media inventory."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ['src', 'href', 'poster']:
            if attrs.get(key):
                self.refs.append(attrs[key])


for html in ROOT.glob('*.html'):
    parser = References()
    parser.feed(html.read_text())
    assert len(parser.ids) == len(set(parser.ids)), f'Duplicate HTML IDs in {html.name}'
    for ref in parser.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        if url.path:
            assert (ROOT / unquote(url.path)).is_file(), f'Missing {ref} in {html.name}'
        elif url.fragment:
            assert url.fragment in parser.ids, f'Missing anchor {ref}'

media = json.loads((ROOT / 'media.json').read_text())
source = json.loads((ROOT / 'media-provenance.json').read_text())
assert len({x['id'] for x in media}) == len(media), 'Duplicate video IDs'
assert {x['original'] for x in media} == set(source['originalVideos']), 'Incomplete media inventory'
for item in media:
    assert item['duration'] > 0 and item['width'] > 0 and item['height'] > 0
    for field in ['src', 'poster']:
        assert (ROOT / item[field]).is_file(), f'Missing {item[field]}'
    assert (ROOT / item['src']).stat().st_size < 100 * 1024 * 1024, 'Video exceeds GitHub file limit'
print(f'Valid local links, anchors, posters, and all {len(media)} original videos.')
