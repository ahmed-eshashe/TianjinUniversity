"""Contact impulse budget evaluated over a fixed physical duration.
Rigid contact reports are per-step impulses divided by dt. Compare the same
1/960 s averaging window at 960 and 1920 Hz; do not compare unequal windows.
The average uses magnitudes, so opposed impulses cannot cancel a stop.
"""
import numpy as np
class FixedWindowLoads:
    def __init__(self, physics_hz, observer_hz=960):
        if physics_hz < observer_hz or physics_hz % observer_hz:
            raise ValueError('Physics frequency must be an integer multiple of the observer frequency')
        self.n = physics_hz // observer_hz
        self.history = None
        self.total = None
        self.index = 0
    def update(self, magnitudes):
        values = np.asarray(magnitudes, dtype=float)
        if not np.isfinite(values).all() or np.any(values < 0):
            raise ValueError('Contact loads must be finite nonnegative magnitudes')
        if self.history is None:
            self.history = np.zeros((self.n, *values.shape))
            self.total = np.zeros_like(values)
        if values.shape != self.total.shape:
            raise ValueError('Contact pair indexing changed during an episode')
        self.total += values - self.history[self.index]
        self.history[self.index] = values
        self.index = (self.index + 1) % self.n
        return np.maximum(self.total / self.n, 0.)
