# Public API for module omni.physx:

## Functions

- def get_physx_interface() -> PhysX
- def get_physxunittests_interface() -> PhysXUnitTests
- def get_physx_property_query_interface() -> IPhysxPropertyQuery
- def get_physx_visualization_interface() -> PhysXVisualization
- def get_physx_scene_query_interface() -> PhysXSceneQuery
- def get_physx_cooking_interface() -> PhysXCooking
- def get_physx_simulation_interface() -> IPhysxSimulation
- def get_physx_benchmarks_interface() -> IPhysxBenchmarks
- def get_physx_replicator_interface() -> IPhysxReplicator
- def get_physx_stage_update_interface() -> IPhysxStageUpdate
- def get_physx_statistics_interface() -> IPhysxStatistics

## Other



# Public API for module omni.physx.scripts.physicsUtils:

## Functions

- def compute_bounding_box_diagonal(points: typing.List[carb.Float3]) -> float
- def create_mesh(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], points: typing.Union[typing.List[Gf.Vec3f], typing.List[Gf.Vec3d]], normals: typing.Union[typing.List[Gf.Vec3f], typing.List[Gf.Vec3d]], indices: typing.List[int], vertexCounts: typing.List[Gf.Vec3f]) -> UsdGeom.Mesh
- def create_mesh_square_axis(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], axis: str, halfSize: float) -> UsdGeom.Mesh
- def create_mesh_concave(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], halfSize: float) -> UsdGeom.Mesh
- def create_mesh_cube(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], halfSize: float) -> UsdGeom.Mesh
- def create_mesh_cylinder(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], height: float, radius: float, tesselation: int = 32) -> UsdGeom.Mesh
- def create_mesh_cone(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], height: float, radius: float, tesselation: int = 32) -> UsdGeom.Mesh
- def add_density(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], value: float) -> UsdPhysics.MassAPI
- def add_mass(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], mass: float = 1.0) -> UsdPhysics.MassAPI
- def add_force_torque(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], force: Gf.Vec3f = Gf.Vec3f(0.0), torque: Gf.Vec3f = Gf.Vec3f(0.0), mode: str = 'acceleration', isEnabled: bool = True, isWorldSpace: bool = False) -> PhysxSchema.PhysxForceAPI
- def add_physics_material_to_prim(stage: Usd.Stage, prim: Usd.Prim, materialPath: typing.Union[str, Sdf.Path])
- def add_collision_to_collision_group(stage: Usd.Stage, collisionPath: typing.Union[str, Sdf.Path], collisionGroupPath: typing.Union[str, Sdf.Path])
- def remove_collision_from_collision_group(stage: Usd.Stage, collisionPath: typing.Union[str, Sdf.Path], collisionGroupPath: typing.Union[str, Sdf.Path])
- def is_in_collision_group(stage: Usd.Stage, collisionPath: typing.Union[str, Sdf.Path], collisionGroupPath: typing.Union[str, Sdf.Path]) -> bool
- def add_ground_plane(stage: Usd.Stage, planePath: typing.Union[str, Sdf.Path], axis: str, size: float, position: typing.Union[Gf.Vec3f, Gf.Vec3d], color: Gf.Vec3f) -> str
- def add_quad_plane(stage: Usd.Stage, quadPath: typing.Union[str, Sdf.Path], axis: str, size: float, position: typing.Union[Gf.Vec3f, Gf.Vec3d], color: Gf.Vec3f)
- def add_cube_ground_plane(stage: Usd.Stage, cubePath: typing.Union[str, Sdf.Path], axis: str, size: float, position: typing.Union[Gf.Vec3f, Gf.Vec3d], color: Gf.Vec3f)
- def add_box(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_box(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_box(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_cube(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_cube(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_cube(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], size: Gf.Vec3f = Gf.Vec3f(1.0), position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_sphere(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_sphere(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_sphere(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_capsule(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_capsule(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_capsule(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_cylinder(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_cylinder(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_cylinder(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_cone(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_collider_cone(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_cone(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], radius: float = 1.0, height: float = 1.0, axis: str = 'Y', position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), color: Gf.Vec3f = Gf.Vec3f(1.0), density: float = 1.0, lin_velocity: Gf.Vec3f = Gf.Vec3f(0.0), ang_velocity: Gf.Vec3f = Gf.Vec3f(0.0)) -> Usd.Prim
- def add_xform(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), scale: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def add_rigid_xform(stage: Usd.Stage, path: typing.Union[str, Sdf.Path], position: Gf.Vec3f = Gf.Vec3f(0.0), orientation: Gf.Quatf = Gf.Quatf(1.0), scale: Gf.Vec3f = Gf.Vec3f(1.0)) -> Usd.Prim
- def get_translation(prim: Usd.Prim) -> typing.Union[Gf.Vec3f, Gf.Vec3d]
- def add_joint_fixed(stage: Usd.Stage, jointPath: typing.Union[str, Sdf.Path], actor0: typing.Union[str, Sdf.Path], actor1: typing.Union[str, Sdf.Path], localPos0: Gf.Vec3f, localRot0: Gf.Quatf, localPos1: Gf.Vec3f, localRot1: Gf.Quatf, breakForce: float, breakTorque: float) -> UsdPhysics.FixedJoint
- def set_or_add_scale_op(xformable: UsdGeom.Xformable, scale: typing.Union[Gf.Vec3f, Gf.Vec3d, Gf.Vec3h]) -> UsdGeom.XformOp
- def set_or_add_translate_op(xformable: UsdGeom.Xformable, translate: typing.Union[Gf.Vec3f, Gf.Vec3d, Gf.Vec3h]) -> UsdGeom.XformOp
- def set_or_add_orient_op(xformable: UsdGeom.Xformable, orient: typing.Union[Gf.Quatf, Gf.Quatd, Gf.Quath]) -> UsdGeom.XformOp
- def set_or_add_scale_orient_translate(xformable: UsdGeom.Xformable, scale: typing.Union[Gf.Vec3f, Gf.Vec3d, Gf.Vec3h], orient: typing.Union[Gf.Quatf, Gf.Quatd, Gf.Quath], translate: typing.Union[Gf.Vec3f, Gf.Vec3d, Gf.Vec3h]) -> typing.List[UsdGeom.XformOp]
- def setup_transform_as_scale_orient_translate(xformable: UsdGeom.Xformable)
- def copy_transform_as_scale_orient_translate(src: UsdGeom.Xformable, dst: UsdGeom.Xformable)
