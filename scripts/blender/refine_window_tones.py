"""Restrained authored generic pane variation; no occupancy or measured glass claims."""
import bpy,math
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3]
obj=bpy.data.objects['Authored grouped window bays - varied low rise'];mesh=obj.data
base=mesh.materials[0];variants=[]
for i,(colour,rough) in enumerate([((.10,.18,.22,1),.24),((.13,.20,.23,1),.29),((.12,.18,.19,1),.32)]):
    name=f'Authored generic pane tonal variation {i}'
    mat=bpy.data.materials.get(name)
    if not mat:
        mat=base.copy();mat.name=name;s=mat.node_tree.nodes.get('Principled BSDF')
        for link in list(mat.node_tree.links):
            if link.to_node==s and link.to_socket==s.inputs['Base Color']:mat.node_tree.links.remove(link)
        s.inputs['Base Color'].default_value=colour;s.inputs['Roughness'].default_value=rough
        mat.diffuse_color=colour
        mat['limits']='Illustrative pane tone and roughness; actual glass, blinds and interiors unverified.'
        mat['shader_reference']='https://docs.blender.org/manual/en/5.1/render/shader_nodes/shader/principled.html'
    s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=colour;s.inputs['Roughness'].default_value=rough;mat.diffuse_color=colour
    if mat.name not in [m.name for m in mesh.materials if m]:mesh.materials.append(mat)
    variants.append(list(mesh.materials).index(mat))
count=0
for p in mesh.polygons:
    if bpy.context.scene.get('generic_window_tone_revision') or p.material_index!=0:continue
    c=p.center
    key=int(abs(math.sin(c.x*12.9898+c.y*78.233+c.z*37.719))*100000)%100
    if key<18:p.material_index=variants[key%3];count+=1
mesh.update();obj['generic_pane_variation']='18 percent deterministic tonal variation; named landmark overrides retained; not occupancy data.'
bpy.context.scene['generic_window_tone_revision']=1
total=sum(p.material_index in variants for p in mesh.polygons)
print('VERIFIED varied generic panes',total,'new assignments',count,'total faces',len(mesh.polygons),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
