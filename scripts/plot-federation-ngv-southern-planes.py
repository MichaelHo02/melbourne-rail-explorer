import json,struct,zlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];d=json.loads((r/'docs/federation-ngv-southern-plane-diagnostic.json').read_text());w,h=640,1000;rgb=bytearray([242]*(w*h*3));colors=[(185,114,44),(40,123,195),(126,75,169),(63,153,91),(192,68,87),(62,163,163)]
for j,p in enumerate(d['planes']):
 for x,y,z in p['samples']:
  px=int((x-190)*12)+20;py=int((96-y)*12)+20
  for dx in range(9):
   for dy in range(9):
    if 0<=px+dx<w and 0<=py+dy<h:
     i=((py+dy)*w+px+dx)*3;rgb[i:i+3]=bytes(colors[j])
def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d)&0xffffffff)
raw=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3] for y in range(h));(r/'docs/images/federation-ngv-southern-plane-support.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
