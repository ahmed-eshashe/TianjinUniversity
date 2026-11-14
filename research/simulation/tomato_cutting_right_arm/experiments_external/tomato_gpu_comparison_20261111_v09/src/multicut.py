"""Persistent, carried-state fragments with one active partial incision per fragment.
Reference-axis prescribed topology only; no contact or paid fracture law.
"""
import copy,hashlib,json
import numpy as np
from scipy.interpolate import BSpline
from scipy.linalg import null_space
from scipy.sparse import csr_matrix,eye,kron,hstack,coo_matrix
from integrated_cut import IntegratedBody,IntegratedCut,RejectedEvent,values_gradient
from block_basis import block_basis
from reference import energy_stress
from continuous_volume import box_certificate


def kron3(mats):return kron(kron(mats[0],mats[1]),mats[2],format='csr')
def maximum(a):return float(np.max(abs(a),initial=0))
def full_rectangle(piece,axis):
    others=[i for i in range(3) if i!=axis]
    return [value for i in others for value in (float(piece.meta['knots'][i][0]),float(piece.meta['knots'][i][-1]))]


class CutPiece(IntegratedCut):
    def __init__(self,knots,X,indices,order=5,E=1e5,nu=.4,rho=1000.,fixed=None):
        IntegratedBody.__init__(self,knots,X,order,E,nu,rho,fixed)
        self.meta={'knots':[np.array(k) for k in knots],'dims':[len(k)-3 for k in knots]}
        self.indices=np.array(indices,int);self.base_ng=len(self.q)
        self.keys,self.history=[],[];self.plane,self.axis,self.plane_data=None,None,None;self.epoch=0

    def plane_basis_axis(self,axis,plane):
        if axis not in [0,1,2]:raise RejectedEvent('only reference-axis normals are implemented')
        old=self.meta['knots'][axis]
        if not old[0]<plane<old[-1]:raise RejectedEvent('plane outside this fragment')
        count=np.count_nonzero(abs(old-plane)<1e-12)
        bs=BSpline(old,np.eye(len(old)-3),2).insert_knot(plane,3-count)
        K=bs.c[:len(bs.t)-3];E=null_space(K.T);knots=list(self.meta['knots']);knots[axis]=bs.t
        mats=[eye(n,format='csr') for n in self.meta['dims']];mats[axis]=csr_matrix(K)
        return {'knots':knots,'dims':[len(k)-3 for k in knots],'axis':axis,'K':K,'E':E,'T0':kron3(mats)}

    def enrichment_map(self,data,keys):
        axis=data['axis'];others=[i for i in range(3) if i!=axis];rr=[];cc=[];vv=[]
        for col,(j,k,e) in enumerate(keys):
            for i,value in enumerate(data['E'][:,e]):
                if value==0:continue
                index=[0,0,0];index[axis]=i;index[others[0]]=j;index[others[1]]=k
                rr.append(np.ravel_multi_index(tuple(index),data['dims']));cc.append(col);vv.append(value)
        extra=coo_matrix((vv,(rr,cc)),shape=(int(np.prod(data['dims'])),len(keys))).tocsr()
        return hstack([data['T0'],extra],format='csr')

    def propose(self,rectangle,plane=0.,axis=0):
        if self.plane is not None and (axis!=self.axis or abs(plane-self.plane)>1e-12):
            raise RejectedEvent('one active partial incision per connected fragment; finish or stop before intersecting it')
        lo,hi,lo2,hi2=map(float,rectangle)
        if lo>hi or lo2>hi2:raise RejectedEvent('invalid rectangle')
        data=self.plane_data if self.plane_data is not None else self.plane_basis_axis(axis,plane)
        others=[i for i in range(3) if i!=axis];ty,tz=[data['knots'][i] for i in others]
        add=[(j,k,e) for j in range(len(ty)-3) for k in range(len(tz)-3) for e in range(data['E'].shape[1]) if ty[j]>=lo-1e-12 and ty[j+3]<=hi+1e-12 and tz[k]>=lo2-1e-12 and tz[k+3]<=hi2+1e-12]
        keys=sorted(set(self.keys)|set(add))
        if keys==self.keys:return {'noop':True,'fingerprint':self.fingerprint()}
        arrays=self.assemble(data['knots'],self.enrichment_map(data,keys));q=np.zeros((self.base_ng+len(keys),3));v=np.zeros_like(q)
        q[:self.base_ng],v[:self.base_ng]=self.q[:self.base_ng],self.vg[:self.base_ng];lookup={k:i for i,k in enumerate(keys)}
        for old,key in enumerate(self.keys):q[self.base_ng+lookup[key]],v[self.base_ng+lookup[key]]=self.q[self.base_ng+old],self.vg[self.base_ng+old]
        x,vel=arrays['O']@q,arrays['O']@v;F=np.stack([g@q for g in arrays['H']],axis=2);Fq=np.stack([g@q for g in arrays['G']],axis=2);self.check_F(Fq)
        energy=float(arrays['volumes']@energy_stress(Fq,self.mu,self.lam)[0]+.5*self.rho*np.sum(arrays['volumes'][:,None]*(arrays['Q']@v)**2));old=self.metrics()
        change={'x':maximum(x-self.x),'v':maximum(vel-self.v),'F':maximum(F-self.F),'energy':energy-old['energy'],'energy_before':old['energy'],'mass':float(self.rho*arrays['volumes'].sum()-old['mass'])}
        if change['x']>1e-11 or change['v']>1e-10 or change['F']>1e-10 or abs(change['energy'])>max(1e-12,abs(old['energy'])*1e-8) or abs(change['mass'])>old['mass']*1e-6:raise RejectedEvent('cut insertion changed mechanical state',change)
        return {'noop':False,'arrays':arrays,'q':q,'vg':v,'data':data,'keys':keys,'plane':plane,'axis':axis,'rectangle':list(rectangle),'transfer':change,'fingerprint':self.fingerprint()}

    def commit(self,p):
        changed=super().commit(p)
        if changed:self.axis=p['axis'];self.history[-1]['axis']=self.axis
        return changed

    def face_jump(self,points):
        if self.plane is None:return np.zeros((len(points),3))
        q=(self.T@self.q).reshape(*self.plane_data['dims'],3);ix=int(np.flatnonzero(abs(self.knots[self.axis]-self.plane)<1e-12)[0]-1)
        delta=np.take(q,ix+1,axis=self.axis)-np.take(q,ix,axis=self.axis);others=[i for i in range(3) if i!=self.axis]
        Y=values_gradient(self.knots[others[0]],np.asarray(points)[:,0])[0].toarray();Z=values_gradient(self.knots[others[1]],np.asarray(points)[:,1])[0].toarray()
        return np.einsum('ni,nj,ijc->nc',Y,Z,delta)

    def completed(self):
        return self.plane is not None and len(self.keys)==self.plane_data['E'].shape[1]*np.prod([self.meta['dims'][i] for i in range(3) if i!=self.axis])

    def partitions(self):
        if not self.completed():raise ValueError('partial incision retains one connected fragment')
        axis=self.axis;t=self.knots[axis];left=list(self.knots);right=list(self.knots)
        left[axis]=np.r_[t[t<self.plane],np.repeat(self.plane,3)];right[axis]=np.r_[np.repeat(self.plane,3),t[t>self.plane]]
        shape=self.plane_data['dims'];Q=(self.T@self.q).reshape(*shape,3);V=(self.T@self.vg).reshape(*shape,3);nleft=len(left[axis])-3
        children=[]
        for index,knots in enumerate([left,right]):
            mask=(self.X[:,axis]<self.plane) if index==0 else (self.X[:,axis]>=self.plane)
            child=CutPiece(knots,self.X[mask],self.indices[mask],self.order,self.E,self.nu,self.rho,self.fixed[mask])
            sel=[slice(None)]*4;sel[axis]=slice(0,nleft) if index==0 else slice(nleft,None)
            child.q=Q[tuple(sel)].reshape(-1,3).copy();child.vg=V[tuple(sel)].reshape(-1,3).copy();child.time,child.steps=self.time,self.steps;child.update_state();child.energy_force(child.q)
            children.append(child)
        before=self.metrics();after=sum_metrics(children);assembled={key:np.zeros_like(getattr(self,key)) for key in ['x','v','F']}
        for child in children:
            mask=np.isin(self.indices,child.indices)
            for key in assembled:assembled[key][mask]=getattr(child,key)
        errors={key:maximum(assembled[key]-getattr(self,key)) for key in assembled};errors.update(mass=after['mass']-before['mass'],energy=after['energy']-before['energy'],momentum=float(np.linalg.norm(after['momentum']-before['momentum'])),angular=float(np.linalg.norm(after['angular']-before['angular'])))
        if errors['x']>1e-11 or errors['v']>1e-10 or errors['F']>1e-10 or abs(errors['mass'])>before['mass']*1e-6 or abs(errors['energy'])>max(1e-12,abs(before['energy'])*1e-8) or errors['momentum']>1e-9 or errors['angular']>1e-10:raise RejectedEvent('carried-state partition changed mechanics',errors)
        return children,errors


def sum_metrics(pieces):
    items=[p.metrics() for p in pieces]
    return {key:sum((item[key] for item in items),np.zeros(3) if key in ['momentum','angular'] else 0.) for key in items[0]}


def volume_certificates(piece):
    if piece.plane is None:return [box_certificate(piece.knots,piece.q)]
    axis=piece.axis;t=piece.knots[axis];lk=list(piece.knots);rk=list(piece.knots);lk[axis]=np.r_[t[t<piece.plane],np.repeat(piece.plane,3)];rk[axis]=np.r_[np.repeat(piece.plane,3),t[t>piece.plane]]
    Q=(piece.T@piece.q).reshape(*piece.plane_data['dims'],3);sel=[slice(None)]*4;n=len(lk[axis])-3;sel[axis]=slice(0,n);a=Q[tuple(sel)].reshape(-1,3);sel[axis]=slice(n,None);b=Q[tuple(sel)].reshape(-1,3)
    return [box_certificate(lk,a),box_certificate(rk,b)]


class MultiCut:
    def __init__(self,X,spacing=.0015,h=.003,order=5,E=1e5,nu=.4,rho=1000.,fixed=None,max_cuts=4):
        self.X=np.array(X);self.config=dict(spacing=spacing,h=h,order=order,E=E,nu=nu,rho=rho,max_cuts=max_cuts);self.fixed=np.zeros(len(X),bool) if fixed is None else np.array(fixed,bool)
        knots=block_basis(X,spacing,h)[4]['knots'];self.pieces={'root':CutPiece(knots,X,np.arange(len(X)),order,E,nu,rho,self.fixed)};self.cut_count=0;self.events=[];self.time=0.;self.steps=0;self.archived_support_impulse=np.zeros(3);self.archived_support_moment=np.zeros(3)

    def fingerprint(self):
        h=hashlib.sha256();h.update(str((self.time,self.steps,self.cut_count,self.events,self.config)).encode());h.update(self.archived_support_impulse.tobytes());h.update(self.archived_support_moment.tobytes())
        for key,piece in self.pieces.items():h.update(key.encode());h.update(piece.fingerprint().encode());h.update(str(piece.axis).encode());h.update(piece.support_impulse.tobytes());h.update(piece.support_moment.tobytes())
        return h.hexdigest()

    def observations(self):
        x=np.zeros_like(self.X);v=np.zeros_like(self.X);F=np.zeros((len(self.X),3,3))
        for p in self.pieces.values():x[p.indices]=p.x;v[p.indices]=p.v;F[p.indices]=p.F
        return x,v,F

    def metrics(self):
        m=sum_metrics(list(self.pieces.values()));m['support_impulse']=self.archived_support_impulse+sum((p.support_impulse for p in self.pieces.values()),np.zeros(3));m['support_moment']=self.archived_support_moment+sum((p.support_moment for p in self.pieces.values()),np.zeros(3));return m

    def propose(self,piece_id,axis,plane,rectangle):
        if piece_id not in self.pieces:raise RejectedEvent('unknown or retired fragment')
        old=self.pieces[piece_id]
        if old.plane is None and self.cut_count>=self.config['max_cuts']:raise RejectedEvent('four-cut capacity exhausted; no history discarded')
        p=old.propose(rectangle,plane,axis)
        if p['noop']:return {'noop':True,'fingerprint':self.fingerprint()}
        trial=copy.copy(old);trial.history=copy.deepcopy(old.history);trial.commit(p)
        certs=volume_certificates(trial)
        if not all(c['passed'] for c in certs):raise RejectedEvent('continuous volume check failed',{'certificates':certs})
        children,partition=(trial.partitions() if trial.completed() else (None,None))
        return {'noop':False,'fingerprint':self.fingerprint(),'piece_id':piece_id,'trial':trial,'children':children,'new_cut':old.plane is None,'insertion':p['transfer'],'partition':partition,'event':{'piece_id':piece_id,'axis':axis,'plane':float(plane),'rectangle':list(rectangle),'complete':children is not None,'fixture_only':True,'paid_fracture_area':0.}}

    def commit(self,p):
        if p['fingerprint']!=self.fingerprint():raise RejectedEvent('stale multicut proposal')
        if p['noop']:return False
        key=p['piece_id'];old=self.pieces[key]
        if p['children'] is None:self.pieces[key]=p['trial']
        else:
            self.archived_support_impulse+=old.support_impulse;self.archived_support_moment+=old.support_moment
            del self.pieces[key]
            for side,child in zip(['L','R'],p['children']):self.pieces[key+side]=child
        self.cut_count+=int(p['new_cut']);self.events.append(copy.deepcopy(p['event']));return True

    def step(self,dt,force0=None,force1=None):
        snapshots={key:{field:getattr(p,field).copy() if isinstance(getattr(p,field),np.ndarray) else getattr(p,field) for field in ['q','vg','time','steps','support_impulse','support_moment']} for key,p in self.pieces.items()}
        try:
            for p in self.pieces.values():p.step(dt,None if force0 is None else force0[p.indices],None if force1 is None else force1[p.indices])
        except Exception:
            for key,p in self.pieces.items():
                for field,value in snapshots[key].items():setattr(p,field,value)
                p.update_state()
            raise
        self.time+=dt;self.steps+=1

    def save(self,path):
        meta={'schema':1,'config':self.config,'events':self.events,'cut_count':self.cut_count,'time':self.time,'steps':self.steps,'piece_ids':list(self.pieces)}
        arrays={'metadata':json.dumps(meta,allow_nan=False),'X':self.X,'fixed':self.fixed,'archived_support_impulse':self.archived_support_impulse,'archived_support_moment':self.archived_support_moment}
        for key,p in self.pieces.items():
            for field in ['q','vg','x','v','F','support_impulse','support_moment']:arrays[key+'_'+field]=getattr(p,field)
        np.savez_compressed(path,**arrays)

    @classmethod
    def restore(cls,path):
        with np.load(path,allow_pickle=False) as z:
            meta=json.loads(str(z['metadata']))
            if meta['schema']!=1:raise ValueError('checkpoint schema')
            b=cls(z['X'],fixed=z['fixed'],**meta['config'])
            for e in meta['events']:
                if not e['fixture_only'] or e['paid_fracture_area']!=0:raise ValueError('not a prescribed unit checkpoint')
                b.commit(b.propose(e['piece_id'],e['axis'],e['plane'],e['rectangle']))
            if b.events!=meta['events'] or list(b.pieces)!=meta['piece_ids'] or b.cut_count!=meta['cut_count']:raise ValueError('checkpoint topology mismatch')
            for key,p in b.pieces.items():
                if p.q.shape!=z[key+'_q'].shape:raise ValueError('checkpoint state shape')
                p.q=z[key+'_q'].copy();p.vg=z[key+'_vg'].copy();p.time=meta['time'];p.steps=meta['steps'];p.support_impulse=z[key+'_support_impulse'].copy();p.support_moment=z[key+'_support_moment'].copy();p.update_state();p.energy_force(p.q)
                if max(maximum(getattr(p,f)-z[key+'_'+f]) for f in ['x','v','F'])>1e-10:raise ValueError('checkpoint derived state mismatch')
            b.archived_support_impulse=z['archived_support_impulse'].copy();b.archived_support_moment=z['archived_support_moment'].copy();b.time=meta['time'];b.steps=meta['steps'];return b
