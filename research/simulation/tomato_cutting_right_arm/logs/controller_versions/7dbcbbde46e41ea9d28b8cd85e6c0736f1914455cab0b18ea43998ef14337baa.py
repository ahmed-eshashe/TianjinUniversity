"""Geometry shared by the disposable scene setup and offline clearance screen."""
import numpy as np
from scipy.spatial import ConvexHull

def long_edge_angle(points):
    hull=np.asarray(points)[ConvexHull(np.asarray(points)[:,:2]).vertices,:2]
    edges=np.roll(hull,-1,axis=0)-hull
    best=None
    for angle in np.arctan2(edges[:,1],edges[:,0]):
        c,s=np.cos(angle),np.sin(angle)
        extents=np.ptp(hull@np.array([[c,-s],[s,c]]),axis=0)
        area=float(np.prod(extents))
        if best is None or area<best[0]:best=(area,angle+(np.pi/2 if extents[1]>extents[0] else 0))
    return float(best[1]%np.pi)

def align_board(board_points,board_matrix,counter_points,counter_matrix):
    world=np.asarray(board_points)@board_matrix[:3,:3].T+board_matrix[:3,3]
    counter=np.asarray(counter_points)@counter_matrix[:3,:3].T+counter_matrix[:3,3]
    delta=(long_edge_angle(counter)-long_edge_angle(world)+np.pi/2)%np.pi-np.pi/2
    c,s=np.cos(delta),np.sin(delta);rotation=np.array([[c,-s,0],[s,c,0],[0,0,1]])
    pivot=(world.min(0)+world.max(0))/2
    result=board_matrix.copy();result[:3,:3]=rotation@result[:3,:3]
    result[:3,3]=pivot+rotation@(board_matrix[:3,3]-pivot)
    error=abs((long_edge_angle(np.asarray(board_points)@result[:3,:3].T+result[:3,3])-long_edge_angle(counter)+np.pi/2)%np.pi-np.pi/2)
    return result,float(np.rad2deg(error))
