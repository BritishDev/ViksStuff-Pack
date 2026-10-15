import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/navra/Desktop/Viks Stuff/ViksStuff-Pack')
# This is a separate background factory-startup process, never the user's scene.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for name,shift in [('parkour_finish',0.0)]:
 data=json.loads((root/f'overlay/assets/viksstuff/models/item/{name}.json').read_text())
 mats={}
 for n,tex in data['textures'].items():
  if n=='particle':continue
  image=bpy.data.images.load(str(root/('overlay/assets/viksstuff/textures/'+tex.split(':')[1]+'.png')),check_existing=True)
  color=tuple(image.pixels[:3]);m=bpy.data.materials.new(name+'_'+n);m.use_nodes=True
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.72;mats[n]=m
 for i,e in enumerate(data['elements']):
  a=e['from'];b=e['to'];center=Vector(((a[0]+b[0])/8-2,(16-a[2]-b[2])/8,(a[1]+b[1])/8-2+shift));size=Vector(((b[0]-a[0])/4,(b[2]-a[2])/4,(b[1]-a[1])/4))
  bpy.ops.mesh.primitive_cube_add(size=1,location=center);obj=bpy.context.object;obj.name=f'{name}_{i:03}';obj.scale=size;obj.data.materials.append(mats[e['faces']['south']['texture'][1:]])
bpy.ops.object.camera_add(location=(5,-10,4.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.4;bpy.context.scene.camera=cam
for location,power,size in [((1,-5,7),1100,5),((-4,-1,2),550,4),((2,4,5),900,3)]:
 bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.render.resolution_x=1400;scene.render.resolution_y=650;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.world.color=(.055,.055,.055);scene.render.film_transparent=True
out=root/'source-art/parkour/recording';bpy.ops.wm.save_as_mainfile(filepath=str(out/'parkour-solid-signs.blend'));scene.render.filepath=str(root/'previews/parkour-solid-signs-3d.png');bpy.ops.render.render(write_still=True)
