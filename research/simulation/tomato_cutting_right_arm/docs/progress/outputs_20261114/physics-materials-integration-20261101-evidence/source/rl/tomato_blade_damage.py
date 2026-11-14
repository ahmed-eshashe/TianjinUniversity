"""Restricted offline wedge contact and committed surface damage, not a full cut.

Fixed cut-face y/z guides, finite surrogate wedge, prescribed cut interface.
Patch damage eligibility needs a swept edge event AND current positive contact.
No simulator imports, friction, arbitrary blade pose, or native integration.
"""
import numpy as np
from scipy.sparse import coo_matrix
from tomato_bonds import DamageState
from tomato_surface_cohesion import SurfaceCohesion,patch_response,update_surface_damage
from tomato_contact_reference import edge_hits_site

BLADE={'length_m':.26593121886253357,'height_m':.0504381824284792,
       'max_thickness_m':.00760862766765058,'single_bevel_length_m':.008}


def fracture_loss(law,state):
    """Exact cumulative integral U0 dD on the bilinear loading envelope.

    Not the larger fixed-geometry energy drop of an explicit damage jump.
    Zero during unloading, independent of step count, capped at area*Gc.
    """
    a,b=law.onset_m,law.failure_m
    q=np.clip(state.kappa_m,a,b)
    return float(.5*law.stiffness_n_m*a*b/(b-a)*(q-a))


class EvolvingCohesion(SurfaceCohesion):
    def __init__(self,design,pairs):
        super().__init__(design,pairs,0.)
        self.states=[DamageState() for _ in self.patches]

    def damage_for_patch(self,index):return self.states[index].damage

    def trial_states(self,x,committed,eligible):
        gaps=x[self.pairs[:,1]]-x[self.pairs[:,0]]-self.reference_gaps
        return [update_surface_damage(p['law'],old,gaps[p['indices']],p['weights'],p['stiffness'],eligible=bool(ok))
                for p,old,ok in zip(self.patches,committed,eligible)]

    def dissipation(self,states):
        return sum(fracture_loss(p['law'],s) for p,s in zip(self.patches,states))

    def algorithmic_tangent(self,x,tangent,committed,eligible):
        """Consistent softening correction, at fixed geometric eligibility.

        On active loading d[(1-D)grad U0]/dx subtracts
        D'(q)/(Kn*q) outer(grad U0,grad U0). Not a frozen-D stability claim.
        """
        gaps=x[self.pairs[:,1]]-x[self.pairs[:,0]]-self.reference_gaps
        result=tangent.copy()
        for p,old,state,ok in zip(self.patches,committed,self.states,eligible):
            q=state.kappa_m;law=p['law'];a,b=law.onset_m,law.failure_m
            if not ok or not (a<q<b):continue
            ids=p['indices'];pair=self.pairs[ids]
            r=patch_response(gaps[ids],p['weights'],p['stiffness'],0.)
            current_q=np.sqrt(2*r['energy_j']/law.stiffness_n_m)
            # At the history boundary include the loading-side correction, a
            # lower bound on both loading and frozen-damage unloading tangents.
            if current_q < old.kappa_m-1e-12:continue
            dofs=(3*pair[:,:,None]+np.arange(3)).reshape(-1)
            g=np.stack([-r['gradient_n'],r['gradient_n']],axis=1).reshape(-1)
            factor=(b*a/((b-a)*q*q))/(law.stiffness_n_m*q)
            h=-factor*np.outer(g,g)
            result+=coo_matrix((h.ravel(),(np.repeat(dofs,len(dofs)),np.tile(dofs,len(dofs)))),shape=result.shape).tocsr()
        return result


def wedge_geometry(design,points,pairs,tip,*,mode='contact'):
    """Fixed-normal unilateral facets. Finite edge, no infinite blade plane."""
    yz=points[pairs[:,0],1:];slope=BLADE['max_thickness_m']/BLADE['single_bevel_length_m']
    inside=np.abs(yz[:,0])<=BLADE['length_m']/2
    if mode=='miss':inside[:]=False
    depth=yz[:,1]-tip
    widths=np.where(inside&(depth>0)&(depth<=BLADE['height_m']),np.minimum(slope*depth,BLADE['max_thickness_m']),0.)
    rows=[];cols=[];data=[];bounds=[];physical_bounds=[];labels=[]
    cut=design['cut_x_m']
    for i,(s,r) in enumerate(pairs):
        j=len(bounds);rows.extend([j,j]);cols.extend([3*s,3*r]);data.extend([-1.,1.])
        # Where both blade halfspaces apply they imply gap >= width > 0.
        # Remove the redundant closed-face tie from this restricted active set;
        # leaving it bindable creates an infeasible set of equalities.
        bounds.append(-1. if widths[i]>0 else 0.);physical_bounds.append(0.);labels.append(['cut',int(s),int(r)])
    for i,(s,r) in enumerate(pairs):
        for side,node,sign in [(0,s,-1.),(1,r,1.)]:
            j=len(bounds);rows.append(j);cols.append(3*node);data.append(sign)
            physical=sign*cut+widths[i]/2
            bounds.append(physical if widths[i]>0 else -1.)
            physical_bounds.append(physical)
            labels.append(['blade_left' if side==0 else 'blade',int(node)])
    A=coo_matrix((data,(rows,cols)),shape=(len(bounds),points.size)).tocsr()
    return A,np.asarray(bounds),labels,np.asarray(physical_bounds),widths


def edge_history(points,pairs,old_tip,tip,committed_hits,*,mode='contact'):
    hits=np.asarray(committed_hits,dtype=bool).copy()
    if mode in ('miss','face_rub'):return hits
    for i,(s,_) in enumerate(pairs):
        hits[i]|=edge_hits_site(points[s,1:],old_tip,tip,BLADE)
    return hits


def contact_eligibility(cohesion,hits,multipliers,widths):
    n=len(cohesion.pairs)
    loaded=np.any(np.asarray(multipliers[n:]).reshape(n,2)>1e-9,axis=1)&(widths>0)&hits
    return np.asarray([np.any(loaded[p['indices']]) for p in cohesion.patches])
