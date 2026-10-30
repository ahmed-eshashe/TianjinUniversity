"""Full-node offline normal-contact coupons; no runtime simulator integration.

Contact is frictionless and restricted to fixed-normal, finite blade facets and
matched cut triangles with supported y/z DOFs. Not a general collision backend.
"""
import numpy as np
from scipy.sparse import coo_matrix,diags,tril,triu
from scipy.sparse.linalg import cg,LinearOperator,spsolve_triangular
from tomato_volume_protection import ProtectedModel,InfeasibleVolume
from offline_tomato_patch_sweep import patch_data


def assemble_model(design,assignments,damage):
    points=np.asarray([n['position_m'] for n in design['nodes']]);pairs=[];stiffness=[];cells=[]
    for a in assignments:
        pairs.extend(design['bonds'][i]['nodes'] for i in a['bond_ids'])
        stiffness.extend(a['bond_stiffness_n_m']);cells.extend(a['integration_cells_global_ids'])
    interface_count=0
    if damage<1:
        for patch in design['interface_patches']:
            _,k,_=patch_data(design,patch)
            for bid,value in zip(patch['bond_ids'],k):
                pairs.append(design['bonds'][bid]['nodes']);stiffness.append((1-damage)*value);interface_count+=1
    pairs=np.asarray(pairs);cells=np.asarray(cells)
    rest=np.linalg.norm(points[pairs[:,1]]-points[pairs[:,0]],axis=1)
    p=points[cells];volumes=np.linalg.det(p[:,1:]-p[:,:1])/6
    model=ProtectedModel(points,pairs,rest,np.asarray(stiffness),cells,volumes)
    model.interface_bonds=interface_count
    return points,model


def cut_pairs(design):
    sides=[]
    for piece in design['pieces']:
        ids={i for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut' for i in tri}
        sides.append({tuple(np.round(design['nodes'][i]['position_m'][1:],12)):i for i in ids})
    if sides[0].keys()!=sides[1].keys():raise ValueError('Unmatched finite cut faces')
    return np.asarray([[sides[0][k],sides[1][k]] for k in sorted(sides[0])])


def supports(design,points,case,drive):
    fixed={3*i+a:points[i,a] for i in design['fixture']['node_ids'] for a in range(3)}
    pairs=cut_pairs(design)
    # Explicit coupon guides preserve identical finite y/z triangulations.
    for i in pairs.reshape(-1):
        for a in [1,2]:fixed[3*i+a]=points[i,a]
    back=[]
    if case=='reclosure':
        surface=design['pieces'][0]['surface_node_ids'];minimum=min(points[i,0] for i in surface)
        back=[i for i in surface if points[i,0]<minimum+.0015]
        for i in back:fixed[3*i]=points[i,0]+drive
        # The finite cut-face guides remove tangential rigid modes; no hidden XYZ clamp.
    return fixed,back


def contact_rows(design,points,case,drive):
    pairs=cut_pairs(design);rows=[];cols=[];values=[];bounds=[];labels=[]
    for s,r in pairs:
        j=len(bounds);rows.extend([j,j]);cols.extend([3*s,3*r]);values.extend([-1.,1.]);bounds.append(0.)
        labels.append(['cut',int(s),int(r)])
    if case=='indentation':
        plane=float(points[:,0].min()+drive)
        # Finite face 265mm along y, 50mm along z; a disclosed planar blade surrogate.
        centre=float(design['dimensions_m'][2]/2)
        for piece in design['pieces']:
            for i in piece['surface_node_ids']:
                y,z=points[i,1:]
                if abs(y)<.1325 and abs(z-centre)<.025:
                    j=len(bounds);rows.append(j);cols.append(3*i);values.append(1.);bounds.append(plane)
                    labels.append(['blade',int(i)])
    matrix=coo_matrix((values,(rows,cols)),shape=(len(bounds),points.size)).tocsr()
    return matrix,np.asarray(bounds),labels


def contact_nullspace(active_labels,fixed,size):
    """Exact null-space elimination for normal pair ties and fixed blade vertices."""
    parent=np.arange(size)
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    blocked=set(fixed)
    for row in active_labels:
        if row[0]=='blade':blocked.add(3*row[1])
        else:
            a,b=map(find,[3*row[1],3*row[2]]);parent[a]=b
    blocked_roots={find(i) for i in blocked};mapping={};rows=[];cols=[]
    for i in range(size):
        root=find(i)
        if root in blocked_roots:continue
        if root not in mapping:mapping[root]=len(mapping)
        rows.append(i);cols.append(mapping[root])
    t=coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(size,len(mapping))).tocsr()
    return t,parent,find


def reduced_tangent(matrix,active_labels,fixed,size):
    t,_,_=contact_nullspace(active_labels,fixed,size)
    return t.T@matrix@t


def constrained_step(hessian,gradient,x,fixed,active_labels,active_bounds):
    """Exact constraint elimination and bounded-memory SSOR-preconditioned CG.

    No sparse direct factorization/fill-in; matrix storage remains proportional
    to the assembled graph. No physical diagonal stiffness is added.
    """
    fixed=dict(fixed)
    for label,bound in zip(active_labels,active_bounds):
        if label[0]=='blade':fixed[3*label[1]]=bound
    t,parent,find=contact_nullspace(active_labels,fixed,len(x))
    values={};counts={}
    for i,value in enumerate(x):
        root=find(i);values[root]=values.get(root,0.)+value;counts[root]=counts.get(root,0)+1
    target={r:v/counts[r] for r,v in values.items()}
    prescribed={}
    for i,value in fixed.items():
        root=find(i)
        if root in prescribed and abs(prescribed[root]-value)>1e-12:raise ValueError('Incompatible contact/support constraints')
        prescribed[root]=value
    target.update(prescribed)
    particular=np.array([target[find(i)]-x[i] for i in range(len(x))])
    h=(t.T@hessian@t).tocsr();rhs=-np.asarray(t.T@(gradient+hessian@particular)).reshape(-1)
    diagonal=h.diagonal()
    if np.any(diagonal<=0):raise ValueError('Nonpositive reduced diagonal')
    lower=tril(h,format='csr');upper=triu(h,format='csr')
    def precondition(v):
        y=spsolve_triangular(lower,v,lower=True)
        return spsolve_triangular(upper,diagonal*y,lower=False)
    pre=LinearOperator(h.shape,matvec=precondition)
    count=[0]
    def counter(_):count[0]+=1
    solution,info=cg(h,rhs,M=pre,rtol=1e-9,atol=1e-12,maxiter=2500,callback=counter)
    if info!=0:raise ValueError('Iterative contact linear solve inconclusive: '+str(info))
    return particular+np.asarray(t@solution).reshape(-1),count[0]


def solve_contact(model,points,initial,fixed,contacts,bounds,labels,max_iterations=60):
    """Primal/dual active-set Newton, exact constraints; no penalty stiffness.

    Newton guesses are uncommitted optimization iterates. Only converged feasible
    endpoints may become coupon states; no crossed physical state is repaired.
    """
    x=np.asarray(initial).reshape(-1).copy();fixed_ids=np.array(sorted(fixed),dtype=int)
    x[fixed_ids]=[fixed[i] for i in fixed_ids];free=np.setdiff1d(np.arange(x.size),fixed_ids)
    active=set(np.flatnonzero(contacts@x-bounds<0).tolist());trace=[];multipliers=np.zeros(len(bounds))
    converged=False
    for iteration in range(max_iterations):
        state=model.evaluate(x.reshape(-1,3),tangent=True);g=state['gradient_n'].reshape(-1)
        gap=contacts@x-bounds
        if np.linalg.norm(g[free])<1e-10 and gap.min()>=-1e-10 and not active:
            trace.append({'iteration':iteration,'force_residual':float(np.linalg.norm(g[free])/1e-4),
                          'min_gap_m':float(gap.min()),'active_constraints':0,'energy_j':state['energy_j'],
                          'min_J':state['min_cell_ratio']});converged=True;break
        active.update(np.flatnonzero(gap < -1e-10).tolist());a=np.array(sorted(active),dtype=int)
        af=contacts[a][:,free]
        direction,linear_iterations=constrained_step(state['tangent_n_m'],g,x,fixed,[labels[i] for i in a],bounds[a])
        effective=g+state['tangent_n_m']@direction
        aa=(af@af.T).tocsr();diagonal=aa.diagonal()
        if aa.nnz!=len(a) or np.any(diagonal<=0):raise ValueError('Unsupported overlapping contact rows')
        multipliers[:]=0.;multipliers[a]=np.asarray(af@effective[free]).reshape(-1)/diagonal
        residual=g-contacts.T@multipliers
        # 1e-6 relative gate, with 1e-10 N absolute allowance at effectively zero load.
        scale=max(np.linalg.norm(g[fixed_ids]),np.linalg.norm(contacts.T@multipliers),1e-4)
        relative=float(np.linalg.norm(residual[free])/scale)
        trace.append({'iteration':iteration,'force_residual':relative,'min_gap_m':float(gap.min()),
                      'active_constraints':len(a),'energy_j':state['energy_j'],'min_J':state['min_cell_ratio']})
        trace[-1]['linear_iterations']=linear_iterations
        if relative<1e-7 and np.max(np.abs(gap[a]),initial=0.)<1e-10 and gap.min()>=-1e-10:
            negative=a[multipliers[a]<-1e-9]
            if len(negative):active.difference_update(negative.tolist());continue
            converged=True;break
        # Active-set QP predicts newly blocking constraints; bind them before stepping.
        end_gap=gap+contacts@direction
        blocking=[i for i in np.flatnonzero(end_gap < -1e-10) if i not in active]
        if blocking:active.update(blocking);continue
        penalty=max(1.,2*float(np.max(np.abs(multipliers),initial=0.)))
        def merit(v,s):
            gv=contacts@v-bounds
            return s['energy_j']+penalty*(np.sum(np.abs(gv[a]))+np.sum(np.maximum(-gv,0.)))
        current=merit(x,state);alpha=1.;accepted=False
        while alpha>1e-8:
            trial=x+alpha*direction
            try:
                result=model.evaluate(trial.reshape(-1,3))
                if merit(trial,result)<=current+1e-14:
                    accepted=True;break
            except InfeasibleVolume:pass
            alpha*=.5
        if not accepted:break
        x=trial
    state=model.evaluate(x.reshape(-1,3),tangent=True)
    return x.reshape(-1,3),multipliers,state,trace,converged,sorted(active),fixed_ids,free


def swept_minimum_volume(model,old,new):
    """Exact cubic-in-path-volume minimum, including interior critical points."""
    times=np.array([0.,1/3,2/3,1.]);samples=[]
    for t in times:
        p=(old+t*(new-old))[model.cells]
        samples.append(np.linalg.det(p[:,1:]-p[:,:1])/(6*model.volumes))
    coefficients=np.linalg.solve(np.vander(times,4,increasing=True),np.asarray(samples)).T
    minimum=float(np.min([samples[0],samples[-1]]))
    a,b,c=3*coefficients[:,3],2*coefficients[:,2],coefficients[:,1]
    discriminant=b*b-4*a*c
    for sign in [-1.,1.]:
        good=(np.abs(a)>1e-12)&(discriminant>=0)
        t=np.full(len(a),-1.)
        t[good]=(-b[good]+sign*np.sqrt(discriminant[good]))/(2*a[good])
        if sign==1:
            linear=(np.abs(a)<=1e-12)&(np.abs(b)>1e-12)
            t[linear]=-c[linear]/b[linear]
        valid=(t>0)&(t<1)
        co=coefficients[valid];tv=t[valid]
        if len(tv):minimum=min(minimum,float(np.min(co[:,0]+tv*(co[:,1]+tv*(co[:,2]+tv*co[:,3])))))
    return minimum


def proper_surface_intersections(design,positions,tolerance=1e-9):
    """Bounded static proper-intersection screen; coplanar touching is allowed.

    This is NOT general continuous collision detection. Separate normal-contact
    interpolation certificates cover the supported blade and matched cut faces.
    """
    triangles=[positions[np.asarray(p['triangles'])] for p in design['pieces']]
    a,b=triangles;blo=b.min(axis=1);bhi=b.max(axis=1);count=0;candidates=0
    def crossings(edges,faces):
        hit=np.zeros(len(faces),dtype=bool);e1=faces[:,1]-faces[:,0];e2=faces[:,2]-faces[:,0]
        normal=np.cross(e1,e2);norm=np.linalg.norm(normal,axis=1)
        for j in range(3):
            p=edges[:,j];q=edges[:,(j+1)%3];d0=np.einsum('ni,ni->n',normal,p-faces[:,0])/norm
            d1=np.einsum('ni,ni->n',normal,q-faces[:,0])/norm
            crossing=((d0 < -tolerance)&(d1>tolerance))|((d1 < -tolerance)&(d0>tolerance))
            indices=np.flatnonzero(crossing)
            if not len(indices):continue
            t=d0[indices]/(d0[indices]-d1[indices]);delta=p[indices]+t[:,None]*(q[indices]-p[indices])-faces[indices,0]
            u=e1[indices];v=e2[indices]
            uu=np.einsum('ni,ni->n',u,u);uv=np.einsum('ni,ni->n',u,v);vv=np.einsum('ni,ni->n',v,v)
            du=np.einsum('ni,ni->n',delta,u);dv=np.einsum('ni,ni->n',delta,v);den=uu*vv-uv*uv
            x=(du*vv-dv*uv)/den;y=(dv*uu-du*uv)/den
            hit[indices]|=(x>=-1e-10)&(y>=-1e-10)&(x+y<=1+1e-10)
        return hit
    for start in range(0,len(a),64):
        block=a[start:start+64];lo=block.min(axis=1);hi=block.max(axis=1)
        overlap=np.all(lo[:,None,:]<=bhi[None,:,:]+tolerance,axis=2)&np.all(hi[:,None,:]>=blo[None,:,:]-tolerance,axis=2)
        i,j=np.nonzero(overlap);candidates+=len(i)
        if len(i):count+=int(np.sum(crossings(block[i],b[j])|crossings(b[j],block[i])))
    return count,candidates
