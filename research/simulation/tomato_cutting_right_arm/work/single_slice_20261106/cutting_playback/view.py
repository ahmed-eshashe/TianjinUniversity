from pathlib import Path
import time,json,numpy as np
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit']).app
from pxr import Gf,Vt,UsdGeom,UsdShade,Sdf
import omni.usd,omni.timeline,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
w=Path(__file__).parent
import carb
carb.settings.get_settings().set_bool('/rtx/hydra/readTransformsFromFabric',False)
carb.settings.get_settings().set_bool('/rtx/hydra/readGeometryFromFabric',False)
omni.usd.get_context().open_stage(str(w/'playback_static.usdc'))
for _ in range(60):app.update()
stage=omni.usd.get_context().get_stage()
cam=UsdGeom.Camera(stage.GetPrimAtPath('/ReplayCamera'));cam.GetOrderedXformOps()[0].Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(-.52,-.55,.42),Gf.Vec3d(-.04,-.06,.04),Gf.Vec3d(0,0,1)).GetInverse());cam.CreateClippingRangeAttr(Gf.Vec2f(.01,1000))
mat=UsdShade.Material.Define(stage,'/PlaybackTomatoRed');shader=UsdShade.Shader.Define(stage,'/PlaybackTomatoRed/Surface');shader.CreateIdAttr('UsdPreviewSurface');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(.65,.018,.008));shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.3);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
for prim in stage.GetPrimAtPath('/RecordedTomato').GetChildren():UsdShade.MaterialBindingAPI.Apply(prim).Bind(mat,bindingStrength=UsdShade.Tokens.strongerThanDescendants)
viewport=get_active_viewport();viewport.camera_path='/ReplayCamera'
window=ui.Window('Recorded cutting — incomplete separation',width=440,height=100)
with window.frame:
 with ui.VStack():
  ui.Label('Saved simulation playback • 4× slower',word_wrap=True)
  ui.Label('Tomato remains connected. No new cutting physics is running.',word_wrap=True)
  ui.Label('Loops automatically. Close this window using the main app close button.',word_wrap=True)
timeline=omni.timeline.get_timeline_interface();timeline.stop();duration=json.loads((w/'manifest.json').read_text())['duration_s'];start=time.monotonic();captured=False
(w/'viewer_ready.json').write_text(json.dumps({'ready':True,'mode':'recorded playback','duration_s':duration}))
data=np.load(w/'playback_arrays.npz');stage=omni.usd.get_context().get_stage();attrs=[stage.GetAttributeAtPath(str(p)) for p in data['paths']];last=-1
while app.is_running():
 t=(time.monotonic()-start)%(duration+2);idx=min(int(np.searchsorted(data['times'],min(t,duration)*24)),len(data['times'])-1)
 if idx!=last:
  for j,a in enumerate(attrs):
   value=data['a'+str(j)][idx];a.Set(Gf.Matrix4d(value.tolist()) if value.shape==(4,4) else Vt.Vec3fArray.FromNumpy(value.astype(np.float32)))
  last=idx
 app.update()
 if not captured and t>duration*.7:
  capture_viewport_to_file(viewport,str(w/'preview.png'));captured=True
 time.sleep(.01)
app.close()
