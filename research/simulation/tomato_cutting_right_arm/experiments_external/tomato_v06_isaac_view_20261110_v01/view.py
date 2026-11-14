"""Isaac Sim presentation of verified v06 block-test recordings; no live physics."""
from pathlib import Path
import json,time,os,numpy as np
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit'],width=1600,height=900,window_width=1800,window_height=1100).app
from pxr import UsdGeom,UsdLux,UsdShade,Sdf,Gf,Vt
import omni.usd,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
W=Path(__file__).parent
assert json.loads((W/'capture_result.json').read_text())['verified_capture']
z=np.load(W/'surfaces.npz');clock=z['time'];omni.usd.get_context().new_stage();stage=omni.usd.get_context().get_stage();UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1.)
meshes={};points={};offsets={'partial':np.array([-.019,0,0]),'full':np.array([.008,0,0])}
def material(name,color):
 mat=UsdShade.Material.Define(stage,'/Looks/'+name);shader=UsdShade.Shader.Define(stage,'/Looks/'+name+'/Shader');shader.CreateIdAttr('UsdPreviewSurface');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.48);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface');return mat
for kind in ['partial','full']:
 for side in ['left','right']:
  key=kind+'_'+side;faces=z[key+'_faces'];p=z[key+'_points']+offsets[kind];m=UsdGeom.Mesh.Define(stage,'/Tests/'+kind+'/'+side);m.CreateFaceVertexCountsAttr([3]*len(faces));m.CreateFaceVertexIndicesAttr(faces.ravel().tolist());m.CreateSubdivisionSchemeAttr('none');m.CreateDoubleSidedAttr(True);m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p[0].astype(np.float32)))
  color=((.65,.075,.045) if side=='left' else (.9,.23,.09)) if kind=='partial' else ((.035,.39,.33) if side=='left' else (.88,.46,.1));UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(material(key,color));meshes[key]=m;points[key]=p
floor=UsdGeom.Cube.Define(stage,'/DisplayFloor');floor.CreateSizeAttr(1.);floor.AddTranslateOp().Set(Gf.Vec3d(.002,-.009,0));floor.AddScaleOp().Set(Gf.Vec3f(.16,.001,.10));UsdShade.MaterialBindingAPI.Apply(floor.GetPrim()).Bind(material('Floor',(.16,.20,.24)))
dome=UsdLux.DomeLight.Define(stage,'/DomeLight');dome.CreateIntensityAttr(850);dome.CreateColorAttr(Gf.Vec3f(.8,.88,1))
light=UsdLux.DistantLight.Define(stage,'/KeyLight');light.CreateIntensityAttr(1800);light.CreateAngleAttr(8);light.AddRotateXYZOp().Set(Gf.Vec3f(-30,20,25))
camera=UsdGeom.Camera.Define(stage,'/ViewCamera');camera.CreateClippingRangeAttr(Gf.Vec2f(.00005,10));camera.CreateFocalLengthAttr(40);camera_op=camera.AddTransformOp()
def aim(which):
 eye,target={'overview':((.062,.048,.088),(.003,0,0)),'partial':((-.003,.014,.026),(-.019,.001,0)),'full':((.049,.021,.040),(.014,0,0))}[which]
 camera_op.Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*target),Gf.Vec3d(0,1,0)).GetInverse());get_active_viewport().camera_path='/ViewCamera'
aim('overview')
control={'playing':True,'elapsed':0.};previous=time.monotonic();rendered=0;capture_requested=False;ready=False
window=ui.Window('Latest mechanics — recorded block tests (v06)',width=580,height=280)
with window.frame:
 with ui.VStack(spacing=7):
  ui.Label('v06 INTEGRATION REPAIR — SMALL-BLOCK TESTS',style={'font_size':18})
  ui.Label('LEFT / RED: partial incision; the lower bridge stays connected.',word_wrap=True)
  ui.Label('RIGHT / TEAL + GOLD: independent-piece test. The 8 mm gap was prescribed before this recording.',word_wrap=True)
  ui.Label('No knife-generated fracture, tomato or robot coupling is shown.',word_wrap=True,style={'color':0xFF91CCFF})
  ui.Label('Saved computed motion: 1 ms stretched to 10 s. Actual displacement scale; display interpolation only.',word_wrap=True)
  timer=ui.Label('Loading verified frames...')
  with ui.HStack(height=30,spacing=6):
   ui.Button('Pause / Play',clicked_fn=lambda:control.update(playing=not control['playing']))
   ui.Button('Restart',clicked_fn=lambda:control.update(elapsed=0.))
  with ui.HStack(height=30,spacing=6):
   ui.Button('Overview',clicked_fn=lambda:aim('overview'))
   ui.Button('Partial cut close-up',clicked_fn=lambda:aim('partial'))
   ui.Button('Independent pieces',clicked_fn=lambda:aim('full'))
  ui.Label('The motions are small. Use the close-up buttons; the partial opening is about 0.05 mm.',word_wrap=True)
stage.GetRootLayer().Export(str(W/'initial_view.usda'))
try:
 while app.is_running():
  now=time.monotonic();delta=min(now-previous,.1);previous=now
  if control['playing']:control['elapsed']+=delta
  cycle=control['elapsed']%13.;phase=np.clip((cycle-1.)/10.,0.,1.);target=phase*.001;i=max(0,min(np.searchsorted(clock,target,side='right')-1,len(clock)-2));u=float(np.clip((target-clock[i])/(clock[i+1]-clock[i]),0,1))
  for key,m in meshes.items():m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(((1-u)*points[key][i]+u*points[key][i+1]).astype(np.float32)))
  timer.text=f'Recorded time: {target*1000:.3f} / 1.000 ms   |   '+('PLAYING' if control['playing'] else 'PAUSED')
  app.update();rendered+=1
  if rendered==50:
   (W/'ready.json').write_text(json.dumps({'visible':True,'pid':os.getpid(),'mode':'verified recorded mechanics, no live physics','source_version':'v06','frames':len(clock),'ui_window':'Latest mechanics — recorded block tests (v06)','control':'Pause / Play, Restart, Overview, Partial cut close-up, Independent pieces'}));ready=True
  if rendered==200 and not capture_requested:capture_viewport_to_file(get_active_viewport(),str(W/'preview.png'));capture_requested=True
  if rendered%100==0:(W/'heartbeat.json').write_text(json.dumps({'pid':os.getpid(),'rendered_frames':rendered,'recorded_time_s':target,'playing':control['playing']}))
  time.sleep(.02)
finally:
 (W/'closed.json').write_text(json.dumps({'closed':True,'rendered_frames':rendered}));app.close()
