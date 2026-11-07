"""Model-independent separation check for the exploratory slicing branch.

Caller must supply EVERY surviving material connection (including damping,
constraints and bulk connectivity). Compressive contact is not a material bond.
This evaluates topology and mass only, not physical validity or cut provenance.
"""
import numpy as np

def assess_separation(masses, material_edges, expected_labels):
    masses = np.asarray(masses, dtype=float)
    labels = np.asarray(expected_labels)
    edges = np.asarray(material_edges)
    n = len(masses)
    if masses.ndim != 1 or not n or not np.isfinite(masses).all() or np.any(masses <= 0):
        raise ValueError('Positive finite node masses required')
    if labels.shape != (n,) or not np.issubdtype(labels.dtype, np.integer):
        raise ValueError('One integer intended-piece label per node required')
    if edges.size == 0:
        edges = np.empty((0, 2), dtype=int)
    if edges.ndim != 2 or edges.shape[1] != 2 or not np.issubdtype(edges.dtype, np.integer):
        raise ValueError('Integer material edge pairs required')
    if np.any(edges < 0) or np.any(edges >= n):
        raise ValueError('Material edge index outside node registry')
    parent = np.arange(n)
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in edges:
        a, b = root(a), root(b)
        if a != b:
            parent[b] = a
    roots = np.array([root(i) for i in range(n)])
    components = []
    mixed = False
    fragmented = False
    for key in np.unique(roots):
        ids = np.flatnonzero(roots == key)
        labs = np.unique(labels[ids])
        mixed |= len(labs) != 1
        components.append(dict(nodes=ids.tolist(), mass_kg=float(masses[ids].sum()), intended_labels=labs.tolist()))
    for label in np.unique(labels):
        fragmented |= len(np.unique(roots[labels == label])) != 1
    intended_count = len(np.unique(labels))
    complete = intended_count >= 2 and not mixed and not fragmented
    return dict(topological_separation=bool(complete), component_count=len(components),
                intended_piece_count=intended_count, surviving_cross_piece_connection=bool(mixed),
                unintended_fragmentation=bool(fragmented), total_mass_kg=float(masses.sum()),
                components=components, physics_validated=False)
