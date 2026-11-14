"""Live isolated approximate tomato solver rendered in Isaac Sim.
No recorded animation, no original scene edits, no robot qualification claim.
"""
from pathlib import Path
import os,sys,json,time,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'src'))
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit'],width=1500,height=900,window_width=1800,window_height=1100).app
from pxr import UsdGeom,UsdLux,UsdShade,Sdf,Gf,Vt
import omni.usd,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
E=CuttingEnv(1,dt=.0002,max_steps=5500);g=E.g
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
fixed_positions=g.model['x'][g.fixed.numpy()!=0]
for i,pos in enumerate(fixed_positions):cube('/Support/P'+str(i),(float(pos[0]),.00035,float(pos[2])),(.0012,.0007,.0012),fixture)
blade=UsdGeom.Mesh.Define(stage,'/Knife/Blade');local=np.array([[0,0,-.06],[.0005,.03,-.06],[-.0005,.03,-.06],[0,0,.06],[.0005,.03,.06],[-.0005,.03,.06]],np.float32);faces=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]],int);blade.CreateFaceVertexCountsAttr([3]*8);blade.CreateFaceVertexIndicesAttr(faces.ravel());blade.CreateSubdivisionSchemeAttr('none');blade.CreateDoubleSidedAttr(True);UsdShade.MaterialBindingAPI.Apply(blade.GetPrim()).Bind(steel)
# Display only geometry used by the blade-contact calculation; no cosmetic handle.
dome=UsdLux.DomeLight.Define(stage,'/Dome');dome.CreateIntensityAttr(900);dome.CreateColorAttr(Gf.Vec3f(.92,.95,1));key=UsdLux.DistantLight.Define(stage,'/Key');key.CreateIntensityAttr(2100);key.CreateAngleAttr(7);key.AddRotateXYZOp().Set(Gf.Vec3f(-35,20,20))
camera=UsdGeom.Camera.Define(stage,'/ViewCamera');camera.CreateClippingRangeAttr(Gf.Vec2f(.0001,10));camera.CreateFocalLengthAttr(35);camera.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(.19,.17,.24),Gf.Vec3d(0,.025,0),Gf.Vec3d(0,1,0)).GetInverse());get_active_viewport().camera_path='/ViewCamera'
control={'playing':True,'phase':0,'mode':'scripted','release':False};manual=[None]*6

def reset():
 E.reset();control.update(playing=True,phase=0,release=False);control['mode']='scripted'
def withdraw():control.update(phase=1,playing=True,mode='scripted')
def open_pieces():
 if E.parts[0]<2:return
 g.fixed.zero_();vel=g.v.numpy();labels=E.labels[0];positions=g.x.numpy()
 for label in np.unique(labels):
  mask=labels==label;sign=-1 if positions[mask,0].mean()<.00175 else 1;vel[mask,0]+=sign*.04
 g.v.assign(vel);control.update(release=True,playing=True)
window=ui.Window('Live approximate tomato — independent experiment',width=590,height=580)
with window.frame:
 with ui.VStack(spacing=6):
  ui.Label('LIVE APPROXIMATE TOMATO | v28',style={'font_size':19})
  ui.Label('Custom bonded-particle solver running now in Isaac Sim. The spheres are the actual collision representation.',word_wrap=True)
  ui.Label('Uncalibrated training model. Scripted blade; no learned policy or robot in this isolated view. Existing kitchen/robot scene is unchanged.',word_wrap=True,style={'color':0xFF80CFFF})
  status_label=ui.Label('Starting…',word_wrap=True);metrics_label=ui.Label('',word_wrap=True)
  with ui.HStack(height=32,spacing=6):
   ui.Button('Pause / Resume',clicked_fn=lambda:control.update(playing=not control['playing']))
   ui.Button('Reset intact tomato',clicked_fn=reset)
   ui.Button('Withdraw horizontally',clicked_fn=withdraw)
  ui.Label('Manual velocity control (m/s, rad/s); limits and physics stops remain active.',word_wrap=True)
  with ui.HStack(height=30):
   ui.Button('Manual mode',clicked_fn=lambda:control.update(mode='manual',playing=True))
   ui.Button('Scripted sawing',clicked_fn=lambda:control.update(mode='scripted',playing=True))
  for i,(name,low,high) in enumerate([('X',-.15,.15),('Y',-.01,.01),('Z',-.15,.15),('Rotate X',-1,1),('Rotate Y',-1,1),('Rotate Z',-1,1)]):
   with ui.HStack(height=22):
    ui.Label(name,width=80);slider=ui.FloatSlider(min=low,max=high);slider.model.set_value(0.);manual[i]=slider.model
  ui.Button('After cutting: release fixture + pull-apart test',height=30,clicked_fn=open_pieces)
  ui.Label('The optional pull-apart test releases the bottom fixture and applies a disclosed outward impulse. It does not create the cut.',word_wrap=True)
  ui.Label('6.5 cm shape • 3.5 mm particles • 121 g • 2 N stop. Particle gaps and simplified forces differ from the detailed reference.',word_wrap=True)
frames=0;start=time.perf_counter();last_info=None
try:
 while app.is_running():
  if control['playing']:
   if control['release']:
    g.step([0,0,0],100);_,info=E.observe();last_info=info
    if info['bad'].any():control['playing']=False
   elif control['mode']=='manual':
    action=np.array([m.get_value_as_float() for m in manual]);action=np.clip(action,-E.action_limits,E.action_limits);g.step(action,100);E.count[0]+=1;_,info=E.observe();last_info=info
    if info['bad'].any():control['playing']=False
   elif not E.done.any():
    k=E.count[0];position=g.tool.numpy()[0]
    if control['mode']=='manual':action=np.array([m.get_value_as_float() for m in manual])
    else:
     action=np.zeros(6)
     if k>=25:
      if control['phase']==0:
       saw=np.sin((k-25)*.4);action[2]=.15*saw
       if position[1]>.0034:action[1]=-.0015*abs(saw)
       if E.parts[0]>=2 and position[1]<=.0034:control['phase']=1
      if control['phase']==1:action[2]=.06
    obs,r,t,tr,info=E.step(action);last_info=info
    if t.any() or tr.any():control['playing']=False
  x=g.x.numpy();particles.GetPositionsAttr().Set(Vt.Vec3fArray.FromNumpy(x));particles.GetProtoIndicesAttr().Set((E.labels[0]%2).tolist())
  q=g.rotation.numpy()[0];rot=Gf.Rotation(Gf.Quatd(float(q[3]),Gf.Vec3d(*map(float,q[:3]))));matrix=np.array(Gf.Matrix3d(rot));position=g.tool.numpy()[0];blade.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy((local@matrix+position).astype(np.float32)))
  # USD uses row-vector matrices, matching the transpose of usual column rotation.

  state='PAUSED' if not control['playing'] else 'LIVE';status_label.text=f'{state} • {control["mode"]} • {E.parts[0]} connected piece(s) • {E.count[0]*.02:.2f} simulated seconds'
  if last_info is not None:
   metrics_label.text=f'Peak blade load: {float(last_info["peak_force_N"][0]):.3f} N | Peak particle penetration: {float(last_info["peak_penetration_m"][0])*1000:.3f} mm\nBroken bonds: {int(last_info["broken"][0])} | Stop code: {int(last_info["bad"][0])} | Fixture: '+('released' if control['release'] else 'holding bottom layer')
  app.update();frames+=1
  if frames==30:(W/'viewer_ready.json').write_text(json.dumps({'pid':os.getpid(),'live':True,'backend':'v28 approximate custom GPU bond network','recorded_playback':False}))
  if frames%100==0:(W/'viewer_status.json').write_text(json.dumps({'pid':os.getpid(),'frames':frames,'simulated_s':float(E.count[0]*.02),'pieces':int(E.parts[0]),'bad':g.bad.numpy().tolist(),'playing':control['playing'],'wall_s':time.perf_counter()-start}))
  if frames==250:capture_viewport_to_file(get_active_viewport(),str(W/'live_preview.png'))
  if E.done.any() and frames%100==0:capture_viewport_to_file(get_active_viewport(),str(W/'live_result.png'))
finally:
 (W/'viewer_closed.json').write_text(json.dumps({'closed':True,'frames':frames}));app.close()
