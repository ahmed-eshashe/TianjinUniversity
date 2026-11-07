from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf,UsdLux
SOURCE='/home/omen/Aperdata-SimReady-Kitchen-01/0_Kitchen_Indoor/Indoor.usd'
def apply(stage,knife):
 source=Usd.Stage.Open(SOURCE);report=[]
 for dest,src in [('/Indoor/RZ/SM_YZ_CF_10','/Root/RZ/SM_YZ_CF_10'),('/Indoor/RZ/SM_kitchen_Board','/Root/RZ/SM_kitchen_Board'),(knife,'/Root/RZ/SM_kitchen_knife_02')]:
  dp=stage.GetPrimAtPath(dest);sp=source.GetPrimAtPath(src);dm=UsdGeom.Mesh(dp);sm=UsdGeom.Mesh(sp)
  assert list(dm.GetFaceVertexIndicesAttr().Get())==list(sm.GetFaceVertexIndicesAttr().Get()),dest
  for pv in UsdGeom.PrimvarsAPI(sp).GetPrimvars():
   if pv.Get() is None:continue
   new=UsdGeom.PrimvarsAPI(dp).CreatePrimvar(pv.GetPrimvarName(),pv.GetTypeName(),pv.GetInterpolation(),pv.GetElementSize());new.Set(pv.Get())
   if pv.IsIndexed():new.SetIndices(pv.GetIndices())
  for part in [sp]+[x for x in sp.GetChildren() if x.IsA(UsdGeom.Subset)]:
   mat,_=UsdShade.MaterialBindingAPI(part).ComputeBoundMaterial()
   if not mat:continue
   suffix=str(part.GetPath())[len(src):];target=stage.GetPrimAtPath(dest+suffix)
   if not target:target=stage.DefinePrim(dest+suffix,'GeomSubset')
   if part.IsA(UsdGeom.Subset):
    for name in ['indices','familyName','elementType']:target.CreateAttribute(name,part.GetAttribute(name).GetTypeName()).Set(part.GetAttribute(name).Get())
   mp='/PresentationLooks/'+dest.rsplit('/',1)[-1]+suffix.replace('/','_');material=UsdShade.Material.Define(stage,mp);material.GetPrim().GetReferences().AddReference(SOURCE,mat.GetPath());UsdShade.MaterialBindingAPI.Apply(target).Bind(material);report.append(dict(prim=str(target.GetPath()),source=str(mat.GetPath())))
 def simple(name,color,metal,rough):
  mat=UsdShade.Material.Define(stage,'/PresentationLooks/'+name);shader=UsdShade.Shader.Define(stage,str(mat.GetPath())+'/Surface');shader.CreateIdAttr('UsdPreviewSurface');shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));shader.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal);shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface');return mat
 paint=simple('robot_painted_metal',(.65,.7,.76),.25,.28);rubber=simple('finger_grip_surfaces',(.055,.065,.075),0,.65)
 for p in stage.Traverse():
  if str(p.GetPath()).startswith('/dual_ar5_o6/') and p.IsA(UsdGeom.Mesh):
   isfinger=any(t in str(p.GetPath()) for t in ['_distal/','thumb_distal/']);UsdShade.MaterialBindingAPI.Apply(p).Bind(rubber if isfinger else paint)
 dome=UsdLux.DomeLight.Define(stage,'/PresentationLight');dome.CreateIntensityAttr(650.);dome.CreateColorAttr(Gf.Vec3f(.85,.92,1.))
 key=UsdLux.DistantLight.Define(stage,'/PresentationSun');key.CreateIntensityAttr(1800.);key.CreateAngleAttr(12.);UsdGeom.Xformable(key).AddRotateXYZOp().Set(Gf.Vec3f(-35,15,-30))
 return report
