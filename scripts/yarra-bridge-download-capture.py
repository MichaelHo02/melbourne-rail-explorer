"""Fetch only OBJ entry from municipal C4-30 ZIP; photographic assets omitted."""
import sys,io,json,urllib.request,zipfile,struct,zlib,hashlib
from pathlib import Path
TILE=sys.argv[1]
URL='https://gis-3dmodelcapture-2020.s3.ap-southeast-2.amazonaws.com/photomesh/OBJ/'+TILE+'.zip'
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/tmp/flinders-photomesh')/(TILE+'.obj');OUT.parent.mkdir(exist_ok=True)
def getrange(start,end):
 req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}'})
 res=urllib.request.urlopen(req,timeout=60)
 if res.status!=206:res.close();raise RuntimeError('Expected ranged archive response')
 return res
with getrange(0,0) as res:SIZE=int(res.headers['Content-Range'].split('/')[-1])
class RemoteArchive(io.RawIOBase):
 def __init__(self):self.pos=0
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,n,w=0):self.pos=n if w==0 else self.pos+n if w==1 else SIZE+n;return self.pos
 def read(self,n=-1):
  n=SIZE-self.pos if n<0 else min(n,SIZE-self.pos)
  if n<=0:return b''
  with getrange(self.pos,self.pos+n-1) as res:data=res.read()
  if len(data)!=n:raise RuntimeError('Truncated archive range')
  self.pos+=n;return data
with zipfile.ZipFile(RemoteArchive()) as archive:
 entries=[e for e in archive.infolist() if e.filename.lower().endswith('.obj')];assert len(entries)==1
 e=entries[0];assert e.compress_type==zipfile.ZIP_DEFLATED
with getrange(e.header_offset,e.header_offset+29) as res:header=res.read()
assert header[:4]==b'PK\x03\x04';name_len,extra_len=struct.unpack_from('<HH',header,26);start=e.header_offset+30+name_len+extra_len
metadata={'source':URL,'region':TILE,'entry':e.filename,'archive_bytes':SIZE,'compressed_bytes':e.compress_size,'expected_obj_bytes':e.file_size,'expected_crc32':e.CRC,'data_start':start,'limits':'Historical2020 municipal geometry only. No photographic textures downloaded or imported.'}
(ROOT/('docs/yarra-bridge-'+TILE+'-download-index.json')).write_text(json.dumps(metadata,indent=2)+'\n');print('OBJ_ENTRY_IDENTIFIED',json.dumps(metadata),flush=True)
if '--index-only' in sys.argv:raise SystemExit(0)
part=OUT.with_suffix('.obj.partial');dec=zlib.decompressobj(-15);total=0;crc=0;sha=hashlib.sha256();compressed=0
with getrange(start,start+e.compress_size-1) as res,part.open('wb') as target:
 while True:
  block=res.read(2**20)
  if not block:break
  compressed+=len(block);raw=dec.decompress(block);target.write(raw);total+=len(raw);crc=zlib.crc32(raw,crc);sha.update(raw)
 raw=dec.flush();target.write(raw);total+=len(raw);crc=zlib.crc32(raw,crc);sha.update(raw)
assert compressed==e.compress_size and total==e.file_size and crc==e.CRC and dec.eof,'Incomplete or corrupt source OBJ'
part.replace(OUT);metadata.update({'actual_obj_bytes':total,'sha256':sha.hexdigest(),'crc32_verified':True});(ROOT/('docs/yarra-bridge-'+TILE+'-download-audit.json')).write_text(json.dumps(metadata,indent=2)+'\n');print('EAST_CAPTURE_OBJ_VERIFIED',total,sha.hexdigest(),flush=True)
