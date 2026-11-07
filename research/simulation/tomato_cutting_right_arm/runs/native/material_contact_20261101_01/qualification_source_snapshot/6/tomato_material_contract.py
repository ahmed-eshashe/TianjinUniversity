"""Host validation for the limited native one-pair-per-patch material operator."""
import math

def validate_registry(pairs,rest,stiffness,laws,history,eligible,colors,node_count):
 n=len(pairs)
 if not n or any(len(x)!=n for x in (rest,stiffness,laws,history,eligible)):raise ValueError('Complete patch registry required')
 seen=set()
 for pair,r,k,law,h,ok in zip(pairs,rest,stiffness,laws,history,eligible):
  if len(pair)!=2 or any(type(i)is not int or not 0<=i<node_count for i in pair) or pair[0]==pair[1] or tuple(sorted(pair)) in seen:raise ValueError('Unique one-pair patch required')
  seen.add(tuple(sorted(pair)))
  if colors[pair[0]]==colors[pair[1]]:raise ValueError('Cohesive neighbors require different VBD colors')
  if len(r)!=3 or len(k)!=3 or any(len(row)!=3 for row in k) or len(law)!=3 or len(h)!=2:raise ValueError('Invalid patch dimensions')
  if not all(math.isfinite(x) for x in [*r,*law,*h,*[x for row in k for x in row]]):raise ValueError('Finite material data required')
  if law[0]<=0 or not 0<law[1]<law[2] or h[0]<0 or not 0<=h[1]<=1 or ok not in (0,1):raise ValueError('Invalid law or history')
  if max(abs(k[i][j]-k[j][i]) for i in range(3) for j in range(3))>1e-12 or any(k[0][j]!=0 or k[j][0]!=0 for j in (1,2)):raise ValueError('Symmetric uncoupled-normal material required')
  if min(k[0][0],k[1][1],k[2][2])<=0 or k[1][1]*k[2][2]-k[1][2]**2<=0:raise ValueError('Positive definite undamaged material required')
 return True
