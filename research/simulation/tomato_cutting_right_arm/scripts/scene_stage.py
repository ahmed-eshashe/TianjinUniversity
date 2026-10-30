"""USD-only scene composition and inspection, shared by preview and preflight."""
from pathlib import Path
from pxr import Usd, UsdPhysics
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENE = ROOT/'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'

def compose(stage, source):
    source = Path(source).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    stage.GetRootLayer().subLayerPaths.append(str(source))
    stage.Load()
    required = ['/dual_ar5_o6', '/Indoor', '/Indoor/RZ/SM_kitchen_knife_02']
    missing = [p for p in required if not stage.GetPrimAtPath(p).IsValid()]
    if missing:
        raise RuntimeError(f'Missing scene objects: {missing}')
    robot = stage.GetPrimAtPath('/dual_ar5_o6')
    if not robot.HasAPI(UsdPhysics.ArticulationRootAPI):
        raise RuntimeError('Robot articulation root is missing')
    return {
        'scene': str(source), 'required_objects': required,
        'prims': len(list(stage.Traverse())),
        'composition_errors': [str(e) for e in stage.GetCompositionErrors()],
        'robot_revolute_joints': sum(p.IsA(UsdPhysics.RevoluteJoint) for p in Usd.PrimRange(robot)),
        'articulation_roots': [str(p.GetPath()) for p in stage.Traverse() if p.HasAPI(UsdPhysics.ArticulationRootAPI)],
    }

if __name__ == '__main__':
    import json
    report = compose(Usd.Stage.CreateInMemory(), DEFAULT_SCENE)
    assert report['robot_revolute_joints'] == 36, report
    (ROOT/'logs').mkdir(exist_ok=True)
    (ROOT/'logs/scene_preflight.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
