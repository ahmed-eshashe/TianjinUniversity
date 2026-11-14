from pathlib import Path
import numpy as np,json,time
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
from pxr import UsdGeom,UsdLux,Gf,Vt
import omni.usd,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
from scipy.interpolate import PchipInterpolator
W=Path(__file__).parent;R=W.parents[1];work=W.parent
mesh=np.load(work/'disect_completion_20261108_v18/conforming_split.npz');plan=json.loads((work/'disect_batched_cutting_20261110_v40/correction_plan.json').read_text());frames={}
for directory in ['disect_cutting_candidate_20261110_v36','disect_batched_cutting_20261110_v40']:
 for p in sorted((work/directory).glob('*trajectory.npz')):
  z=np.load(p)
  if 't' not in z or 'x' not in z:continue
  for t,x in zip(z['t'],z['x']):
   if t<=.155971875+1e-10:frames[float(t)]=x.copy()
assert frames
clock=np.array(sorted(frames));positions=[frames[t] for t in clock]
cad=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');Q=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rot=Q.T@ref['rotation'];verts=np.array(cad['vertices'])@rot.T
front=np.array(plan['front_lateral_path_m']);curve=PchipInterpolator(front[:,0],front[:,1]);initial=np.array(plan['selected']['translation_m'])
def blade(t):
 u=t/plan['durations_s'][0];d=plan['downward_stroke_m']*(10*u**3-15*u**4+6*u**5);return verts+initial+[float(curve(d)),-d,0]
omni.usd.get_context().new_stage();stage=omni.usd.get_context().get_stage();UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1.)
def make(path,faces,color):
 a=UsdGeom.Mesh.Define(stage,path);a.CreateFaceVertexCountsAttr([3]*len(faces));a.CreateFaceVertexIndicesAttr(np.asarray(faces).ravel().tolist());a.CreateDisplayColorAttr([color]);a.CreateSubdivisionSchemeAttr('none');a.CreateDoubleSidedAttr(True);return a
body=make('/Tomato',mesh['outer'],(.7,.035,.015));knife=make('/Blade',cad['triangles'],(.65,.7,.75))
board=UsdGeom.Cube.Define(stage,'/Board');board.AddTranslateOp().Set(Gf.Vec3d(-.025,-.004,0));board.AddScaleOp().Set(Gf.Vec3f(.14,.008,.14));board.CreateDisplayColorAttr([(.45,.28,.13)])
light=UsdLux.DomeLight.Define(stage,'/Light');light.CreateIntensityAttr(900)
cam=UsdGeom.Camera.Define(stage,'/Camera');cam.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(.14,.12,.18),Gf.Vec3d(-.025,.025,0),Gf.Vec3d(0,1,0)).GetInverse());cam.CreateClippingRangeAttr(Gf.Vec2f(.001,100));get_active_viewport().camera_path='/Camera'
win=ui.Window('DiSECt candidate — saved physical results',width=540,height=150)
with win.frame:
 with ui.VStack():
  ui.Label('DiSECt-based modified FEM candidate: recorded loading',word_wrap=True)
  ui.Label('Original material run stopped before fracture. No separated slice.',word_wrap=True)
  ui.Label('Saved states slowed for viewing; no live physics or robot coupling.',word_wrap=True)
  label=ui.Label('')
start=time.monotonic();last=-1;ready=False;captured=False
while app.is_running():
 fraction=min(((time.monotonic()-start)%14)/11,1);target=clock[0]+fraction*(clock[-1]-clock[0]);i=min(np.searchsorted(clock,target),len(clock)-1)
 if i!=last:
  body.CreatePointsAttr().Set(Vt.Vec3fArray.FromNumpy(positions[i].astype(np.float32)));knife.CreatePointsAttr().Set(Vt.Vec3fArray.FromNumpy(blade(clock[i]).astype(np.float32)));label.text=f'Recorded time: {clock[i]*1000:.3f} ms — no damage';last=i
 app.update()
 if not ready:
  (W/'ready.json').write_text(json.dumps({'ready':True,'frames':len(clock),'start_s':float(clock[0]),'end_s':float(clock[-1]),'mode':'saved DiSECt-derived candidate playback, no live physics'}));ready=True
 if not captured and time.monotonic()-start>8:
  capture_viewport_to_file(get_active_viewport(),str(W/'preview.png'));captured=True
 time.sleep(.01)
app.close()
