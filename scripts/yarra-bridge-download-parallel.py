"""Verified parallel range download of geometry entries; omit texture assets."""
import concurrent.futures,json,urllib.request,zlib,hashlib,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for tile in sys.argv[1:]:
    d=json.loads((ROOT/('docs/yarra-bridge-'+tile+'-download-index.json')).read_text())
    size=d['compressed_bytes'];start=d['data_start'];url=d['source'];chunk=4*1024*1024
    def fetch(offset):
        end=min(size,offset+chunk)
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={'Range':f'bytes={start+offset}-{start+end-1}'})
                with urllib.request.urlopen(req,timeout=60) as r:
                    assert r.status==206
                    raw=r.read();assert len(raw)==end-offset
                    return offset,raw
            except Exception:
                if attempt==2:raise
    compressed=Path('/tmp/flinders-photomesh')/(tile+'.compressed')
    with compressed.open('wb') as f:f.truncate(size)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool,compressed.open('r+b') as f:
        complete=0
        for offset,raw in pool.map(fetch,range(0,size,chunk)):
            f.seek(offset);f.write(raw);complete+=len(raw)
            print(tile,'download',round(100*complete/size,1),flush=True)
    dec=zlib.decompressobj(-15);crc=0;total=0;sha=hashlib.sha256();part=Path('/tmp/flinders-photomesh')/(tile+'.parallel.partial')
    with compressed.open('rb') as f,part.open('wb') as out:
        while True:
            block=f.read(1024*1024)
            if not block:break
            raw=dec.decompress(block);out.write(raw);crc=zlib.crc32(raw,crc);sha.update(raw);total+=len(raw)
        raw=dec.flush();out.write(raw);crc=zlib.crc32(raw,crc);sha.update(raw);total+=len(raw)
    assert dec.eof and crc==d['expected_crc32'] and total==d['expected_obj_bytes']
    part.replace(Path('/tmp/flinders-photomesh')/(tile+'.obj'))
    d.update({'actual_obj_bytes':total,'sha256':sha.hexdigest(),'crc32_verified':True})
    (ROOT/('docs/yarra-bridge-'+tile+'-download-audit.json')).write_text(json.dumps(d,indent=2)+'\n')
    print(tile,'VERIFIED',total,flush=True)
