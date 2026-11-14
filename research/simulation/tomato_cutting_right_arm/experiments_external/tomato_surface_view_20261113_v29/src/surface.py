"""Appearance-only surface driven by particle motion and actual broken bonds.
No topology, masses, forces, actions, contact or failure laws are changed.
"""
from pathlib import Path
import numpy as np

class TomatoSurface:
    def __init__(self,path):
        z=np.load(path)
        for key in z.files:setattr(self,key,z[key])
        self.last_alive=None
        self.skin_faces=self.faces[self.skin]
        self.skin_colors=self.colors(self.vertices,skin=True)
        self.flesh_colors=self.colors(self.vertices,skin=False)
        self.w=None
        self.outer_ids=np.unique(self.skin_faces)
        center=self.particle_rest.mean(0);radii=np.ptp(self.vertices,axis=0)*.5
        self.rest_normal=(self.vertices[self.outer_ids]-center)/(radii*radii)
        self.rest_normal/=np.linalg.norm(self.rest_normal,axis=1)[:,None]

    def update_topology(self,alive):
        if self.last_alive is not None and np.array_equal(alive,self.last_alive):return False
        self.last_alive=alive.copy()
        labels=np.broadcast_to(np.arange(8),(len(self.unique),8)).copy()
        active=(self.local_bonds>=0)&alive[np.maximum(self.local_bonds,0)].astype(bool)
        for _ in range(8):
            before=labels.copy()
            for k,(a,b) in enumerate(self.pairs):
                value=np.minimum(labels[:,a],labels[:,b]);labels[:,a]=np.where(active[:,k],value,labels[:,a]);labels[:,b]=np.where(active[:,k],value,labels[:,b])
            if np.array_equal(labels,before):break
        roots=labels[self.group,self.owner_slot]
        keep=labels[self.group]==roots[:,None]
        self.w=self.weights[self.group]*keep
        self.w/=self.w.sum(1,keepdims=True)
        self.slots=self.group*8+roots
        self.indices=self.support[self.group]
        ids=self.outer_ids;w=self.w[ids];reference=self.particle_rest[self.indices[ids]];mean=np.einsum('vi,vij->vj',w,reference);self.normal_reference=reference-mean[:,None,:]
        covariance=np.einsum('vi,vij,vik->vjk',w,self.normal_reference,self.normal_reference)
        self.normal_inverse=np.linalg.inv(covariance+1e-9*np.eye(3)[None,:,:])
        visible=(~self.skin)&(alive[np.maximum(self.face_bond,0)]==0)
        self.visible_cut_ids=np.flatnonzero(visible)
        self.cut_faces=self.faces[visible]
        # Cosmetic seeds appear only on actual exposed fracture triangles.
        rest=self.vertices[self.cut_faces];centers=rest.mean(1);area=np.linalg.norm(np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]),axis=1)*.5
        r=np.linalg.norm(centers[:,[0,2]],axis=1)
        mask=(area>3e-6)&(r>.007)&(r<.023)&(centers[:,1]>.008)&(centers[:,1]<.044)&((self.visible_cut_ids*73+19)%31==0)
        self.seed_faces=self.cut_faces[mask]
        return True

    def points(self,x):
        delta=x-self.particle_rest
        return self.vertices+np.einsum('vi,vij->vj',self.w,delta[self.indices])

    def normals(self,points,x=None):
        # Smooth ellipsoidal skin normals, transported by a local deformation fit.
        # This only changes shading; no surface position or solver state is moved.
        result=np.zeros_like(self.vertices)
        if x is None:
            result[self.outer_ids]=self.rest_normal
            return result
        ids=self.outer_ids;displacement=(x-self.particle_rest)[self.indices[ids]]
        covariance=np.einsum('vi,vij,vik->vjk',self.w[ids],displacement,self.normal_reference)
        deformation=np.eye(3)[None,:,:]+covariance@self.normal_inverse
        try:normal=np.linalg.solve(np.swapaxes(deformation,1,2),self.rest_normal[:,:,None])[:,:,0]
        except np.linalg.LinAlgError:normal=self.rest_normal.copy()
        normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12);result[ids]=normal
        return result

    def seeds(self,points):
        f=self.seed_faces
        if not len(f):return np.empty((0,3),np.float32),np.empty((0,3),np.int32)
        p=points[f];center=p.mean(1);u=p[:,1]-p[:,0];u/=np.maximum(np.linalg.norm(u,axis=1)[:,None],1e-12);normal=np.cross(u,p[:,2]-p[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12);v=np.cross(normal,u);angle=np.linspace(0,2*np.pi,13)[:-1]
        rim=center[:,None,:]+.0007*np.cos(angle)[None,:,None]*u[:,None,:]+.00038*np.sin(angle)[None,:,None]*v[:,None,:]+.000025*normal[:,None,:]
        dome=center+.00014*normal
        vertices=np.concatenate([dome[:,None,:],rim],axis=1).reshape(-1,3).astype(np.float32)
        triangles=np.array([[i*13,i*13+1+k,i*13+1+(k+1)%12] for i in range(len(f)) for k in range(12)],np.int32)
        return vertices,triangles

    @staticmethod
    def colors(p,skin):
        # Subtle natural variation rather than a flat plastic red.
        if skin:
            noise=.035*np.sin(370*p[:,0]+29*p[:,1])*np.cos(410*p[:,2])+.018*np.sin(1300*p[:,0]+900*p[:,2])
            warm=np.clip((p[:,1]-.035)/.02,0,1)
            return np.c_[.48*(1+noise)+.035*warm,.014+.008*warm+.002*noise,.007+.003*warm].astype(np.float32)
        x,y,z=p.T;r=np.hypot(x,z);angle=np.arctan2(z,x);gel=np.clip((.8-np.abs(np.sin(3*angle)))*2,0,1)*np.exp(-((r-.015)/.008)**4)*np.exp(-((y-.026)/.024)**4)
        flesh=np.tile([.66,.065,.045],(len(p),1));flesh= flesh*(1-gel[:,None]) + gel[:,None]*[.66,.22,.065]
        pith=np.exp(-(r/.006)**4);flesh=flesh*(1-.45*pith[:,None])+.45*pith[:,None]*[.85,.39,.20]
        return flesh.astype(np.float32)


def foliage(rest):
    """Decorative calyx and curved stem, attached to the upper particle group."""
    top=np.array([0.,rest[:,1].max()+.003,0.]);verts=[];faces=[];colors=[]
    # Six tapered, gently curling sepals.
    for leaf in range(6):
        theta=2*np.pi*leaf/6+.3;axis=np.array([np.cos(theta),0,np.sin(theta)]);side=np.array([-np.sin(theta),0,np.cos(theta)])
        base=len(verts)
        for j in range(8):
            t=j/7;length=.0105*(.92+.12*np.sin(leaf*2.1));width=.0024*np.sin(np.pi*t)**.8
            center=top+axis*(.0005+length*t)+[0,.0005+.0008*np.sin(np.pi*t)-.0035*t*t,0]
            for s in [-1,0,1]:
                point=center+s*width*side;point[1]+=.0006*(1-abs(s))*np.sin(np.pi*t);verts.append(point);colors.append([.045+.025*(1-t),.18+.08*(1-t),.009])
        for j in range(7):
            for k in range(2):a=base+j*3+k;faces.extend([[a,a+3,a+1],[a+1,a+3,a+4]])
    # Slightly bent stem, not a physics object.
    base=len(verts)
    for j in range(7):
        t=j/6;center=top+[.0022*t*t,.007*t,.001*t];radius=.00125*(1-.45*t)
        for k in range(10):
            angle=2*np.pi*k/10;verts.append(center+radius*np.array([np.cos(angle),0,np.sin(angle)]));colors.append([.08,.24-.05*t,.018])
    for j in range(6):
        for k in range(10):a=base+j*10+k;b=base+j*10+(k+1)%10;faces.extend([[a,a+10,b],[b,a+10,b+10]])
    return np.asarray(verts,np.float32),np.asarray(faces,np.int32),(np.asarray(colors,np.float32)*[.7,.5,.7]).astype(np.float32),top
