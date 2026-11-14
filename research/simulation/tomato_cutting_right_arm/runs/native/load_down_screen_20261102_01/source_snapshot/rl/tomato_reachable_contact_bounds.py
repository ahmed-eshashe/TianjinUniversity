"""Retain interaction coverage as well as positive separation between queries.

For detection radius R and interaction radius r, proxy motion <= .4(R-r)
ensures a previously undetected pair remains at least r+.2(R-r) apart.
Known pairs additionally use .4*d per vertex, leaving >=.2*d separation.
Positive barycentric embeddings preserve the physical-node motion ball.
"""
import warp as wp
@wp.kernel(enable_backward=False)
def retain_query_coverage(global_bound:float,bounds:wp.array[float]):
 i=wp.tid()
 if bounds[i]<float(wp.inf):bounds[i]=wp.min(bounds[i],global_bound)
