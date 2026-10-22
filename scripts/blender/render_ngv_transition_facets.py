"""Isolated captured fold study; canonical city stays unchanged."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];d=json.loads((r/'assets/source/environment/ngv-transition-facet-study.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for i,f in enumerate(d['facets']):
 c=f['plane'];v=[(x,y,c[0]*x+c[1]*y+c[2]) for x,y in f['support_hull']];m=bpy.data.meshes.new('Captured fold support');m.from_pydata(v,[],[list(range(len(v)))]);o=bpy.data.objects.new('Captured fold '+str(i+1),m);bpy.context.collection.objects.link(o);mat=bpy.data.materials.new('Authored diagnostic zinc '+str(i+1));mat.diffuse_color=(*[(.22,.28,.30),(.36,.29,.20)][i],1);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=mat.diffuse_color;p.inputs['Metallic'].default_value=.3;p.inputs['Roughness'].default_value=.4;o.data.materials.append(mat)
s=bpy.context.scene;s.world.color=(.3,.3,.3);l=bpy.data.lights.new('Study sun','SUN');l.energy=3;o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.rotation_euler=(.4,-.5,-.3)
c=bpy.data.cameras.new('Captured fold study');o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=(273,145,67);o.rotation_euler=(Vector((238,121,30))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=42;s.camera=o;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(r/'docs/images/ngv-transition-captured-facets-study.png');bpy.ops.render.render(write_still=True);print('CAPTURED_FACET_STUDY_RENDERED_NO_SAVE',flush=True)
