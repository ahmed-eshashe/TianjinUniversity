"""Cosmetic v29 skin, interior and calyx driven by the live v28 particle state."""
from pathlib import Path
import sys,numpy as np
from scipy.spatial import cKDTree
from pxr import UsdGeom,UsdShade,Sdf,Gf,Vt
V=Path('/home/omen/Documents/Codex/experiments/tomato_surface_view_20261113_v29')
sys.path.insert(0,str(V/'src'))
from surface import TomatoSurface,foliage
class Appearance:
 def __init__(self,stage,E,Q,anchor):
  self.E=E;self.g=E.g;self.stage=stage;g=self.g
  T=np.eye(4);T[:3,:3]=Q;T[:3,3]=anchor
  root=UsdGeom.Xform.Define(stage,'/FastTomatoFrame');root.AddTransformOp().Set(Gf.Matrix4d(T.T.tolist()))
  def mat(name,color,roughness=.45,metal=0.,vertex=False,coat=0.):
   path='/FastTomatoLooks/'+name;m=UsdShade.Material.Define(stage,path);s=UsdShade.Shader.Define(stage,path+'/Shader');s.CreateIdAttr('UsdPreviewSurface');s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));s.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(roughness);s.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal);m.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface')
   if vertex:
    reader=UsdShade.Shader.Define(stage,path+'/Colors');reader.CreateIdAttr('UsdPrimvarReader_float3');reader.CreateInput('varname',Sdf.ValueTypeNames.Token).Set('displayColor');s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).ConnectToSource(reader.ConnectableAPI(),'result');s.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(coat)
   return m
  def mesh(name,faces,colors,material):
   m=UsdGeom.Mesh.Define(stage,'/FastTomatoFrame/'+name);m.CreateSubdivisionSchemeAttr('none');m.CreateDoubleSidedAttr(True);m.CreateFaceVertexCountsAttr([3]*len(faces));m.CreateFaceVertexIndicesAttr(faces.ravel().tolist());m.CreateDisplayColorAttr(Vt.Vec3fArray.FromNumpy(colors));m.GetDisplayColorPrimvar().SetInterpolation('vertex');UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(material);return m
  self.surface=surface=TomatoSurface(V/'assets/surface.npz');surface.update_topology(g.alive.numpy())
  skinmat=mat('Skin',(.6,.02,.01),.38,vertex=True,coat=.12);fleshmat=mat('Flesh',(.7,.03,.01),.42,vertex=True,coat=.05);leafmat=mat('Calyx',(.1,.2,.02),.65,vertex=True);seedmat=mat('Seeds',(.78,.56,.24),.4)
  self.skin=mesh('SmoothSkin',surface.skin_faces,surface.skin_colors,skinmat);self.skin.SetNormalsInterpolation('vertex');self.flesh=mesh('CutFlesh',surface.cut_faces,surface.flesh_colors,fleshmat)
  self.seeds=mesh('Seeds',np.empty((0,3),int),np.array([[.78,.56,.24]],np.float32),seedmat);self.seeds.GetDisplayColorPrimvar().SetInterpolation('constant')
  self.leaf_rest,faces,colors,anchor_leaf=foliage(g.model['x']);self.leaves=mesh('Calyx',faces,colors,leafmat)
  _,self.leaf_support=cKDTree(g.model['x']).query(anchor_leaf,k=8);self.leaf_weights=1/np.maximum(np.linalg.norm(g.model['x'][self.leaf_support]-anchor_leaf,axis=1),.0001)**2;self.leaf_weights/=self.leaf_weights.sum();self.leaf_owner=self.leaf_support[0]
  fixture=mat('BottomFixture',(.12,.16,.17),.4,.4)
  for i,pos in enumerate(g.model['x'][g.fixed.numpy()!=0]):
   c=UsdGeom.Cube.Define(stage,'/FastTomatoFrame/BottomFixture/P'+str(i));c.CreateSizeAttr(1.);c.AddTranslateOp().Set(Gf.Vec3d(float(pos[0]),.00035,float(pos[2])));c.AddScaleOp().Set(Gf.Vec3f(.0012,.0007,.0012));UsdShade.MaterialBindingAPI.Apply(c.GetPrim()).Bind(fixture)
  self.update()
 def update(self):
  g=self.g;surface=self.surface;x=g.x.numpy();changed=surface.update_topology(g.alive.numpy());points=surface.points(x)
  self.skin.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points));self.skin.CreateNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(surface.normals(points,x)));self.flesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points))
  if changed:self.flesh.GetFaceVertexCountsAttr().Set([3]*len(surface.cut_faces));self.flesh.GetFaceVertexIndicesAttr().Set(surface.cut_faces.ravel().tolist())
  self.flesh.GetVisibilityAttr().Set('inherited' if len(surface.cut_faces) else 'invisible')
  points_seed,faces=surface.seeds(points);self.seeds.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points_seed));self.seeds.GetVisibilityAttr().Set('inherited' if len(faces) else 'invisible')
  if changed:self.seeds.GetFaceVertexCountsAttr().Set([3]*len(faces));self.seeds.GetFaceVertexIndicesAttr().Set(faces.ravel().tolist())
  labels=self.E.labels[0];weight=self.leaf_weights*(labels[self.leaf_support]==labels[self.leaf_owner]);weight/=weight.sum();delta=np.sum(weight[:,None]*(x[self.leaf_support]-g.model['x'][self.leaf_support]),axis=0);self.leaves.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy((self.leaf_rest+delta).astype(np.float32)))
