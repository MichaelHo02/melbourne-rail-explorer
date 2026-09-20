"""Convert a bounded selection of official I3S raw mesh tiles into embedded GLBs.
Run with Python 3; standard library only. No whole-city archive or API key.
"""
import concurrent.futures,datetime,gzip,hashlib,json,math,pathlib,struct,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://tiles.arcgis.com/tiles/KGdHCCUjGBpOPPac/arcgis/rest/services/Southbank_WGS84/SceneServer/layers/0'
OUT=ROOT/'public/models/photomesh';OUT.mkdir(parents=True,exist_ok=True)
ORIGIN=[144.9671,-37.8183]
SELECTIONS={'southern-cross-context': ['34440', '150709', '153085', '158179', '186273', '187588', '191470', '194217', '196542', '211660', '213382', '222364', '28830', '28937', '30661', '31830', '218894', '220141'], 'viaduct-context': ['25693', '111578', '141755', '147014', '147456', '155581', '161066', '161756', '163103', '164095', '25816', '27596', '28751', '109969', '111116', '119369', '122529', '123359', '125431', '126186', '136083', '137550', '138874', '140285', '143132', '145508', '145719', '146111', '128495', '129847', '130208'], 'southbank-context': ['19402', '19915', '20222', '21069', '23289', '60745', '62044', '102414', '107186', '107654', '108253', '109798', '102771', '105838', '106433', '110123', '110639'], 'flinders-street-context': ['CBD:90514', 'CBD:91824', 'CBD:178250', 'CBD:179837', 'CBD:184574', 'CBD:196149', 'CBD:198529', 'CBD:199208', 'CBD:200263', 'CBD:175192'], 'southern-cross-north': ['CBD:220330', 'CBD:223505', 'CBD:280503', 'CBD:282345', 'CBD:284115', 'CBD:284568', 'CBD:288770', 'CBD:289078', 'CBD:289401', 'CBD:289848', 'CBD:292532', 'CBD:228313', 'CBD:229887', 'CBD:231701', 'CBD:232059', 'CBD:247419', 'CBD:249075', 'CBD:249271', 'CBD:249560', 'CBD:250103', 'CBD:254349', 'CBD:254592', 'CBD:270773', 'CBD:271098', 'CBD:272407', 'CBD:274183', 'CBD:276178', 'CBD:277199', 'CBD:278601', 'CBD:278890']}
CACHE=pathlib.Path('/tmp/melbourne-photomesh-source');CACHE.mkdir(exist_ok=True)
MAX_RESOURCE=8_000_000

def fetch(path,service='Southbank'):
 base=BASE.replace('Southbank_WGS84',service+'_WGS84')
 url=base+'/'+path;cache=CACHE/((service+'_' if service!='Southbank' else '')+path.replace('/','_'))
 if cache.exists():return cache.read_bytes()
 request=urllib.request.Request(url,headers={'User-Agent':'MelbourneRailExplorer-source-preparation/1.0'})
 with urllib.request.urlopen(request,timeout=45) as response:data=response.read(MAX_RESOURCE+1)
 if len(data)>MAX_RESOURCE:raise RuntimeError('Refusing oversized source resource: '+url)
 if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
 cache.write_bytes(data);return data

def convex_hull(points):
 points=sorted(set(points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[];upper=[]
 for point in points:
  while len(lower)>=2 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
  lower.append(point)
 for point in reversed(points):
  while len(upper)>=2 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
  upper.append(point)
 return lower[:-1]+upper[:-1]

def decode(node_id):
 service,node_id=node_id.split(':') if ':' in node_id else ('Southbank',node_id)
 base=BASE.replace('Southbank_WGS84',service+'_WGS84')
 node=json.loads(fetch('nodes/'+node_id,service));geometry=fetch('nodes/'+node_id+'/geometries/0',service);jpeg=fetch('nodes/'+node_id+'/textures/0',service)
 count,features=struct.unpack_from('<II',geometry);expected=8+count*36+features*16
 if len(geometry)!=expected or count%3:raise RuntimeError('Unexpected raw I3S geometry layout for node '+node_id)
 offset=8;positions=struct.unpack_from('<'+str(count*3)+'f',geometry,offset);offset+=count*12
 normals=struct.unpack_from('<'+str(count*3)+'f',geometry,offset);offset+=count*12
 uv=struct.unpack_from('<'+str(count*2)+'f',geometry,offset)
 p=[];n=[];t=[]
 for i in range(count):
  lon,lat,height=positions[i*3:i*3+3];p.extend([lon*87939,height,-lat*111320])
  east,north,up=normals[i*3:i*3+3];n.extend([east,up,-north])
  u,v=uv[i*2:i*2+2];t.extend([u,v])
 if not all(math.isfinite(v) for v in p+n+t):raise RuntimeError('Non-finite vertex data')
 center=node['mbs'][:3];translation=[(center[0]-ORIGIN[0])*87939,center[2],-(center[1]-ORIGIN[1])*111320]
 bounds={'min':[min(p[k::3])+translation[k] for k in range(3)],'max':[max(p[k::3])+translation[k] for k in range(3)]}
 provenance={'nodeId':node_id,'service':base,'nodeLevel':node['level'],'nodeCenterWGS84':center,'sourceBoundingSphere':node['mbs'],'worldBounds':bounds,'footprintHullXZ':convex_hull([(round(p[i]+translation[0],3),round(p[i+2]+translation[2],3)) for i in range(0,len(p),3)]),'vertexCount':count,'triangleCount':count//3,'geometrySha256':hashlib.sha256(geometry).hexdigest(),'textureSha256':hashlib.sha256(jpeg).hexdigest(),'geometryBytes':len(geometry),'textureBytes':len(jpeg),'license':'CC BY 4.0','attribution':'City of Melbourne, 3D Textured Mesh (Photomesh) 2020. Converted from I3S to local game coordinates.','resources':{'geometry':base+'/nodes/'+node_id+'/geometries/0','texture':base+'/nodes/'+node_id+'/textures/0','metadata':base+'/nodes/'+node_id}}
 return {'p':p,'n':n,'uv':t,'jpeg':jpeg,'translation':translation,'provenance':provenance}

def glb(name,tiles):
 binary=bytearray();views=[];accessors=[];meshes=[];nodes=[];materials=[];textures=[];images=[]
 def view(payload,target=None):
  while len(binary)%4:binary.append(0)
  start=len(binary);binary.extend(payload);v={'buffer':0,'byteOffset':start,'byteLength':len(payload)}
  if target:v['target']=target
  views.append(v);return len(views)-1
 def attribute(values,kind):
  width=3 if kind=='VEC3' else 2;i=view(struct.pack('<'+str(len(values))+'f',*values),34962);a={'bufferView':i,'componentType':5126,'count':len(values)//width,'type':kind}
  if kind=='VEC3':a.update({'min':[min(values[k::3]) for k in range(3)],'max':[max(values[k::3]) for k in range(3)]})
  accessors.append(a);return len(accessors)-1
 for index,tile in enumerate(tiles):
  # Losslessly share identical complete vertices; keep atlas seams and hard normals.
  unique={};positions=[];normals=[];uvs=[];indices=[]
  for i in range(len(tile['p'])//3):
   key=tuple(tile['p'][i*3:i*3+3]+tile['n'][i*3:i*3+3]+tile['uv'][i*2:i*2+2])
   if key not in unique:
    unique[key]=len(unique);positions.extend(key[:3]);normals.extend(key[3:6]);uvs.extend(key[6:])
   indices.append(unique[key])
  attrs={'POSITION':attribute(positions,'VEC3'),'NORMAL':attribute(normals,'VEC3'),'TEXCOORD_0':attribute(uvs,'VEC2')}
  index_view=view(struct.pack('<'+str(len(indices))+'I',*indices),34963)
  accessors.append({'bufferView':index_view,'componentType':5125,'count':len(indices),'type':'SCALAR'});index_accessor=len(accessors)-1
  images.append({'bufferView':view(tile['jpeg']),'mimeType':'image/jpeg'});textures.append({'source':index,'sampler':0})
  materials.append({'name':'Photomesh baked colour '+tile['provenance']['nodeId'],'pbrMetallicRoughness':{'baseColorTexture':{'index':index},'metallicFactor':0,'roughnessFactor':1},'doubleSided':True,'extensions':{'KHR_materials_unlit':{}}})
  meshes.append({'name':'I3S '+tile['provenance']['nodeId'],'primitives':[{'attributes':attrs,'indices':index_accessor,'material':index,'mode':4}]})
  nodes.append({'mesh':index,'translation':tile['translation']})
 while len(binary)%4:binary.append(0)
 document={'asset':{'version':'2.0','generator':'Melbourne Rail Explorer official I3S sample converter','copyright':'City of Melbourne. CC BY 4.0.'},'extensionsUsed':['KHR_materials_unlit'],'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':materials,'textures':textures,'images':images,'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}],'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors}
 encoded=json.dumps(document,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
 payload=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
 path=OUT/(name+'.glb');path.write_bytes(payload)
 return {'name':name,'path':'/models/photomesh/'+name+'.glb','bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'tiles':[t['provenance'] for t in tiles]}

def main():
 manifest={'source':'City of Melbourne 3D Textured Mesh (Photomesh) 2020','catalogueUrl':'https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020/information/','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/legalcode','retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'capture':'May 2020','sourceCRS':{'horizontal':'EPSG:4326 WGS84','vertical':'EPSG:5773 EGM96 geoid heights (declared by served layer)'},'gameOrigin':ORIGIN,'transform':{'x':'(longitude-144.9671)*87939','y':'source EGM96 height in metres, no vertical offset applied','z':'-(latitude+37.8183)*111320','normal':'ENU (east,north,up) becomes (east,up,-north)','uv':'glTF TEXCOORD_0 preserves source (u,v); served JPEG coordinates verified by render'},'assets':[]}
 for name,node_ids in SELECTIONS.items():
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:tiles=list(pool.map(decode,node_ids))
  result=glb(name,tiles);manifest['assets'].append(result);print(name,result['bytes'],'bytes',sum(t['provenance']['triangleCount'] for t in tiles),'triangles',flush=True)
 if sum(a['bytes'] for a in manifest['assets'])>40_000_000:raise RuntimeError('Runtime selection exceeds40MB')
 (ROOT/'src/data/photomesh-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
