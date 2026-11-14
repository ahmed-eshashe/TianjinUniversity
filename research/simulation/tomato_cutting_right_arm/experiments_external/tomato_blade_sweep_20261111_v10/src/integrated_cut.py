"""Isolated v06 reference-cell integration; one prescribed X-normal cut only.

Observation points are not mass samples. Mechanics uses Gauss integration over
every current reference knot span. No contact or physical fracture is supplied.
"""
import hashlib
import json
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import BSpline
from scipy.linalg import null_space
from scipy.sparse import csr_matrix,coo_matrix,kron,eye,hstack
from scipy.sparse.linalg import splu
from block_basis import block_basis
from reference import energy_stress


class RejectedEvent(RuntimeError):
    def __init__(self, reason, detail=None):
        super().__init__(reason)
        self.detail = detail or {}


def values_gradient(knots, x):
    n = len(knots)-3
    B = BSpline(knots, np.eye(n), 2)(x)
    low = BSpline(knots, np.eye(n+1), 1)(x)
    G = np.zeros_like(B)
    for i in range(n):
        a, b = knots[i+2]-knots[i], knots[i+3]-knots[i+1]
        if a > 0: G[:, i] += 2/a*low[:, i]
        if b > 0: G[:, i] -= 2/b*low[:, i+1]
    return csr_matrix(B), csr_matrix(G)


def tensor_basis(knots, axes):
    bg = [values_gradient(t, x) for t, x in zip(knots, axes)]
    B = kron(kron(bg[0][0], bg[1][0]), bg[2][0], format='csr')
    G = [kron(kron(bg[0][j==0], bg[1][j==1]), bg[2][j==2], format='csr') for j in range(3)]
    return B, G


def quadrature(knots, order):
    g, w = leggauss(order)
    axes, weights = [], []
    for t in knots:
        breaks = np.unique(t)
        lo, hi = breaks[:-1], breaks[1:]
        axes.append((.5*((hi-lo)[:, None]*g+hi[:, None]+lo[:, None])).ravel())
        weights.append((.5*(hi-lo)[:, None]*w).ravel())
    points = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1,3)
    vols = np.einsum('i,j,k->ijk', *weights).ravel()
    return axes, points, vols


def greville(knots):
    return np.stack(np.meshgrid(*[np.array([np.mean(t[i+1:i+3]) for i in range(len(t)-3)]) for t in knots], indexing='ij'), axis=-1).reshape(-1,3)


def matrix_audit(M):
    d = np.linalg.eigvalsh(M.toarray())
    rank = int(np.sum(d > d[-1]*1e-12))
    cond = float(d[-1]/d[0]) if d[0] > 0 else float('inf')
    audit = {'dofs':M.shape[0], 'mass_rank':rank, 'mass_condition':cond if np.isfinite(cond) else None, 'min_eigenvalue':float(d[0]), 'max_eigenvalue':float(d[-1])}
    if rank < M.shape[0] or cond > 1e8:
        raise RejectedEvent('unresolved or ill-conditioned integrated mass', audit)
    return audit


class IntegratedBody:
    """Direct tensor-basis body, also used as an independent two-body reference."""
    def __init__(self, knots, observations, order=5, E=1e5, nu=.4, rho=1000., fixed=None):
        self.knots = [np.array(t, float) for t in knots]
        self.X = np.asarray(observations, float).copy()
        self.axes = [np.unique(self.X[:, i]) for i in range(3)]
        expected = np.stack(np.meshgrid(*self.axes,indexing='ij'),axis=-1).reshape(-1,3)
        if expected.shape != self.X.shape or not np.allclose(expected,self.X,rtol=0,atol=1e-14):
            raise ValueError('ordered tensor observation points required')
        self.order,self.E,self.nu,self.rho = order,E,nu,rho
        self.mu,self.lam = E/(2*(1+nu)),E*nu/((1+nu)*(1-2*nu))
        self.fixed = np.zeros(len(self.X),bool) if fixed is None else np.array(fixed,bool)
        self.q = greville(self.knots)
        self.vg = np.zeros_like(self.q)
        arrays = self.assemble(self.knots, eye(len(self.q),format='csr'))
        for k,v in arrays.items(): setattr(self,k,v)
        self.translation = np.ones(len(self.q))
        self.time,self.steps = 0.,0
        self.support_impulse,self.support_moment = np.zeros(3),np.zeros(3)
        self.configure_support()
        self.update_state()

    def assemble(self, knots, T):
        axes, points, vols = quadrature(knots,self.order)
        Q,G = tensor_basis(knots,axes)
        O,H = tensor_basis(knots,self.axes)
        Q,G,O,H = Q@T,[g@T for g in G],O@T,[g@T for g in H]
        M = (self.rho*(Q.T@Q.multiply(vols[:,None]))).tocsc()
        audit = matrix_audit(M)
        return {'Q':Q.tocsr(),'G':[g.tocsr() for g in G],'O':O.tocsr(),'H':[g.tocsr() for g in H],'points':points,'volumes':vols,'M':M,'factor':splu(M),'T':T,'audit':audit}

    def configure_support(self):
        self.S = self.O[self.fixed]
        self.Z = self.factor.solve(self.S.T.toarray()) if self.S.shape[0] else None
        if self.Z is not None:
            H = self.S@self.Z
            d,U = np.linalg.eigh(H)
            inv = np.zeros_like(d)
            np.divide(1,d,out=inv,where=d>max(d.max()*1e-12,1e-30))
            self.Hinv = (U*inv)@U.T

    @staticmethod
    def check_F(F):
        if len(F)==0:
            return  # A small fragment may have no observation points; quadrature remains nonempty.
        J = np.linalg.det(F)
        if not np.isfinite(J).all() or J.min() <= .1 or J.max() >= 10:
            raise RuntimeError('inadmissible material volume')

    def update_state(self):
        self.x,self.v = self.O@self.q,self.O@self.vg
        self.F = np.stack([g@self.q for g in self.H],axis=2)
        self.check_F(self.F)
        if not np.isfinite(self.q).all() or not np.isfinite(self.vg).all():
            raise RuntimeError('nonfinite mechanical state')

    def energy_force(self,q):
        F = np.stack([g@q for g in self.G],axis=2)
        self.check_F(F)
        e,P = energy_stress(F,self.mu,self.lam)
        force = -sum(g.T@(self.volumes[:,None]*P[:,:,j]) for j,g in enumerate(self.G))
        return float(self.volumes@e),force

    def acceleration(self,q,external=None):
        _,f = self.energy_force(q)
        if external is not None: f += self.O.T@external
        a = self.factor.solve(f)
        reaction = np.zeros_like(f)
        if self.Z is not None:
            lam = -self.Hinv@(self.S@a)
            a += self.Z@lam
            reaction = self.S.T@lam
            if abs(self.S@a).max() > 1e-6: raise RuntimeError('support acceleration residual')
        residual = np.linalg.norm(self.M@a-f-reaction)/max(np.linalg.norm(f+reaction),1e-12)
        if residual > 1e-7: raise RuntimeError('integrated mass solve residual')
        return a,reaction

    def step(self,dt,force0=None,force1=None):
        a,r0 = self.acceleration(self.q,force0)
        vh = self.vg+.5*dt*a
        qn = self.q+dt*vh
        a1,r1 = self.acceleration(qn,force1 if force1 is not None else force0)
        self.check_F(np.stack([g@qn for g in self.H],axis=2))
        self.support_impulse += .5*dt*(self.translation@(r0+r1))
        self.support_moment += .5*dt*(np.cross(self.q,r0).sum(0)+np.cross(qn,r1).sum(0))
        self.q,self.vg = qn,vh+.5*dt*a1
        self.time += dt
        self.steps += 1
        self.update_state()

    def metrics(self):
        U,_ = self.energy_force(self.q)
        x,v = self.Q@self.q,self.Q@self.vg
        m = self.rho*self.volumes
        T = .5*np.sum(m[:,None]*v*v)
        return {'mass':float(m.sum()),'energy':float(U+T),'strain_energy':float(U),'kinetic_energy':float(T),'momentum':np.sum(m[:,None]*v,axis=0),'angular':np.sum(m[:,None]*np.cross(x,v),axis=0)}


class IntegratedCut(IntegratedBody):
    def __init__(self,X,spacing=.0015,h=.003,order=5,E=1e5,nu=.4,rho=1000.,fixed=None):
        meta = block_basis(X,spacing,h)[4]
        super().__init__(meta['knots'],X,order,E,nu,rho,fixed)
        self.meta,self.spacing,self.h = meta,spacing,h
        self.base_ng = len(self.q)
        self.keys,self.history = [],[]
        self.plane,self.plane_data,self.epoch = None,None,0

    def fingerprint(self):
        h = hashlib.sha256()
        h.update(self.q.tobytes());h.update(self.vg.tobytes())
        h.update(str((self.steps,self.epoch,self.keys,self.plane)).encode())
        return h.hexdigest()

    def plane_basis(self,plane):
        old = self.meta['knots'][0]
        if not old[0] < plane < old[-1]: raise RejectedEvent('plane outside body')
        count = np.count_nonzero(abs(old-plane)<1e-12)
        insert = BSpline(old,np.eye(len(old)-3),2).insert_knot(plane,3-count)
        K = insert.c[:len(insert.t)-3]
        E = null_space(K.T)
        knots = [insert.t,*self.meta['knots'][1:]]
        T0 = kron(csr_matrix(K),eye(np.prod(self.meta['dims'][1:])),format='csr')
        return {'knots':knots,'K':K,'E':E,'T0':T0,'dims':[len(t)-3 for t in knots]}

    def enrichment_map(self,data,keys):
        ny,nz = data['dims'][1:]
        rr,cc,vv = [],[],[]
        for col,(j,k,e) in enumerate(keys):
            for i,value in enumerate(data['E'][:,e]):
                if value != 0: rr.append((i*ny+j)*nz+k);cc.append(col);vv.append(value)
        extra = coo_matrix((vv,(rr,cc)),shape=(np.prod(data['dims']),len(keys))).tocsr()
        return hstack([data['T0'],extra],format='csr')

    def propose(self,rectangle,plane=0.):
        if self.plane is not None and abs(plane-self.plane)>1e-12: raise RejectedEvent('one-plane capacity')
        ylo,yhi,zlo,zhi = map(float,rectangle)
        if ylo>yhi or zlo>zhi: raise RejectedEvent('invalid rectangle')
        data = self.plane_data if self.plane_data is not None else self.plane_basis(plane)
        ty,tz = data['knots'][1:]
        add = [(j,k,e) for j in range(len(ty)-3) for k in range(len(tz)-3) for e in range(data['E'].shape[1]) if ty[j]>=ylo-1e-12 and ty[j+3]<=yhi+1e-12 and tz[k]>=zlo-1e-12 and tz[k+3]<=zhi+1e-12]
        keys = sorted(set(self.keys)|set(add))
        if keys==self.keys: return {'noop':True,'fingerprint':self.fingerprint()}
        arrays = self.assemble(data['knots'],self.enrichment_map(data,keys))
        q,v = np.zeros((self.base_ng+len(keys),3)),np.zeros((self.base_ng+len(keys),3))
        q[:self.base_ng],v[:self.base_ng] = self.q[:self.base_ng],self.vg[:self.base_ng]
        lookup = {key:i for i,key in enumerate(keys)}
        for old,key in enumerate(self.keys):
            q[self.base_ng+lookup[key]],v[self.base_ng+lookup[key]] = self.q[self.base_ng+old],self.vg[self.base_ng+old]
        x,vel = arrays['O']@q,arrays['O']@v
        F = np.stack([g@q for g in arrays['H']],axis=2)
        Fq = np.stack([g@q for g in arrays['G']],axis=2)
        self.check_F(Fq)
        energy = arrays['volumes']@energy_stress(Fq,self.mu,self.lam)[0]+.5*self.rho*np.sum(arrays['volumes'][:,None]*(arrays['Q']@v)**2)
        old = self.metrics()
        change = {'x':float(abs(x-self.x).max()),'v':float(abs(vel-self.v).max()),'F':float(abs(F-self.F).max()),'energy':float(energy-old['energy']),'energy_before':old['energy'],'mass':float(self.rho*arrays['volumes'].sum()-old['mass'])}
        if change['x']>1e-11 or change['v']>1e-10 or change['F']>1e-10 or abs(change['energy'])>max(1e-12,abs(old['energy'])*1e-8) or abs(change['mass'])>old['mass']*1e-6:
            raise RejectedEvent('integration/topology insertion changed existing mechanical state',change)
        return {'noop':False,'arrays':arrays,'q':q,'vg':v,'data':data,'keys':keys,'plane':plane,'rectangle':list(rectangle),'transfer':change,'fingerprint':self.fingerprint()}

    def commit(self,p):
        if p['fingerprint']!=self.fingerprint(): raise RejectedEvent('stale proposal')
        if p['noop']: return False
        for k,v in p['arrays'].items(): setattr(self,k,v)
        for k in ['q','vg','keys','plane']: setattr(self,k,p[k])
        self.plane_data,self.knots = p['data'],p['data']['knots']
        self.translation = np.r_[np.ones(self.base_ng),np.zeros(len(self.keys))]
        self.configure_support()
        self.epoch += 1
        self.history.append({'fixture_only':True,'plane':self.plane,'rectangle':p['rectangle'],'keys_after':len(self.keys),'paid_fracture_area':0.})
        self.update_state()
        return True

    def face_jump(self,yz):
        if self.plane_data is None: return np.zeros((len(yz),3))
        q = (self.T@self.q).reshape(*self.plane_data['dims'],3)
        ix = int(np.flatnonzero(abs(self.knots[0]-self.plane)<1e-12)[0]-1)
        Y = values_gradient(self.knots[1],np.asarray(yz)[:,0])[0].toarray()
        Z = values_gradient(self.knots[2],np.asarray(yz)[:,1])[0].toarray()
        return np.einsum('nj,nk,jkc->nc',Y,Z,q[ix+1]-q[ix])

    def split_knots(self):
        if self.plane is None: raise ValueError('no cut')
        t = self.knots[0]
        return [np.r_[t[t<self.plane],np.repeat(self.plane,3)],*self.knots[1:]],[np.r_[np.repeat(self.plane,3),t[t>self.plane]],*self.knots[1:]]

    def set_full_piece_state(self,left,right):
        if self.plane_data is None or len(self.keys)!=self.plane_data['E'].shape[1]*np.prod(self.meta['dims'][1:]): raise ValueError('full prescribed topology required')
        self.q = np.linalg.solve(self.T.toarray(),np.concatenate([left.q,right.q]))
        self.vg = np.linalg.solve(self.T.toarray(),np.concatenate([left.vg,right.vg]))
        self.update_state()

    def save(self,path):
        meta = {'schema':1,'spacing':self.spacing,'h':self.h,'order':self.order,'E':self.E,'nu':self.nu,'rho':self.rho,'plane':self.plane,'time':self.time,'steps':self.steps,'epoch':self.epoch,'history':self.history}
        np.savez_compressed(path,metadata=json.dumps(meta,allow_nan=False),X=self.X,q=self.q,vg=self.vg,x=self.x,v=self.v,F=self.F,keys=np.asarray(self.keys,dtype=int).reshape(-1,3),fixed=self.fixed,support_impulse=self.support_impulse,support_moment=self.support_moment)

    @classmethod
    def restore(cls,path):
        with np.load(path,allow_pickle=False) as s:
            meta = json.loads(str(s['metadata']))
            if meta['schema']!=1: raise ValueError('unsupported checkpoint')
            b = cls(s['X'],**{k:meta[k] for k in ['spacing','h','order','E','nu','rho']},fixed=s['fixed'])
            for e in meta['history']:
                if not e['fixture_only'] or e['paid_fracture_area']!=0: raise ValueError('invalid fixture history')
                b.commit(b.propose(e['rectangle'],e['plane']))
            if b.history!=meta['history'] or b.epoch!=meta['epoch'] or b.plane!=meta['plane'] or b.keys!=[tuple(k) for k in s['keys']]: raise ValueError('checkpoint history mismatch')
            if b.q.shape!=s['q'].shape or b.vg.shape!=s['vg'].shape: raise ValueError('checkpoint state shape mismatch')
            b.q,b.vg = s['q'].copy(),s['vg'].copy()
            b.time,b.steps = meta['time'],meta['steps']
            b.support_impulse,b.support_moment = s['support_impulse'].copy(),s['support_moment'].copy()
            b.update_state();b.energy_force(b.q)
            if max(abs(getattr(b,k)-s[k]).max() for k in ['x','v','F'])>1e-10: raise ValueError('checkpoint field mismatch')
            return b
