"""Exact spatial contact for guided cut triangles and a finite capped wedge.

Only fixed cut-face y/z, full blade span, and no blade back-edge passage are
supported. Two-node barycentric constraints resolve edge and bevel-cap crossings.
No simulator imports or changes to material, damage, or runtime controllers.
"""
import numpy as np
from scipy.sparse import coo_matrix
from tomato_blade_damage import wedge_geometry,BLADE


def cut_edges(design):
    edges=set()
    for t,tag in zip(design['pieces'][0]['triangles'],design['pieces'][0]['face_tags']):
        if tag=='cut':
            for i,j in [(0,1),(1,2),(2,0)]:edges.add(tuple(sorted((t[i],t[j]))))
    return sorted(edges)


def triangle_geometry(design,points,pairs,tip):
    """All extrema of triangle gap on its planar/bevel/cap clipped polygons.

    Entry intersections enforce sidedness only where the finite edge is present. The
    concave bevel-cap transition needs every triangle-edge intersection. The
    fixed y/z projection makes these exact linear inequalities in nodal x.
    Rows have stable identities; inactive rows have an artificial loose bound
    and zero physical power. Physical bounds are returned separately.
    """
    z=points[pairs[:,0],2];y=points[pairs[:,0],1]
    if np.max(np.abs(y))>BLADE['length_m']/2-1e-12:raise ValueError('Partial blade span requires polygon clipping; unsupported')
    if np.max(z-tip)>=BLADE['height_m']-1e-12:raise ValueError('Blade back-edge passage is unsupported')
    A,b,labels,physical,widths=wedge_geometry(design,points,pairs,tip)
    n=len(pairs);active=np.ones(len(b),dtype=bool);active[n:]=np.repeat(z-tip>=0,2)
    b[n:]=np.where(active[n:],physical[n:],b[n:])
    # Ordinary cut contact is retained everywhere, independent of damage.
    b[:n]=0.
    slope=BLADE['max_thickness_m']/BLADE['single_bevel_length_m']
    derivative=np.zeros(len(b));loading=(z-tip>0)&(z-tip<BLADE['single_bevel_length_m'])
    derivative[n:]=np.repeat(np.where(loading,slope/2,0.),2)
    rows=[];cols=[];data=[];derivatives=[];eb=[];ep=[];ea=[];meta=[]
    mapping={int(s):int(r) for s,r in pairs};crest=tip+BLADE['single_bevel_length_m']
    for kind,plane,half_width in [('entry_edge',tip,0.),('cap_edge',crest,BLADE['max_thickness_m']/2)]:
      for s0,s1 in cut_edges(design):
        z0,z1=points[[s0,s1],2];dz=z1-z0
        alpha=(plane-z0)/dz if abs(dz)>1e-14 else -1.
        live=abs(dz)>1e-14 and 0<=alpha<=1
        w=np.array([1-np.clip(alpha,0,1),np.clip(alpha,0,1)])
        for nodes,sign in [((s0,s1),-1.),((mapping[s0],mapping[s1]),1.)]:
            row=len(eb)
            for j,node in enumerate(nodes):
                rows.append(row);cols.append(3*node);data.append(sign*w[j])
                derivatives.append(sign*(1 if j==0 else -1)/dz if live else 0.)
            bound=sign*design['cut_x_m']+half_width
            eb.append(bound if live else -1.);ep.append(bound);ea.append(live)
            meta.append({'kind':kind,'nodes':nodes,'weights':w.tolist(),'active':bool(live)})
    from scipy.sparse import vstack
    E=coo_matrix((data,(rows,cols)),shape=(len(eb),points.size)).tocsr()
    Ed=coo_matrix((derivatives,(rows,cols)),shape=E.shape).tocsr()
    zero=coo_matrix(A.shape).tocsr();C=vstack([A,E],format='csr');Cd=vstack([zero,Ed],format='csr')
    # Derivatives use downward insertion depth in metres, not tip height.
    return {'matrix':C,'bounds':np.r_[b,eb],'physical':np.r_[physical,ep],
            'active':np.r_[active,ea],'d_bounds':np.r_[derivative,np.zeros(len(eb))],
            'd_matrix':Cd,'widths':widths,'base_rows':len(b),'cap_rows':meta,'labels':labels}


def blade_resistance(geometry,x,multipliers):
    """Virtual work per metre of downward insertion, including moving weights."""
    velocity=geometry['d_bounds']-geometry['d_matrix']@np.asarray(x).ravel()
    velocity[:len(geometry['widths'])]=0.
    return float(np.asarray(multipliers)@(velocity*geometry['active']))


def swept_triangle_gap(design,points,pairs,old,new,old_tip,new_tip):
    """Exact quadratic gap minima on each contact-activation interval.

    Along affine nodal paths cap barycentric weights are affine in time: their
    product is quadratic. Include every vertex entry/cap event and stationary
    point, rather than sampling only endpoints or temporal midpoints.
    """
    knots={0.,1.};dt=new_tip-old_tip
    if dt:
        for z in points[pairs[:,0],2]:
            for event in (z,z-BLADE['single_bevel_length_m']):
                t=(event-old_tip)/dt
                if 0<t<1:knots.add(float(t))
    knots=sorted(knots);minimum=float('inf')
    for a,b in zip(knots[:-1],knots[1:]):
        samples=[];mask=None
        for u in [0.,.5,1.]:
            t=a+(b-a)*u;g=triangle_geometry(design,points,pairs,old_tip+t*dt)
            samples.append(g['matrix']@np.asarray(old+t*(new-old)).ravel()-g['physical'])
            if u==.5:mask=g['active']
        f0,fm,f1=[s[mask] for s in samples]
        c=2*(f1+f0-2*fm);d=f1-f0-c
        minimum=min(minimum,float(np.min(f0)),float(np.min(f1)))
        good=np.abs(c)>1e-18;u=np.zeros(len(c));u[good]=-d[good]/(2*c[good]);inside=good&(u>0)&(u<1)
        if np.any(inside):minimum=min(minimum,float(np.min(f0[inside]+d[inside]*u[inside]+c[inside]*u[inside]**2)))
    return minimum


def nodal_blade_multipliers(geometry,pairs,multipliers):
    """Distribute barycentric facet loads for the existing eligibility gate.

    This retains the existing shared-patch approximation and edge-history gate;
    it does not replace physical blade-load eligibility with insertion depth.
    """
    n=len(pairs);out=np.asarray(multipliers[:3*n]).copy();lookup={int(s):(i,0) for i,(s,r) in enumerate(pairs)}
    lookup.update({int(r):(i,1) for i,(s,r) in enumerate(pairs)})
    for m,lam in zip(geometry['cap_rows'],multipliers[3*n:]):
        if m['active'] and lam>0:
            for node,w in zip(m['nodes'],m['weights']):
                i,side=lookup[node];out[n+2*i+side]+=w*lam
    return out


def solve_triangle_contact(model,initial,fixed,geometry,*,max_iterations=60):
    """Solve only physical active facets, then restore stable row identities.

    Loose placeholders preserve checkpoint indexing, not physical planes. They
    must not burden the QP or acquire spurious multipliers.
    """
    from tomato_linear_contact import solve_linear_contact
    used=np.flatnonzero(geometry['active'])
    result=list(solve_linear_contact(model,initial,fixed,geometry['matrix'][used],geometry['bounds'][used],max_iterations=max_iterations))
    multipliers=np.zeros(len(geometry['bounds']));multipliers[used]=result[1]
    result[1]=multipliers;result[5]=used[result[5]].tolist()
    return tuple(result)
