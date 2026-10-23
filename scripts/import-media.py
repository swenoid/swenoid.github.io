"""Import a read-only copy of the personal site's media into this website.

Usage: python3 scripts/import-media.py /path/to/personal-site-snapshot
Requires ffmpeg, ffprobe, and cwebp. No originals are modified.
"""

import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]).resolve()
ITEMS = json.loads((ROOT / 'media.json').read_text())
TEMP = ROOT / '.local' / 'import'
TEMP.mkdir(parents=True, exist_ok=True)


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def convert(item):
    source = SOURCE / 'content' / item['original']
    output = ROOT / 'assets/videos' / (item['id'] + '.mp4')
    poster = ROOT / 'assets/posters' / (item['id'] + '.webp')
    if not output.is_file():
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(source),
         '-map', '0:v:0', '-map', '0:a?', '-map_metadata', '-1',
         '-vf', "scale=w='min(1440,iw)':h='min(1080,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2,format=yuv420p",
         '-c:v', 'libx264', '-crf', '23', '-preset', 'fast', '-threads', '3',
         '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(output)])
    temp_poster = TEMP / (item['id'] + '.png')
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', str(output),
         '-frames:v', '1', '-vf', 'scale=960:-2', str(temp_poster)])
    run(['cwebp', '-quiet', '-q', '85', str(temp_poster), '-o', str(poster)])
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height',
        '-of', 'json', str(output)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    item.update(duration=float(probe['format']['duration']), width=video['width'],
                height=video['height'], src='assets/videos/' + output.name,
                poster='assets/posters/' + poster.name,
                originalSha256=hashlib.sha256(source.read_bytes()).hexdigest())
    print('Imported ' + item['original'], flush=True)
    return item


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    converted = list(pool.map(convert, ITEMS))
(ROOT / 'media.json').write_text(json.dumps(converted, indent=2) + '\n')

for name in ['attachments.png', 'gesture.jpg', 'split.jpg', 'sidesplit.jpg', 'sit.jpg']:
    run(['cwebp', '-quiet', '-q', '88', '-resize', '1400', '0',
         str(SOURCE / 'content' / name), '-o', str(ROOT / 'assets/images' / (Path(name).stem + '.webp'))])
print('All media imported.', flush=True)
