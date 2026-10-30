"""Evaluator-only PhysX contacts; never included in policy observations."""
import numpy as np
import warp as wp
from pxr import UsdPhysics
from isaaclab_physx.physics import PhysxManager


def numpy(value):
    if isinstance(value,np.ndarray):return value
    if isinstance(value,wp.array):return value.numpy()
    return value.detach().cpu().numpy()


class NativeContactMonitor:
    def __init__(self,env):
        self.env=env
        from isaaclab.app.settings_manager import get_settings_manager
        get_settings_manager().set_bool('/physics/disableContactProcessing',False)
        stage=env.sim.stage
        self.bodies=[str(p.GetPath()) for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
        self.filters=self.bodies+[env.manifest['board_path'],env.manifest['counter_path']]
        self.view=PhysxManager.get_physics_sim_view().create_rigid_contact_view(
            self.bodies,[self.filters for _ in self.bodies],max_contact_data_count=4096)

    def summary(self):
        matrix=numpy(self.view.get_contact_force_matrix(dt=1/240))
        forces=np.linalg.norm(matrix,axis=-1)
        return [{'body':self.bodies[i],'other':self.filters[j],'force_n':float(forces[i,j])}
                for i,j in zip(*np.where(forces>.05))]
