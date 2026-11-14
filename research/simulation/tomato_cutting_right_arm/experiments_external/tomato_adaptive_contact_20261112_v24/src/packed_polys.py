"""Immutable packed convex vertices, with lazy per-region array views."""
class PackedPolys:
 def __init__(self,ptr,vertices):
  self.ptr=ptr;self.vertices=vertices;ptr.flags.writeable=False;vertices.flags.writeable=False
 def __len__(self):return len(self.ptr)-1
 def __getitem__(self,i):
  if isinstance(i,slice):return [self[j] for j in range(*i.indices(len(self)))]
  if i<0:i+=len(self)
  if i<0 or i>=len(self):raise IndexError(i)
  return self.vertices[self.ptr[i]:self.ptr[i+1]]
 def __iter__(self):
  for a,b in zip(self.ptr[:-1],self.ptr[1:]):yield self.vertices[a:b]
