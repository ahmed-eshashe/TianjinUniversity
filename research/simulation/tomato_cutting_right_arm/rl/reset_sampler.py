"""Seeded flat resets; all knife vertices must lie on the board with a 20 mm margin."""
import numpy as np
from scipy.spatial.transform import Rotation


class FlatResetSampler:
    def __init__(self, points, board_bounds, seed=731, margin=.02):
        self.points=np.asarray(points,dtype=float)
        self.lo,self.hi=np.asarray(board_bounds,dtype=float)
        self.margin=margin
        self.rng=np.random.default_rng(seed)
        self.centre=(self.points.min(0)+self.points.max(0))/2
        self.rejected=0

    def at(self, centre_xy, yaw):
        rotation=Rotation.from_euler('z',yaw)
        rotated=(self.points-self.centre)@rotation.as_matrix().T
        world=rotated+[*centre_xy,self.hi[2]+.003-rotated[:,2].min()]
        valid=bool(np.all(world.min(0)[:2]>=self.lo[:2]+self.margin) and
                   np.all(world.max(0)[:2]<=self.hi[:2]-self.margin))
        origin=world[0]-rotation.apply(self.points[0])
        return {'valid':valid,'pose_xyzw':[*origin,*rotation.as_quat()],
                'centre_xy':list(centre_xy),'yaw_rad':float(yaw),
                'minimum_edge_margin_m':float(np.min(np.r_[world.min(0)[:2]-self.lo[:2],self.hi[:2]-world.max(0)[:2]]))}

    def sample(self, count):
        cases=[]
        for _ in range(count*10000):
            xy=self.rng.uniform(self.lo[:2]+self.margin,self.hi[:2]-self.margin)
            case=self.at(xy,self.rng.uniform(-np.pi,np.pi))
            if case['valid']:cases.append(case)
            else:self.rejected+=1
            if len(cases)==count:return cases
        raise ValueError('Board cannot fit the requested flat reset distribution')
