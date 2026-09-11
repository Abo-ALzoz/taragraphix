"""Create gallery display derivatives and compatible reels; never overwrite originals."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_streams', '-show_format', '-of', 'json', str(path)]))

def main():
    gallery = ROOT / 'media/gallery'
    gallery.mkdir(exist_ok=True)
    rows = []
    for source in sorted((ROOT / 'images').glob('image*.g*.png')):
        stream = probe(source)['streams'][0]
        widths = sorted(set([min(stream['width'], w) for w in (360, 720, 1440)]))
        row = {'source': str(source.relative_to(ROOT)), 'original_bytes': source.stat().st_size,
               'width': stream['width'], 'height': stream['height'], 'variants': []}
        for width in widths:
            stem = gallery / (source.stem + '-' + str(width))
            webp, avif = Path(str(stem) + '.webp'), Path(str(stem) + '.avif')
            run(['cwebp', '-quiet', '-q', '90', '-m', '6', '-sharp_yuv', '-resize', str(width), '0', str(source), '-o', str(webp)])
            run(['ffmpeg', '-y', '-v', 'error', '-i', str(source), '-vf', f'scale={width}:-1:flags=lanczos', '-frames:v', '1',
                 '-c:v', 'libsvtav1', '-crf', '20', '-preset', '6', '-svtav1-params', 'lp=2', '-pix_fmt', 'yuv420p10le', str(avif)])
            for path in (webp, avif):
                row['variants'].append({'path': str(path.relative_to(ROOT)), 'width': width, 'bytes': path.stat().st_size})
        rows.append(row)
    videos = []
    for source in sorted((ROOT / 'media/videos').glob('reel[123].mp4')):
        target = source.with_name(source.stem + '-display.mp4')
        run(['ffmpeg', '-y', '-v', 'error', '-i', str(source), '-map', '0:v:0', '-map', '0:a?',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(target)])
        videos.append({'source': str(source.relative_to(ROOT)), 'path': str(target.relative_to(ROOT)),
                       'before': source.stat().st_size, 'after': target.stat().st_size, 'probe': probe(target)})
    (ROOT / 'tools/media-display-manifest.json').write_text(json.dumps({'gallery': rows, 'videos': videos}, indent=2) + '\n')
    print('Created', sum(len(row['variants']) for row in rows), 'gallery variants and', len(videos), 'reels.')

if __name__ == '__main__':
    main()
