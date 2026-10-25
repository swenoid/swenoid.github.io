"""Check local references and coverage of the selected media inventory."""
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = []
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

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
    assert not re.search(r'\b(paper|abstract)\b', ' '.join(parser.text), re.I), f'Publication framing in {html.name}'
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
assert {x['original'] for x in media} == (set(source['originalVideos']) - set(source['excludedVideos'])) | {item['original'] for item in source.get('additionalVideos', [])}, 'Incorrect media selection'
for item in media:
    assert item['duration'] > 0 and item['width'] > 0 and item['height'] > 0
    for field in ['src', 'poster']:
        assert (ROOT / item[field]).is_file(), f'Missing {item[field]}'
    assert (ROOT / item['src']).stat().st_size < 100 * 1024 * 1024, 'Video exceeds GitHub file limit'
comparison = json.loads((ROOT / 'wave-comparison.json').read_text())
expected_stages = ['amass-reference', 'amass-shaped', 'wave-ik', 'wave-simulation', 'wave-hardware']
assert [stage['id'] for stage in comparison['stages']] == expected_stages
assert comparison['duration'] == 3.6 and comparison['fps'] == 50
for stage in comparison['stages']:
    item = next(item for item in media if item['id'] == stage['id'])
    assert stage['source'] == item['src']
    assert stage['comparisonDuration'] == comparison['duration']
for layout in ['desktop', 'mobile']:
    path = ROOT / comparison[layout]
    assert path.is_file() and 0 < path.stat().st_size < 100 * 1024 * 1024
    assert (ROOT / f'assets/posters/wave-comparison-{layout}.webp').is_file()
assert all(not re.search(r'\b(paper|manuscript)\b', item['description'], re.I) for item in media)
print(f'Valid links, all {len(media)} source videos, and the synchronized five-stage comparison.')
