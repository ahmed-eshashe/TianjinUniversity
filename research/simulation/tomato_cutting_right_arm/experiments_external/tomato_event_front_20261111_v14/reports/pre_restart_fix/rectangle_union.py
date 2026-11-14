"""Exact axis-aligned rectangle coverage, without filling unvisited gaps."""
import numpy as np

TOL = 1e-12

def union_area(rectangles):
    if not rectangles:return 0.
    r=np.asarray(rectangles,float).reshape(-1,4)
    xs=np.unique(r[:,:2]);area=0.
    for lo,hi in zip(xs[:-1],xs[1:]):
        mid=.5*(lo+hi);intervals=sorted((a,b) for x,y,a,b in r if x<=mid<=y and b>a)
        length=0.;end=-np.inf
        for a,b in intervals:
            length+=max(0.,b-max(a,end));end=max(end,b)
        area+=(hi-lo)*length
    return float(area)

def covered(rectangle,rectangles):
    x0,x1,y0,y1=rectangle
    r=[(max(x0,a),min(x1,b),max(y0,c),min(y1,d)) for a,b,c,d in rectangles if b>x0 and a<x1 and d>y0 and c<y1]
    if not r:return False
    xs=sorted(set([x0,x1]+[z for a,b,_,_ in r for z in (a,b)]))
    for lo,hi in zip(xs[:-1],xs[1:]):
        if hi-lo<=TOL:continue
        mid=.5*(lo+hi);end=y0
        for a,b in sorted((c,d) for x,y,c,d in r if x<=mid<=y):
            if a>end+TOL:return False
            end=max(end,b)
        if end<y1-TOL:return False
    return True
