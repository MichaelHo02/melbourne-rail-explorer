import json,urllib.request,struct,zlib,pathlib,concurrent.futures,hashlib
project=pathlib.Path(__file__).resolve().parents[1]
root=pathlib.Path('/tmp/flinders-photomesh');root.mkdir(exist_ok=True)
metadata=json.load(open(project/'assets/source/environment/flinders-photomesh-download-index.json'))
index=metadata['zip_entries']
expected={r['region']:r['sha256'] for r in metadata['geometry_downloads']}
def fetch(r):
 e=r['obj'];p=root/(r['region']+'.obj');d=zlib.decompressobj(-15);h=hashlib.sha256();total=0
 req=urllib.request.Request(r['url'],headers={'Range':f"bytes={r['data_start']}-{r['data_start']+e['compressed']-1}"})
 with urllib.request.urlopen(req,timeout=120) as res,p.open('wb') as out:
  assert res.status==206
  while True:
   buf=res.read(2**20)
   if not buf:break
   a=d.decompress(buf);out.write(a);h.update(a);total+=len(a)
  a=d.flush();out.write(a);h.update(a);total+=len(a)
 assert total==e['size'];assert h.hexdigest()==expected[r['region']],'Source OBJ changed; recheck public archive';print(r['region'],total,h.hexdigest(),flush=True);return {'region':r['region'],'url':r['url'],'bytes':total,'sha256':h.hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 a=list(ex.map(fetch,index))
json.dump(a,open(root/'download-audit.json','w'),indent=2)
