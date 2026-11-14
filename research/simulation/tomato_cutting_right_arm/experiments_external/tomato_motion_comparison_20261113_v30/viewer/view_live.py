"""Live isolated approximate tomato solver rendered in Isaac Sim.
No recorded animation, no original scene edits, no robot qualification claim.
"""
from pathlib import Path
import os,sys,json,time,numpy as np
W=Path(__file__).resolve().parent;REFERENCE=Path('/home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28');sys.path.insert(0,str(REFERENCE/'src'));DISPLAY_SOURCE=Path('/home/omen/Documents/Codex/experiments/tomato_surface_view_20261113_v29');sys.path.insert(0,str(DISPLAY_SOURCE/'src'));sys.path.insert(0,str(W.parent))
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit'],width=1500,height=900,window_width=1800,window_height=1100).app
from pxr import UsdGeom,UsdLux,UsdShade,Sdf,Gf,Vt
import omni.usd,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
from surface import TomatoSurface,foliage
from compare import command as motion_command, CASES
MOTION=CASES['smooth_sync_2x']
from scipy.spatial import cKDTree
E=CuttingEnv(1,dt=.0001,max_steps=5500);g=E.g
omni.usd.get_context().new_stage();stage=omni.usd.get_context().get_stage();UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1.)
def mat(name,color,roughness=.45,metal=0.):
 m=UsdShade.Material.Define(stage,'/Looks/'+name);s=UsdShade.Shader.Define(stage,'/Looks/'+name+'/Shader');s.CreateIdAttr('UsdPreviewSurface');s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));s.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(roughness);s.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal);m.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface');return m
red=mat('Tomato',(.65,.025,.012),.28);red2=mat('SecondPiece',(.95,.12,.025),.3);wood=mat('Board',(.38,.19,.065),.65);steel=mat('Steel',(.65,.7,.76),.2,.9);black=mat('Handle',(.035,.026,.023));fixture=mat('Fixture',(.12,.16,.17),.4,.4)
def cube(path,center,size,material):
 c=UsdGeom.Cube.Define(stage,path);c.CreateSizeAttr(1);c.AddTranslateOp().Set(Gf.Vec3d(*center));c.AddScaleOp().Set(Gf.Vec3f(*size));UsdShade.MaterialBindingAPI.Apply(c.GetPrim()).Bind(material);return c
cube('/Board',(0,-.003,0),(.22,.006,.31),wood);cube('/Ground',(0,-.012,0),(2,.01,2),mat('Ground',(.055,.07,.075),.8))
particles=UsdGeom.PointInstancer.Define(stage,'/Tomato/Particles');prototypes=[]
for i,m in enumerate([red,red2]):
 path='/Tomato/Prototypes/P'+str(i);s=UsdGeom.Sphere.Define(stage,path);s.CreateRadiusAttr(g.model['radius']);UsdShade.MaterialBindingAPI.Apply(s.GetPrim()).Bind(m);prototypes.append(path)
particles.CreatePrototypesRel().SetTargets(prototypes);particles.CreatePositionsAttr(Vt.Vec3fArray.FromNumpy(g.x.numpy()));particles.CreateProtoIndicesAttr([0]*g.n)

# Continuous, cosmetic surface; all opening is driven by current particle data.
surface=TomatoSurface(DISPLAY_SOURCE/'assets/surface.npz');surface.update_topology(g.alive.numpy())
def vertex_material(name,roughness,coat=0.):
 m=mat(name,(.5,.02,.01),roughness);shader=UsdShade.Shader.Get(stage,'/Looks/'+name+'/Shader');reader=UsdShade.Shader.Define(stage,'/Looks/'+name+'/Colors');reader.CreateIdAttr('UsdPrimvarReader_float3');reader.CreateInput('varname',Sdf.ValueTypeNames.Token).Set('displayColor');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).ConnectToSource(reader.ConnectableAPI(),'result');shader.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(coat);shader.CreateInput('clearcoatRoughness',Sdf.ValueTypeNames.Float).Set(.22);return m
skin_material=vertex_material('NaturalSkin',.38,.12);flesh_material=vertex_material('CutFlesh',.42,.05);leaf_material=vertex_material('Calyx',.65);seed_material=mat('Seeds',(.78,.56,.24),.4)
def surface_mesh(path,faces,colors,material):
 mesh=UsdGeom.Mesh.Define(stage,path);mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist());mesh.CreateDisplayColorAttr(Vt.Vec3fArray.FromNumpy(colors));mesh.GetDisplayColorPrimvar().SetInterpolation('vertex');UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material);return mesh
skin=surface_mesh('/Tomato/SmoothSkin',surface.skin_faces,surface.skin_colors,skin_material);skin.SetNormalsInterpolation('vertex')
flesh=surface_mesh('/Tomato/CutFlesh',surface.cut_faces,surface.flesh_colors,flesh_material)
seed_mesh=surface_mesh('/Tomato/VisibleSeeds',np.empty((0,3),int),np.array([[.78,.56,.24]],np.float32),seed_material);seed_mesh.GetDisplayColorPrimvar().SetInterpolation('constant');seed_mesh.GetVisibilityAttr().Set('invisible');flesh.GetVisibilityAttr().Set('invisible')
leaf_rest,leaf_faces,leaf_colors,leaf_anchor=foliage(g.model['x']);leaves=surface_mesh('/Tomato/Calyx',leaf_faces,leaf_colors,leaf_material)
_,leaf_support=cKDTree(g.model['x']).query(leaf_anchor,k=8);leaf_weights=1/np.maximum(np.linalg.norm(g.model['x'][leaf_support]-leaf_anchor,axis=1),.0001)**2;leaf_weights/=leaf_weights.sum();leaf_owner=leaf_support[0]
particles.GetVisibilityAttr().Set('invisible')
def toggle_particles():
 control['particles']=not control['particles']
 particles.GetVisibilityAttr().Set('inherited' if control['particles'] else 'invisible')
 for mesh in [skin,flesh,seed_mesh,leaves]:mesh.GetVisibilityAttr().Set('invisible' if control['particles'] else 'inherited')
fixed_positions=g.model['x'][g.fixed.numpy()!=0]
for i,pos in enumerate(fixed_positions):cube('/Support/P'+str(i),(float(pos[0]),.00035,float(pos[2])),(.0012,.0007,.0012),fixture)
blade=UsdGeom.Mesh.Define(stage,'/Knife/Blade');local=np.array([[0,0,-.06],[.0005,.03,-.06],[-.0005,.03,-.06],[0,0,.06],[.0005,.03,.06],[-.0005,.03,.06]],np.float32);faces=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]],int);blade.CreateFaceVertexCountsAttr([3]*8);blade.CreateFaceVertexIndicesAttr(faces.ravel());blade.CreateSubdivisionSchemeAttr('none');blade.CreateDoubleSidedAttr(True);UsdShade.MaterialBindingAPI.Apply(blade.GetPrim()).Bind(steel)
# Display only geometry used by the blade-contact calculation; no cosmetic handle.
dome=UsdLux.DomeLight.Define(stage,'/Dome');dome.CreateIntensityAttr(900);dome.CreateColorAttr(Gf.Vec3f(.92,.95,1));key=UsdLux.DistantLight.Define(stage,'/Key');key.CreateIntensityAttr(2100);key.CreateAngleAttr(7);key.AddRotateXYZOp().Set(Gf.Vec3f(-35,20,20))
camera=UsdGeom.Camera.Define(stage,'/ViewCamera');camera.CreateClippingRangeAttr(Gf.Vec2f(.0001,10));camera.CreateFocalLengthAttr(35);camera.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(.19,.17,.24),Gf.Vec3d(0,.025,0),Gf.Vec3d(0,1,0)).GetInverse());get_active_viewport().camera_path='/ViewCamera'
control={'playing':False,'phase':0,'mode':'scripted','release':False,'particles':False};manual=[None]*6

def reset():
 E.reset();control.update(playing=False,phase=0,release=False);control['mode']='scripted'
def withdraw():control.update(phase=1,playing=True,mode='scripted')
def open_pieces():
 if E.parts[0]<2:return
 g.fixed.zero_();vel=g.v.numpy();labels=E.labels[0];positions=g.x.numpy()
 for label in np.unique(labels):
  mask=labels==label;sign=-1 if positions[mask,0].mean()<.00175 else 1;vel[mask,0]+=sign*.04
 g.v.assign(vel);control.update(release=True,playing=True)
def replay():
 reset();control['playing']=True
window=ui.Window('Smoother tomato slicing',width=540,height=620)
with window.frame:
 with ui.VStack(spacing=6):
  ui.Label('LIVE TOMATO | smoother slicing',style={'font_size':19})
  ui.Label('Longer, smoother sweeps. Downward movement eases as the blade changes direction.',word_wrap=True)
  ui.Label('Same approximate material and safety limits. Scripted blade motion; not a learned policy. Expected cycle: about 32 simulated seconds.',word_wrap=True,style={'color':0xFF80CFFF})
  status_label=ui.Label('Starting…',word_wrap=True);metrics_label=ui.Label('',word_wrap=True)
  with ui.HStack(height=32,spacing=6):
   ui.Button('Run / Pause cut',clicked_fn=lambda:control.update(playing=not control['playing']))
   ui.Button('Replay from start',clicked_fn=replay)
   ui.Button('Withdraw horizontally',clicked_fn=withdraw)
  ui.Button('Smooth surface / particles',height=28,clicked_fn=toggle_particles)
  ui.Label('Manual velocity control (m/s, rad/s); limits and physics stops remain active.',word_wrap=True)
  with ui.HStack(height=30):
   ui.Button('Manual mode',clicked_fn=lambda:control.update(mode='manual',playing=True))
   ui.Button('Smooth slicing',clicked_fn=lambda:control.update(mode='scripted',playing=True))
  for i,(name,low,high) in enumerate([('X',-.15,.15),('Y',-.01,.01),('Z',-.15,.15),('Rotate X',-1,1),('Rotate Y',-1,1),('Rotate Z',-1,1)]):
   with ui.HStack(height=22):
    ui.Label(name,width=80);slider=ui.FloatSlider(min=low,max=high);slider.model.set_value(0.);manual[i]=slider.model
  ui.Button('After cutting: release fixture + pull-apart test',height=30,clicked_fn=open_pieces)
  ui.Label('The optional pull-apart test releases the bottom fixture and applies a disclosed outward impulse. It does not create the cut.',word_wrap=True)
  ui.Label('The skin, calyx and interior colours are visual details, not newly validated material properties.',word_wrap=True)
frames=0;start=time.perf_counter();last_info=None;captured_partial=False;captured_result=False
try:
 while app.is_running():
  command_path=W/'command.json'
  if command_path.exists():
   try:
    command=json.loads(command_path.read_text());command_path.unlink();operation=command.get('action')
    if operation=='start':control['playing']=True
    elif operation=='pause':control['playing']=False
    elif operation=='replay':replay()
    elif operation=='reset':reset();captured_partial=False;captured_result=False
    elif operation=='particles' and not control['particles']:toggle_particles()
    elif operation=='surface' and control['particles']:toggle_particles()
    elif operation=='open_pieces':open_pieces()
    elif operation=='capture':capture_viewport_to_file(get_active_viewport(),str(W/'appearance_check.png'))
   except Exception as error:print('Viewer command failed:',error,flush=True)
  if control['playing']:
   if control['release']:
    g.step([0,0,0],E.substeps);_,info=E.observe();last_info=info
    if info['bad'].any():control['playing']=False
   elif control['mode']=='manual':
    action=np.array([m.get_value_as_float() for m in manual]);action=np.clip(action,-E.action_limits,E.action_limits);g.step(action,E.substeps);E.count[0]+=1;_,info=E.observe();last_info=info
    if info['bad'].any():control['playing']=False
   elif not E.done.any():
    k=E.count[0];position=g.tool.numpy()[0]
    action,control['phase']=motion_command(MOTION,k,position,E.parts[0],control['phase'])
    obs,r,t,tr,info=E.step(action);last_info=info
    if t.any() or tr.any():control['playing']=False
  x=g.x.numpy();particles.GetPositionsAttr().Set(Vt.Vec3fArray.FromNumpy(x));particles.GetProtoIndicesAttr().Set((E.labels[0]%2).tolist())
  changed=surface.update_topology(g.alive.numpy());points=surface.points(x)
  skin.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points));skin.CreateNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(surface.normals(points,x)));flesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points))
  if changed:
   flesh.GetFaceVertexCountsAttr().Set([3]*len(surface.cut_faces));flesh.GetFaceVertexIndicesAttr().Set(surface.cut_faces.ravel().tolist())
  flesh.GetVisibilityAttr().Set('inherited' if len(surface.cut_faces) and not control['particles'] else 'invisible')
  seed_points,seed_faces=surface.seeds(points);seed_mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(seed_points))
  seed_mesh.GetVisibilityAttr().Set('inherited' if len(seed_faces) and not control['particles'] else 'invisible')
  if changed:seed_mesh.GetFaceVertexCountsAttr().Set([3]*len(seed_faces));seed_mesh.GetFaceVertexIndicesAttr().Set(seed_faces.ravel().tolist())
  # The decorative stem belongs to one actual material piece after separation.
  weight=leaf_weights*(E.labels[0][leaf_support]==E.labels[0][leaf_owner]);weight/=weight.sum();leaf_delta=np.sum(weight[:,None]*(x[leaf_support]-g.model['x'][leaf_support]),axis=0);leaves.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy((leaf_rest+leaf_delta).astype(np.float32)))
  q=g.rotation.numpy()[0];rot=Gf.Rotation(Gf.Quatd(float(q[3]),Gf.Vec3d(*map(float,q[:3]))));matrix=np.array(Gf.Matrix3d(rot));position=g.tool.numpy()[0];blade.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy((local@matrix+position).astype(np.float32)))
  # USD uses row-vector matrices, matching the transpose of usual column rotation.

  state='PAUSED' if not control['playing'] else 'LIVE';status_label.text=f'{state} • {control["mode"]} • {E.parts[0]} connected piece(s) • {E.count[0]*.02:.2f} simulated seconds'
  if last_info is not None:
   metrics_label.text=f'Peak blade load: {float(last_info["peak_force_N"][0]):.3f} N | Peak particle penetration: {float(last_info["peak_penetration_m"][0])*1000:.3f} mm\nBroken bonds: {int(last_info["broken"][0])} | Stop code: {int(last_info["bad"][0])} | Fixture: '+('released' if control['release'] else 'holding bottom layer')
  app.update();frames+=1
  if frames==30:(W/'viewer_ready.json').write_text(json.dumps({'pid':os.getpid(),'live':True,'backend':'v28 unchanged physics; v29 appearance; v30 synchronized smooth slicing at 0.1 ms','motion':'smooth_sync_2x','dt_s':E.dt,'recorded_playback':False}))
  if frames%100==0:(W/'viewer_status.json').write_text(json.dumps({'pid':os.getpid(),'frames':frames,'motion':'smooth_sync_2x','dt_s':E.dt,'simulated_s':float(E.count[0]*.02),'peak_load_N':float(g.peak.numpy()[0]),'peak_penetration_mm':float(g.penetration_peak.numpy()[0])*1000,'pieces':int(E.parts[0]),'bad':g.bad.numpy().tolist(),'playing':control['playing'],'surface':not control['particles'],'visible_fracture_triangles':len(surface.cut_faces),'wall_s':time.perf_counter()-start}))
  if frames==100:capture_viewport_to_file(get_active_viewport(),str(W/'intact_preview.png'))
  if E.count[0]>700 and E.parts[0]==1 and not captured_partial:capture_viewport_to_file(get_active_viewport(),str(W/'partial_preview.png'));captured_partial=True
  if E.done.any() and not captured_result:capture_viewport_to_file(get_active_viewport(),str(W/'cut_preview.png'));captured_result=True
finally:
 (W/'viewer_closed.json').write_text(json.dumps({'closed':True,'frames':frames}));app.close()
