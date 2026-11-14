from pathlib import Path
import json
from pxr import Usd,UsdShade,UsdPhysics
W=Path(__file__).resolve().parent
rows=[]
for old,new in [('head_vision_pickup_v02.usda','head_vision_pickup_v03.usda'),('knife_short_blade_v01.usda','knife_short_blade_v02.usda')]:
 path=W/new;assert not path.exists();s=Usd.Stage.CreateNew(str(path));s.GetRootLayer().subLayerPaths=[str(W/old)];mat=UsdShade.Material(s.GetPrimAtPath('/Phase3ContactMaterial'));assert UsdPhysics.MaterialAPI(mat.GetPrim()).GetDynamicFrictionAttr().Get()>.59
 for suffix in ['CollisionHandle','CollisionBlade']:
  p=s.GetPrimAtPath('/dual_ar5_o6/MountedKnife/'+suffix);UsdShade.MaterialBindingAPI.Apply(p).Bind(mat,UsdShade.Tokens.strongerThanDescendants,'physics');actual,_=UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial(materialPurpose='physics');assert str(actual.GetPath())=='/Phase3ContactMaterial'
 s.GetRootLayer().Save();rows.append(dict(source=str(W/old),corrected=str(path),change='Explicit local physics-purpose binding of knife colliders to existing Phase3ContactMaterial; previous referenced binding target escaped its reference scope.',static_friction=.8,dynamic_friction=.6,restitution=0.,geometry_mass_actuator_limits_unchanged=True))
(W/'reports/material_binding_repair.json').write_text(json.dumps(rows,indent=2))
