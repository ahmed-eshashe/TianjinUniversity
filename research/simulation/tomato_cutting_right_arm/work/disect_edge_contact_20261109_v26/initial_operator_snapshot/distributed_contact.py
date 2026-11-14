"""Conservative, fixed material-edge quadrature candidate.

Each interface vertex owns a unit contact budget divided across its incident
interior edges, then across fixed Gauss samples. Force is the exact pullback
of the discretized contact potential, including force at BOTH endpoints.
Unlike entry-plane endpoint forces, the potential releases continuously at
CAD features. Oriented intersections remain an independent coverage guard.
No coupled physical qualification is implied by this module.
"""
import numpy as np
from edge_contact import material_edges


class DistributedContact:
    def __init__(self, mesh, order=64):
        self.edges = material_edges(mesh)
        self.node_count = len(mesh['x'])
        self.cut = np.unique(mesh['ties'])
        self.outer = np.setdiff1d(np.unique(mesh['outer']),self.cut)
        counts = np.bincount(self.edges[:,1],minlength=self.node_count)
        assert np.all(counts[self.cut] > 0)
        u,w = np.polynomial.legendre.leggauss(order)
        self.coordinates = (u+1)/2
        self.gauss_weights = w/2
        self.edge_weights = 1/counts[self.edges[:,1]]
        assert np.max(abs(np.bincount(self.edges[:,1],weights=self.edge_weights,
                                     minlength=self.node_count)[self.cut]-1)) < 1e-14

    def samples(self,q,v):
        a,b = self.edges.T
        u = self.coordinates[None,:,None]
        return (q[a,None]*(1-u)+q[b,None]*u,
                v[a,None]*(1-u)+v[b,None]*u)

    def evaluate(self,q,v,query,tool_velocity,com,ke=2000.,kd=1.,kf=2500.,mu=.5):
        points,velocities = self.samples(q,v)
        shape = points.shape
        result = query(points.reshape(-1,3))
        phi = result['phi'].reshape(shape[:2])
        normal = result['normal'].reshape(shape)
        weights = self.edge_weights[:,None]*self.gauss_weights[None,:]
        relative = velocities-tool_velocity
        vn = np.sum(relative*normal,axis=2)
        tangent = relative-vn[:,:,None]*normal
        speed = np.linalg.norm(tangent,axis=2)
        elastic = ke*np.maximum(-phi,0)
        ratio = speed/kf
        friction = elastic*(mu*np.tanh(4*ratio)+(.5-mu)*ratio/(.25*ratio**2+.75)**2)
        fs = (elastic+kd*np.maximum(-vn,0)*(phi<0))[:,:,None]*normal
        fs -= friction[:,:,None]*tangent/np.maximum(speed[:,:,None],1e-300)
        fs *= weights[:,:,None]
        force = np.zeros_like(q)
        u = self.coordinates[None,:,None]
        np.add.at(force,self.edges[:,0],np.sum((1-u)*fs,axis=1))
        np.add.at(force,self.edges[:,1],np.sum(u*fs,axis=1))
        energy = .5*ke*np.sum(weights*np.minimum(phi,0)**2)
        moment = -np.cross(points-com,fs).sum(axis=(0,1))
        # Spatial-linear embedding guarantees the same wrench at material DOFs.
        assert np.max(abs(moment+np.cross(q-com,force).sum(0))) < 1e-9
        return dict(force=force,energy_J=float(energy),reaction=-force.sum(0),
                    moment=moment,maximum_sample_penetration_m=float(np.maximum(-phi,0).max()),
                    active_samples=int((phi<0).sum()),quadrature_order=len(self.coordinates),
                    sample_force=fs,phi=phi,sample_normal=normal,sample_weights=weights)
