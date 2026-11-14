"""Separate display-only stage for verified v10 GPU block results."""
from pathlib import Path
import json,time,os,numpy as np
from isaaclab.app import AppLauncher
app=AppLauncher(headless=False,device='cpu',visualizer=['kit'],width=1600,height=900,window_width=1800,window_height=1100).app
from pxr import UsdGeom,UsdLux,UsdShade,Sdf,Gf,Vt
import omni.usd,omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
W=Path(__file__).parent
meta=json.loads((W/'capture_result.json').read_text());assert meta['source_preserved']
z=np.load(W/'surfaces.npz');omni.usd.get_context().new_stage();stage=omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1.)
def material(name,color,metal=0.):
    m=UsdShade.Material.Define(stage,'/Looks/'+name);s=UsdShade.Shader.Define(stage,'/Looks/'+name+'/Shader');s.CreateIdAttr('UsdPreviewSurface')
    s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));s.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.4);s.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal);m.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface');return m
def mesh(path,p,f,mat):
    m=UsdGeom.Mesh.Define(stage,path);m.CreateFaceVertexCountsAttr([3]*len(f));m.CreateFaceVertexIndicesAttr(f.ravel().tolist());m.CreateSubdivisionSchemeAttr('none');m.CreateDoubleSidedAttr(True);m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)));UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mat);return m
blocks={};inside={}
for side,color in [('left',(.05,.43,.38)),('right',(.9,.45,.09))]:
    mat=material(side,color);blocks[side]=mesh('/Block/'+side,z[side+'_points'][0],z[side+'_faces'],mat);inside[side]=mesh('/Block/'+side+'_cut_face',z[side+'_points'][0],z[side+'_inside'],mat)
blade=mesh('/Knife/CAD_surface',z['blade_points'][0],z['blade_faces'],material('Steel',(.6,.67,.73),.7));blade.GetVisibilityAttr().Set('invisible')
tri=z['blade_faces'];pairs=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
def curves(path,p,counts,color,width):
    c=UsdGeom.BasisCurves.Define(stage,path);c.CreateTypeAttr('linear');c.CreateCurveVertexCountsAttr(counts);c.CreateWidthsAttr([width]);c.SetWidthsInterpolation('constant');c.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)));c.CreateDisplayColorAttr([Gf.Vec3f(*color)]);return c
wire=curves('/Knife/CAD_wireframe',z['blade_points'][0][pairs].reshape(-1,3),[2]*len(pairs),(.45,.62,.8),.000045)
edge=curves('/Knife/Actual_straight_edge',z['edge_points'][0],[2],(1,.8,.15),.00012)
floor=UsdGeom.Cube.Define(stage,'/Display_floor_only');floor.CreateSizeAttr(1);floor.AddTranslateOp().Set(Gf.Vec3d(0,-.008,0));floor.AddScaleOp().Set(Gf.Vec3f(.4,.0005,.5));UsdShade.MaterialBindingAPI.Apply(floor.GetPrim()).Bind(material('Floor',(.07,.09,.13)))
dome=UsdLux.DomeLight.Define(stage,'/Dome');dome.CreateIntensityAttr(900);dome.CreateColorAttr(Gf.Vec3f(.82,.9,1))
key=UsdLux.DistantLight.Define(stage,'/Key');key.CreateIntensityAttr(1900);key.CreateAngleAttr(8);key.AddRotateXYZOp().Set(Gf.Vec3f(-30,20,25))
camera=UsdGeom.Camera.Define(stage,'/ViewCamera');camera.CreateClippingRangeAttr(Gf.Vec2f(.00002,10));camera.CreateFocalLengthAttr(45);camop=camera.AddTransformOp()
def aim(which):
    eye,target={'block':((.033,.026,.036),(.0003,0,0)),'gap':((.009,.008,.017),(.0003,0,0)),'knife':((.14,.12,.19),(0,.025,0))}[which]
    camop.Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*target),Gf.Vec3d(0,1,0)).GetInverse());get_active_viewport().camera_path='/ViewCamera'
aim('block');control={'playing':True,'elapsed':0.,'solid':False}
def toggle_blade():
    control['solid']=not control['solid'];blade.GetVisibilityAttr().Set('inherited' if control['solid'] else 'invisible')
def show_gap():control.update(elapsed=23.,playing=False);aim('gap')
window=ui.Window('GPU blade-motion result — recorded playback',width=600,height=350)
with window.frame:
    with ui.VStack(spacing=7):
        ui.Label('GPU BLADE-MOTION TEST | v10',style={'font_size':19})
        ui.Label('Saved 12 mm block test. Geometry-driven splitting; no physical knife fracture or tomato is claimed.',word_wrap=True,style={'color':0xFF91CCFF})
        ui.Label('Gold line = finite cutting edge. Blue wireframe = original knife CAD. Teal/orange identify the eventual pieces.',word_wrap=True)
        phase_label=ui.Label('Loading...',word_wrap=True);clock_label=ui.Label('')
        ui.Label('Playback is slowed down. Spatial displacement is NOT amplified. Interpolation between saved frames is for display only.',word_wrap=True)
        with ui.HStack(height=30,spacing=5):
            ui.Button('Pause / Play',clicked_fn=lambda:control.update(playing=not control['playing']))
            ui.Button('Restart',clicked_fn=lambda:control.update(elapsed=0.,playing=True))
            ui.Button('Inspect final gap',clicked_fn=show_gap)
        with ui.HStack(height=30,spacing=5):
            ui.Button('Block close-up',clicked_fn=lambda:aim('block'))
            ui.Button('Whole knife',clicked_fn=lambda:aim('knife'))
            ui.Button('Knife surface on/off',clicked_fn=toggle_blade)
        ui.Label('Final opening: +/-0.4 N auxiliary loads, 0.45 mm gap. Withdrawal is a saved pose query, not simulated contact. Existing scene unchanged.',word_wrap=True)
stage.GetRootLayer().Export(str(W/'initial_view.usda'))
previous=time.monotonic();rendered=0;captured=False
try:
    while app.is_running():
        now=time.monotonic();delta=min(now-previous,.1);previous=now
        if control['playing']:control['elapsed']+=delta
        cycle=control['elapsed']%28
        if cycle<2:i=j=0;u=0.;label='1 / Start — intact block, knife edge above material'
        elif cycle<15:
            t=cycle-2;i=min(int(t),12);j=i+1;u=t-i;label='2 / Blade traversal — persistent geometric cut develops'
        elif cycle<17:i=j=13;u=0.;label='3 / Full geometric interface — faces still coincide'
        elif cycle<19:i=j=14;u=0.;label='4 / Knife clear — static withdrawal pose query (not a contact rollout)'
        elif cycle<22:i=14;j=15;u=(cycle-19)/3;label='5 / Opening loads — display interpolation between saved endpoints'
        else:i=j=15;u=0.;label='6 / Final saved state — 0.45 mm gap from auxiliary opening forces'
        for side in blocks:
            p=(1-u)*z[side+'_points'][i]+u*z[side+'_points'][j]
            for m in [blocks[side],inside[side]]:m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)))
            inside[side].GetVisibilityAttr().Set('inherited' if i>=12 else 'invisible')
        bp=(1-u)*z['blade_points'][i]+u*z['blade_points'][j];ep=(1-u)*z['edge_points'][i]+u*z['edge_points'][j]
        blade.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(bp.astype(np.float32)));wire.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(bp[pairs].reshape(-1,3).astype(np.float32)));edge.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(ep.astype(np.float32)))
        sim=(1-u)*meta['frames'][i]['material_time_s']+u*meta['frames'][j]['material_time_s'];phase_label.text=label;clock_label.text=f'Material time: {sim*1000:.3f} ms | '+('PLAYING' if control['playing'] else 'PAUSED')
        app.update();rendered+=1
        if rendered==50:(W/'ready.json').write_text(json.dumps({'pid':os.getpid(),'visible':True,'mode':'saved GPU block evidence; no live physics','source':'v10','controls_window':window.title}))
        if rendered%100==0:(W/'heartbeat.json').write_text(json.dumps({'pid':os.getpid(),'rendered_frames':rendered,'phase':label,'material_time_s':sim,'playing':control['playing']}))
        if rendered==180 and not captured:capture_viewport_to_file(get_active_viewport(),str(W/'preview.png'));captured=True
        time.sleep(.02)
finally:
    (W/'closed.json').write_text(json.dumps({'closed':True,'rendered_frames':rendered}));app.close()
