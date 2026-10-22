"""Render diagnostic placeholder-ground categories without saving scene mutations."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3]
def emission(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');s=n.new('ShaderNodeEmission');s.inputs['Color'].default_value=(*c,1);m.node_tree.links.new(s.outputs[0],o.inputs['Surface']);return m
black=emission('DIAGNOSTIC other geometry',(0,0,0));red=emission('DIAGNOSTIC fallback ground',(1,0,0));yellow=emission('DIAGNOSTIC neutral open parcel',(1,1,0));classified=[];handled=set()
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 names=[m.name if m else '' for m in o.data.materials];neutral=any(name=='Authored neutral urban ground' for name in names)
 category='fallback' if neutral and o.name in ['Authored flat ground','Authored ground with City Square portal'] else 'neutral_parcel' if neutral else 'other'
 if neutral:classified.append({'object':o.name,'category':category})
 key=o.data.as_pointer()
 if key in handled:continue
 handled.add(key)
 o.data.materials.clear();o.data.materials.append(red if category=='fallback' else yellow if category=='neutral_parcel' else black)
 for p in o.data.polygons:p.material_index=0
s=bpy.context.scene;s.camera=bpy.data.objects['02 Flinders precinct'];s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.film_transparent=False;s.use_nodes=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.world.use_nodes=True;n=s.world.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(0,0,0,1);bg.inputs['Strength'].default_value=0;s.world.node_tree.links.new(bg.outputs[0],out.inputs[0])
s.render.filepath=str(R/'docs/images/observatory-placeholder-ground-mask.png');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(s.render.filepath,check_existing=False);pixels=list(im.pixels);red_count=sum(1 for i in range(0,len(pixels),4) if pixels[i]>.8 and pixels[i+1]<.2 and pixels[i+2]<.2);yellow_count=sum(1 for i in range(0,len(pixels),4) if pixels[i]>.8 and pixels[i+1]>.8 and pixels[i+2]<.2);total=len(pixels)//4
out={'camera':'02 Flinders precinct','resolution':[1000,800],'red_exposed_fallback_pixels':red_count,'yellow_neutral_parcel_pixels':yellow_count,'total_pixels':total,'fallback_frame_fraction':red_count/total,'neutral_parcel_frame_fraction':yellow_count/total,'classified_objects':classified,'limits':'Screen-space diagnostic, not ground area, material accuracy or city-wide completeness. Bright interior category pixels counted; antialiased edge pixels excluded. Camera framing includes a different field of view than the normal review render because aspect ratio differs. Transparent materials replaced by opaque black; this mask reports geometry occlusion, not optical ground visibility through glass. No scene file saved.'};(R/'docs/visible-placeholder-ground-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED visible placeholder diagnostic',red_count,yellow_count,total,flush=True)
