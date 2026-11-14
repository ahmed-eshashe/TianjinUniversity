"""Independent graph oracle for the actual transfer connectivity."""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from reference import stencil,compatible

def components(X,codes,h):
 ids,w,g,nodes=stencil(X,h);N=len(nodes);n=len(X);active,slots=np.unique(codes,return_inverse=True);K=len(active)
 keep=w>1e-12;p=np.broadcast_to(np.arange(n)[:,None],ids.shape)[keep];q=(n+slots[:,None]*N+ids)[keep]
 occupied=np.zeros(K*N,bool);occupied[q-n]=True;occupied=occupied.reshape(K,N)
 rows=[p];cols=[q]
 for a in range(K):
  for b in range(a+1,K):
   if compatible(int(active[a]),int(active[b])):
    joint=np.where(occupied[a]&occupied[b])[0];rows.append(n+a*N+joint);cols.append(n+b*N+joint)
 graph=coo_matrix((np.ones(sum(len(x) for x in rows),dtype=bool),(np.concatenate(rows),np.concatenate(cols))),shape=(n+K*N,n+K*N)).tocsr()
 _,labels=connected_components(graph,directed=False);unique,compact=np.unique(labels[:n],return_inverse=True)
 return compact,{'components':len(unique),'sizes':np.bincount(compact).tolist(),'active_codes':active.tolist(),'occupied_node_states':int(occupied.sum()),'graph_edges':int(graph.nnz)}
