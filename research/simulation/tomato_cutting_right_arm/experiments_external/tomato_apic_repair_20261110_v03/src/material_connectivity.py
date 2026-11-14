"""Persistent whole-fragment IDs supplement, rather than replace, partial-cut codes.
Reference-neighbor edges can be removed by committed history, never rebuilt from
current spatial proximity. This prevents unlabelled outer material rebonding.
"""
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from reference import compatible

def fragments(X,codes,spacing):
 pairs=cKDTree(X).query_pairs(spacing*1.01,output_type='ndarray')
 good=np.array([compatible(int(codes[a]),int(codes[b])) for a,b in pairs]);pairs=pairs[good];rows=pairs[:,0];cols=pairs[:,1];G=coo_matrix((np.ones(len(rows),bool),(rows,cols)),shape=(len(X),len(X))).tocsr();num,lab=connected_components(G,directed=False)
 if num>81:raise RuntimeError('fragment capacity exceeded')
 keys=lab*81+np.asarray(codes)
 if len(np.unique(keys))>81:raise RuntimeError('logical-state capacity exceeded')
 return lab,keys
