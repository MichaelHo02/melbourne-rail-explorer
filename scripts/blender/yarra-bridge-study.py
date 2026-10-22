"""Render isolated river study, optionally apply repair; no canonical save."""
import bpy, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
if os.environ.get('YARRA_BRIDGE_APPLY')=='1':
    p=ROOT/'scripts/blender/yarra-bridge-repair.py'
    exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
    if os.environ.get('YARRA_BRIDGE_CAPTURED_DECKS')=='1' or os.environ.get('YARRA_BRIDGE_AUTHORED_UNION')=='1':
        p=ROOT/'scripts/blender/yarra-bridge-captured-decks.py'
        exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
s=bpy.context.scene
c=bpy.data.objects.new('Yarra bridge study camera',bpy.data.cameras.new('Yarra bridge study camera'))
s.collection.objects.link(c)
view=os.environ.get('YARRA_BRIDGE_VIEW','river')
if view=='landing':
    c.location=(300,-260,120);target=(130,-220,4);scale=225
elif view=='landing-extent':
    c.location=(400,-350,170);target=(160,-280,3);scale=375
elif view=='western':
    c.location=(-780,-620,200);target=(-750,-355,4);scale=650
else:
    c.location=(-200,-270,170);target=(-170,-155,5);scale=660
c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
c.data.type='ORTHO'; c.data.ortho_scale=scale; c.data.clip_end=12000; s.camera=c
s.render.engine='CYCLES'; s.cycles.samples=24; s.cycles.use_denoising=True
s.render.resolution_x=1500;s.render.resolution_y=900;s.render.resolution_percentage=100
variant='captured-trial' if os.environ.get('YARRA_BRIDGE_CAPTURED_DECKS')=='1' else 'isolated' if os.environ.get('YARRA_BRIDGE_ISOLATE_KINGS')=='1' else 'captured-landing-trial' if os.environ.get('YARRA_BRIDGE_CAPTURED_LANDING_TRIAL')=='1' else 'after' if os.environ.get('YARRA_BRIDGE_APPLY')=='1' else 'before'
s.render.filepath='/tmp/yarra-bridge-'+view+'-'+variant+'.png'
bpy.ops.render.render(write_still=True)
