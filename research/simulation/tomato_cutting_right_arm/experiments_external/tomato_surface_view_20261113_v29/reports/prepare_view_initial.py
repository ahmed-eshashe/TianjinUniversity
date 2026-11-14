from pathlib import Path
R=Path('/home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28');W=Path(__file__).parent
s=(R/'view_live.py').read_text();s=s.replace('W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/\'src\'))',"W=Path(__file__).resolve().parent;REFERENCE=Path('/home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28');sys.path.insert(0,str(REFERENCE/'src'));sys.path.insert(0,str(W/'src'))")
s=s.replace('from environment import CuttingEnv','from environment import CuttingEnv\nfrom surface import TomatoSurface,foliage\nfrom scipy.spatial import cKDTree')
s=s.replace("control={'playing':True,'phase':0,'mode':'scripted','release':False}","control={'playing':False,'phase':0,'mode':'scripted','release':False,'particles':False}")
s=s.replace("E.reset();control.update(playing=True,phase=0,release=False);control['mode']='scripted'","E.reset();control.update(playing=False,phase=0,release=False);control['mode']='scripted'")
start=s.index("fixed_positions=g.model['x']")
insertion='''
# Continuous, cosmetic surface; all opening is driven by current particle data.
surface=TomatoSurface(W/'assets/surface.npz');surface.update_topology(g.alive.numpy())
def vertex_material(name,roughness,coat=0.):
 m=mat(name,(.5,.02,.01),roughness);shader=UsdShade.Shader.Get(stage,'/Looks/'+name+'/Shader');reader=UsdShade.Shader.Define(stage,'/Looks/'+name+'/Colors');reader.CreateIdAttr('UsdPrimvarReader_float3');reader.CreateInput('varname',Sdf.ValueTypeNames.Token).Set('displayColor');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).ConnectToSource(reader.ConnectableAPI(),'result');shader.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(coat);shader.CreateInput('clearcoatRoughness',Sdf.ValueTypeNames.Float).Set(.22);return m
skin_material=vertex_material('NaturalSkin',.31,.28);flesh_material=vertex_material('CutFlesh',.42,.05);leaf_material=vertex_material('Calyx',.65);seed_material=mat('Seeds',(.78,.56,.24),.4)
def surface_mesh(path,faces,colors,material):
 mesh=UsdGeom.Mesh.Define(stage,path);mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist());mesh.CreateDisplayColorAttr(Vt.Vec3fArray.FromNumpy(colors));mesh.GetDisplayColorPrimvar().SetInterpolation('vertex');UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material);return mesh
skin=surface_mesh('/Tomato/SmoothSkin',surface.skin_faces,surface.skin_colors,skin_material);skin.SetNormalsInterpolation('vertex')
flesh=surface_mesh('/Tomato/CutFlesh',surface.cut_faces,surface.flesh_colors,flesh_material)
seed_mesh=surface_mesh('/Tomato/VisibleSeeds',np.empty((0,3),int),np.array([[.78,.56,.24]],np.float32),seed_material)
leaf_rest,leaf_faces,leaf_colors,leaf_anchor=foliage(g.model['x']);leaves=surface_mesh('/Tomato/Calyx',leaf_faces,leaf_colors,leaf_material)
_,leaf_support=cKDTree(g.model['x']).query(leaf_anchor,k=8);leaf_weights=1/np.maximum(np.linalg.norm(g.model['x'][leaf_support]-leaf_anchor,axis=1),.0001)**2;leaf_weights/=leaf_weights.sum();leaf_owner=leaf_support[0]
particles.GetVisibilityAttr().Set('invisible')
def toggle_particles():
 control['particles']=not control['particles']
 particles.GetVisibilityAttr().Set('inherited' if control['particles'] else 'invisible')
 for mesh in [skin,flesh,seed_mesh,leaves]:mesh.GetVisibilityAttr().Set('invisible' if control['particles'] else 'inherited')
'''
s=s[:start]+insertion+s[start:]
s=s.replace("window=ui.Window('Live approximate tomato — independent experiment',width=590,height=580)","window=ui.Window('Tomato — smooth appearance, unchanged physics',width=540,height=620)")
s=s.replace("ui.Label('LIVE APPROXIMATE TOMATO | v28'","ui.Label('LIVE TOMATO | smooth display'")
s=s.replace("ui.Label('Custom bonded-particle solver running now in Isaac Sim. The spheres are the actual collision representation.',word_wrap=True)","ui.Label('Smooth skin, green calyx and visible cut flesh follow the same live particle model.',word_wrap=True)")
s=s.replace("ui.Label('Uncalibrated training model. Scripted blade; no learned policy or robot in this isolated view. Existing kitchen/robot scene is unchanged.',word_wrap=True,style={'color':0xFF80CFFF})","ui.Label('Appearance only: physics remains approximate. Switch to particles to inspect the collision representation. Existing robot/kitchen is unchanged.',word_wrap=True,style={'color':0xFF80CFFF})")
s=s.replace("ui.Button('Pause / Resume'","ui.Button('Run / Pause cut'")
s=s.replace("  ui.Label('Manual velocity control", "  ui.Button('Smooth surface / particles',height=28,clicked_fn=toggle_particles)\n  ui.Label('Manual velocity control")
s=s.replace("  ui.Label('6.5 cm shape • 3.5 mm particles • 121 g • 2 N stop. Particle gaps and simplified forces differ from the detailed reference.',word_wrap=True)","  ui.Label('The skin, calyx and interior colours are visual details, not newly validated material properties.',word_wrap=True)")
s=s.replace('frames=0;start=time.perf_counter();last_info=None',"frames=0;start=time.perf_counter();last_info=None;captured_partial=False;captured_result=False")
s=s.replace(" while app.is_running():\n  if control['playing']:",''' while app.is_running():
  command_path=W/'command.json'
  if command_path.exists():
   try:
    command=json.loads(command_path.read_text());command_path.unlink();operation=command.get('action')
    if operation=='start':control['playing']=True
    elif operation=='pause':control['playing']=False
    elif operation=='reset':reset();captured_partial=False;captured_result=False
    elif operation=='particles' and not control['particles']:toggle_particles()
    elif operation=='surface' and control['particles']:toggle_particles()
    elif operation=='open_pieces':open_pieces()
    elif operation=='capture':capture_viewport_to_file(get_active_viewport(),str(W/'appearance_check.png'))
   except Exception as error:print('Viewer command failed:',error,flush=True)
  if control['playing']:''')
needle="  x=g.x.numpy();particles.GetPositionsAttr().Set(Vt.Vec3fArray.FromNumpy(x));particles.GetProtoIndicesAttr().Set((E.labels[0]%2).tolist())"
replacement='''  x=g.x.numpy();particles.GetPositionsAttr().Set(Vt.Vec3fArray.FromNumpy(x));particles.GetProtoIndicesAttr().Set((E.labels[0]%2).tolist())
  changed=surface.update_topology(g.alive.numpy());points=surface.points(x)
  skin.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points));skin.CreateNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(surface.normals(points)));flesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points))
  if changed:
   flesh.GetFaceVertexCountsAttr().Set([3]*len(surface.cut_faces));flesh.GetFaceVertexIndicesAttr().Set(surface.cut_faces.ravel().tolist())
  seed_points,seed_faces=surface.seeds(points);seed_mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(seed_points))
  if changed:seed_mesh.GetFaceVertexCountsAttr().Set([3]*len(seed_faces));seed_mesh.GetFaceVertexIndicesAttr().Set(seed_faces.ravel().tolist())
  # The decorative stem belongs to one actual material piece after separation.
  weight=leaf_weights*(E.labels[0][leaf_support]==E.labels[0][leaf_owner]);weight/=weight.sum();leaf_delta=np.sum(weight[:,None]*(x[leaf_support]-g.model['x'][leaf_support]),axis=0);leaves.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy((leaf_rest+leaf_delta).astype(np.float32)))'''
s=s.replace(needle,replacement)
s=s.replace("'backend':'v28 approximate custom GPU bond network'","'backend':'unchanged v28 approximate GPU bond network; v29 smooth display'")
s=s.replace("'playing':control['playing'],'wall_s':time.perf_counter()-start", "'playing':control['playing'],'surface':not control['particles'],'visible_fracture_triangles':len(surface.cut_faces),'wall_s':time.perf_counter()-start")
s=s.replace("  if frames==250:capture_viewport_to_file(get_active_viewport(),str(W/'live_preview.png'))", "  if frames==100:capture_viewport_to_file(get_active_viewport(),str(W/'intact_preview.png'))\n  if E.count[0]>1600 and E.parts[0]==1 and not captured_partial:capture_viewport_to_file(get_active_viewport(),str(W/'partial_preview.png'));captured_partial=True")
s=s.replace("  if E.done.any() and frames%100==0:capture_viewport_to_file(get_active_viewport(),str(W/'live_result.png'))", "  if E.done.any() and not captured_result:capture_viewport_to_file(get_active_viewport(),str(W/'cut_preview.png'));captured_result=True")
(W/'view_live.py').write_text(s)
(W/'launch_live.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\nexport DISPLAY="${DISPLAY:-:1}"\nexport OPENBLAS_NUM_THREADS=1\nexport PYTHONDONTWRITEBYTECODE=1\nexec /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python '+str(W/'view_live.py')+'\n');(W/'launch_live.sh').chmod(0o755)
