import bpy,json
out={}
for name in ['Federation fitted captured-height deck','Federation approximate deck closure walls','Federation approximate building base closures']:
 o=bpy.data.objects[name];out[name]={'vertices':[v.co[:] for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]}
open('/tmp/ngv-platform-original-meshes.json','w').write(json.dumps(out));print('EXPORTED_NGV_CONTACT_MESHES')
