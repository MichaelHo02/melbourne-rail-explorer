"""Usage: python3 scripts/pov-contact-sheet.py artifacts/pov-survey/RUN

Requires Pillow. Arranges captures without changing the original evidence.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

folder = Path(sys.argv[1])
files = sorted(p for p in folder.glob('*.png') if p.stem.isdigit())
if not files:
    raise SystemExit('No distance-labelled PNG captures found')
sheet = Image.new('RGB', (1280, ((len(files) + 3) // 4) * 204), '#17212b')
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(files):
    with Image.open(path) as original:
        preview = original.copy()
        preview.thumbnail((320, 180))
    x, y = index % 4 * 320, index // 4 * 204
    sheet.paste(preview, (x, y))
    draw.text((x + 8, y + 184), f'{int(path.stem)} m', fill='white')
sheet.save(folder / 'contact-sheet.jpg')
