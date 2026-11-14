"""Offline SI reference for a future solver adapter; not a robot controller.

R maps source-frame components to world components. p is the source origin
in world metres. Wrenches are (force N, moment N m) acting ON the named body.
No simulator, numerical array library, or production solver is imported.
"""
import math


def vector(value):
    value = tuple(float(x) for x in value)
    if len(value) != 3 or not all(math.isfinite(x) for x in value):
        raise ValueError('Expected three finite SI components')
    return value


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def rotation(value):
    rows = tuple(vector(row) for row in value)
    if len(rows) != 3:
        raise ValueError('Expected 3 by 3 rotation')
    if any(abs(dot(rows[i], rows[j]) - (i == j)) > 1e-12
           for i in range(3) for j in range(3)):
        raise ValueError('Frame axes must be orthonormal')
    if abs(dot(rows[0], cross(rows[1], rows[2])) - 1) > 1e-12:
        raise ValueError('Frame must be right handed')
    return rows


def to_world(force, moment, R, p, target=(0, 0, 0)):
    """Rotate wrench and shift its moment from source origin p to target."""
    f, m, p, target = map(vector, (force, moment, p, target))
    R = rotation(R)
    f = tuple(dot(row, f) for row in R)
    m = tuple(dot(row, m) for row in R)
    arm = tuple(x-y for x, y in zip(p, target))
    return f, tuple(x+y for x, y in zip(m, cross(arm, f)))


def pair_residual(first, second):
    """Residuals for two wrenches ALREADY at the same origin and frame.

    Keep force and moment separate: adding N to N m is not meaningful.
    The adapter must enforce synchronized samples and declare its units.
    """
    f1, m1 = map(vector, first)
    f2, m2 = map(vector, second)
    return {'force_residual_n': math.hypot(*(a+b for a,b in zip(f1,f2))),
            'moment_residual_nm': math.hypot(*(a+b for a,b in zip(m1,m2)))}


def power(force, moment, velocity, angular_velocity):
    """Instantaneous watts; velocity is measured at the wrench origin."""
    f, m, v, w = map(vector, (force, moment, velocity, angular_velocity))
    return dot(f, v) + dot(m, w)
