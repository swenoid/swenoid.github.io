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

def run(args):
    subprocess.run(args, check=True, cwd=ROOT)

def prepare(entry):
    key, title = entry
    source = ROOT / MEDIA[key]['src']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=duration,r_frame_rate', '-of', 'json', str(source)]))
    source_duration = float(probe['streams'][0]['duration'])
    filters = (
        f'[0:v]setpts=(PTS-STARTPTS)*{DURATION/source_duration:.10f},fps={FPS},'
        'scale=384:528:force_original_aspect_ratio=decrease,'
        'pad=384:528:(ow-iw)/2:(oh-ih)/2:color=0xf6f5f0,setsar=1,'
        f'tpad=stop_mode=clone:stop_duration=0.1,trim=duration={DURATION}[out]'
    )
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source),
         '-filter_complex', filters, '-map', '[out]',
         '-t', str(DURATION), '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-threads', '2', '-pix_fmt', 'yuv420p', str(WORK/f'{key}.mp4')])
    return {'id': key, 'title': title, 'source': MEDIA[key]['src'],
            'sourceDuration': source_duration, 'comparisonDuration': DURATION,
            'playbackRate': source_duration/DURATION}

with ThreadPoolExecutor(max_workers=3) as pool:
    stages = list(pool.map(prepare, STAGES))

for layout, positions in [('desktop', '0_0|384_0|768_0|1152_0|1536_0'),
                          ('mobile', '0_0|384_0|768_0|192_528|576_528')]:
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for key, _ in STAGES:
        args += ['-i', str(WORK/f'{key}.mp4')]
    output = ROOT/f'assets/videos/wave-comparison-{layout}.mp4'
    args += ['-filter_complex', f'[0:v][1:v][2:v][3:v][4:v]xstack=inputs=5:layout={positions}:fill=0xf6f5f0:shortest=1,pad=iw:ih+48:0:0:color=0xf6f5f0[out]',
             '-map', '[out]', '-an', '-t', str(DURATION), '-c:v', 'libx264', '-crf', '20',
             '-preset', 'medium', '-threads', '4', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    run(args)
    still = WORK/f'{layout}-poster.png'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '0.65', '-i', str(output),
         '-frames:v', '1', str(still)])
    run(['magick', str(still), '-quality', '85', str(ROOT/f'assets/posters/wave-comparison-{layout}.webp')])

(ROOT/'wave-comparison.json').write_text(json.dumps({
    'duration': DURATION, 'fps': FPS, 'stages': stages,
    'alignment': 'All five recordings start together and are uniformly retimed to the same 3.6-second wave cycle. No frames are reordered; motion differences are retained.',
    'desktop': 'assets/videos/wave-comparison-desktop.mp4',
    'mobile': 'assets/videos/wave-comparison-mobile.mp4',
}, indent=2)+'\n')
print('Built desktop and mobile wave comparisons; originals unchanged.')
