"""Narrow reader for this project's authored ASCII USD blade overrides.

Not a general USD composer. Uses phase3's baked SI points and base topology,
requires a rigid unit-scale phase3 body transform and no blade transform.
Preserves the exact authored collision surface, not a thick box or convex hull.
Native USD/Isaac equivalence must still be checked after the upgrade.
"""
import ast
import hashlib
import math
import re
from tomato_wrench_contract import rotation
from tomato_native_coupon import validate_blade_export


def block(text, spec, name):
    matches=list(re.finditer(r'\b'+spec+r'\s+(?:Mesh\s+)?"'+re.escape(name)+r'"\s*(?:\([^{}]*?\))?\s*\{',text,re.S))
    if len(matches)!=1:
        raise ValueError('Expected one authored prim: '+name)
    start=matches[0].end();depth=1
    for i in range(start,len(text)):
        if text[i]=='{':depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return text[start:i]
    raise ValueError('Unclosed prim')


def literal_array(text, name):
    matches=re.findall(r'(?m)^\s*[^\n=]*\b'+re.escape(name)+r'\s*=\s*(\[[^\]]*\])',text)
    if len(matches)!=1:
        raise ValueError('Expected one literal array: '+name)
    value=ast.literal_eval(matches[0])
    if not isinstance(value,list):raise ValueError('Literal list required')
    return value


def export_authored_blade(base_text, phase3_text):
    if not re.search(r'\bmetersPerUnit\s*=\s*1\s',base_text):
        raise ValueError('Base stage units must be explicitly metres')
    base=block(base_text,'def','CollisionBlade')
    phase=block(phase3_text,'over','CollisionBlade')
    body=block(phase3_text,'over','SM_kitchen_knife_02')
    if any(x in base+phase for x in ['xformOp:', 'timeSamples', 'references', 'payload', 'variantSet']):
        raise ValueError('Unsupported blade composition or transforms')
    matrix=re.findall(r'(?m)^\s*matrix4d xformOp:transform:phase3\s*=\s*(\([^\n]*\))',body)
    if len(matrix)!=1:raise ValueError('Expected baked phase3 body transform')
    M=ast.literal_eval(matrix[0]);rotation([row[:3] for row in M[:3]])
    if len(M)!=4 or any(len(row)!=4 for row in M) or any(M[i][3]!=0 for i in range(3)) or M[3][3]!=1:
        raise ValueError('Unsupported affine body transform')
    if literal_array(body,'xformOpOrder')!=['xformOp:transform:phase3']:
        raise ValueError('Unsupported phase3 transform stack')
    points=literal_array(phase,'points');counts=literal_array(base,'faceVertexCounts');ids=literal_array(base,'faceVertexIndices')
    if any(n!=3 for n in counts) or len(ids)!=3*len(counts):
        raise ValueError('Only inherited triangle topology supported')
    vertices=[list(p) for p in points];faces=[ids[i:i+3] for i in range(0,len(ids),3)]
    source_hashes={'minimal_benchmark.usda':hashlib.sha256(base_text.encode()).hexdigest(),
                   'phase3.usda':hashlib.sha256(phase3_text.encode()).hexdigest()}
    result=dict(units='m',frame='blade_local',vertices=vertices,triangles=faces,
                source_sha256=source_hashes['phase3.usda'],source_hashes=source_hashes,
                method='phase3 baked SI local points plus inherited base triangles; unit-scale rigid body transform excluded as pose',
                runtime_composition_verified=False,collision_representation='authored_triangle_surface; original PhysX convexHull differs')
    validate_blade_export(result)
    result['bounds_m']=[[min(p[i] for p in vertices) for i in range(3)],
                        [max(p[i] for p in vertices) for i in range(3)]]
    result['dimensions_m']=[result['bounds_m'][1][i]-result['bounds_m'][0][i] for i in range(3)]
    return result
