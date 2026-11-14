"""Independent scalar determinant polynomial bound for a full nodal trial."""
from tomato_wrench_contract import dot,cross

def fraction(points,displacements,reference_volume,floor=.1):
 if reference_volume<=0:raise ValueError('Positive reference volume required')
 def difference(a,b):return tuple(x-y for x,y in zip(a,b))
 d=[difference(points[i],points[0]) for i in (1,2,3)];e=[difference(displacements[i],displacements[0]) for i in (1,2,3)]
 def det(a,b,c):return dot(a,cross(b,c))/(6*reference_volume)
 j=det(*d);c1=det(e[0],d[1],d[2])+det(d[0],e[1],d[2])+det(d[0],d[1],e[2]);c2=det(e[0],e[1],d[2])+det(e[0],d[1],e[2])+det(d[0],e[1],e[2]);c3=det(*e)
 if j<=floor:raise ValueError('Starting volume is already infeasible')
 bound=abs(c1)+abs(c2)+abs(c3);alpha=1. if j-bound>floor else .9*(j-floor)/bound
 return dict(fraction=alpha,polynomial=[j,c1,c2,c3],lower_bound=j-bound*alpha)
