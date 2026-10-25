"""Make a single-clock, five-stage wave comparison for desktop and mobile."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.local/wave-build'
WORK.mkdir(parents=True, exist_ok=True)
MEDIA = {item['id']: item for item in json.loads((ROOT/'media.json').read_text())}
STAGES = [
    ('amass-reference', 'SMPL'),
    ('amass-shaped', 'Reshaped SMPL'),
    ('wave-ik', 'Retargeted robot'),
    ('wave-simulation', 'Simulation'),
    ('wave-hardware', 'Real robot'),
]
DURATION, FPS = 3.6, 50
PANEL_HEIGHT, GAP, CONTROL_SPACE = 528, 24, 48

def run(args):
    subprocess.run(args, check=True, cwd=ROOT)

def prepare(entry):
    key, title = entry
    source = ROOT / MEDIA[key]['src']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=duration,r_frame_rate', '-of', 'json', str(source)]))
    source_duration = float(probe['streams'][0]['duration'])
    width = round(MEDIA[key]['width'] * PANEL_HEIGHT / MEDIA[key]['height'] / 2) * 2
    filters = (
        f'[0:v]setpts=(PTS-STARTPTS)*{DURATION/source_duration:.10f},fps={FPS},'
        f'scale={width}:{PANEL_HEIGHT},setsar=1,'
        f'tpad=stop_mode=clone:stop_duration=0.1,trim=duration={DURATION}[out]'
    )
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source),
         '-filter_complex', filters, '-map', '[out]',
         '-t', str(DURATION), '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-threads', '2', '-pix_fmt', 'yuv420p', str(WORK/f'{key}.mp4')])
    return {'id': key, 'title': title, 'source': MEDIA[key]['src'],
            'sourceDuration': source_duration, 'comparisonDuration': DURATION,
            'playbackRate': source_duration/DURATION, 'width': width, 'height': PANEL_HEIGHT}

with ThreadPoolExecutor(max_workers=3) as pool:
    stages = list(pool.map(prepare, STAGES))

layouts = {}
for layout in ['desktop', 'mobile']:
    rows = [stages] if layout == 'desktop' else [stages[:3], stages[3:]]
    row_widths = [sum(stage['width'] for stage in row) + GAP * (len(row)-1) for row in rows]
    canvas_width = max(row_widths)
    panels = []
    for row_index, (row, row_width) in enumerate(zip(rows, row_widths)):
        x = (canvas_width - row_width) // 2
        y = row_index * (PANEL_HEIGHT + GAP)
        for stage in row:
            panels.append({'id': stage['id'], 'x': x, 'y': y, 'width': stage['width'], 'height': PANEL_HEIGHT})
            x += stage['width'] + GAP
    positions = '|'.join(f"{panel['x']}_{panel['y']}" for panel in panels)
    layouts[layout] = {'width': canvas_width, 'height': len(rows) * PANEL_HEIGHT + (len(rows)-1) * GAP + CONTROL_SPACE, 'gap': GAP, 'panels': panels}
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for key, _ in STAGES:
        args += ['-i', str(WORK/f'{key}.mp4')]
    output = ROOT/f'assets/videos/wave-comparison-{layout}.mp4'
    args += ['-filter_complex', f'[0:v][1:v][2:v][3:v][4:v]xstack=inputs=5:layout={positions}:fill=0xf6f5f0:shortest=1,pad=iw:ih+{CONTROL_SPACE}:0:0:color=0xf6f5f0[out]',
             '-map', '[out]', '-an', '-t', str(DURATION), '-c:v', 'libx264', '-crf', '20',
             '-preset', 'medium', '-threads', '4', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    run(args)
    still = WORK/f'{layout}-poster.png'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '0.65', '-i', str(output),
         '-frames:v', '1', str(still)])
    run(['magick', str(still), '-quality', '85', str(ROOT/f'assets/posters/wave-comparison-{layout}.webp')])

(ROOT/'wave-comparison.json').write_text(json.dumps({
    'duration': DURATION, 'fps': FPS, 'stages': stages, 'layouts': layouts,
    'alignment': 'All five recordings start together and are uniformly retimed to the same 3.6-second wave cycle. No frames are reordered; motion differences are retained.',
    'desktop': 'assets/videos/wave-comparison-desktop.mp4',
    'mobile': 'assets/videos/wave-comparison-mobile.mp4',
}, indent=2)+'\n')
print('Built desktop and mobile wave comparisons; originals unchanged.')
