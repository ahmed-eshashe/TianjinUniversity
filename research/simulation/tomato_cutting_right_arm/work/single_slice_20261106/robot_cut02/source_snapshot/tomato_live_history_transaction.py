"""Acceptance-only history transaction for the existing objective cohesive law.

Does not qualify contact eligibility or authorize the prepared-history integrator
for cutting. A caller supplies frozen, measured-contact eligibility and calls
commit only after its mechanics/contact/work audits have accepted the candidate.
"""
import numpy as np
import warp as wp
from tomato_failed_safe_objective import commit_objective_history, validate_active_frames

class HistoryTransaction:
    def __init__(self, holder, accepted_positions, eligibility):
        eligibility = np.asarray(eligibility)
        count = holder.objective_history.shape[0]
        if eligibility.shape != (count,) or eligibility.dtype != np.bool_:
            raise ValueError('One explicit boolean contact eligibility per patch required')
        self.holder = holder
        self.before = holder.objective_history.numpy().copy()
        self.before_mirror = holder.history.numpy().copy()
        self.used = False
        self.eligibility = wp.array(eligibility.astype(np.int32), dtype=int, device=accepted_positions.device)
        self.candidate = wp.clone(holder.objective_history)
        self.mirror = wp.clone(holder.history)
        invalid = wp.zeros(1, dtype=int, device=accepted_positions.device)
        wp.launch(validate_active_frames, dim=count, device=accepted_positions.device,
                  inputs=[accepted_positions, holder.pairs, holder.objective_anchors,
                          holder.objective_law, self.candidate], outputs=[invalid])
        if invalid.numpy()[0]:
            raise ValueError('Invalid accepted candidate geometry/history')
        wp.launch(commit_objective_history, dim=count, device=accepted_positions.device,
                  inputs=[accepted_positions, holder.pairs, holder.counts,
                          holder.objective_anchors, holder.objective_sign,
                          holder.objective_weights, holder.objective_stiffness,
                          holder.objective_law, self.eligibility],
                  outputs=[self.candidate, self.mirror])
        trial = self.candidate.numpy()
        if not np.isfinite(trial).all() or np.any(trial < self.before):
            raise ValueError('Nonfinite or healing candidate history')
        if not np.array_equal(trial[~eligibility], self.before[~eligibility]):
            raise ValueError('Ineligible patch changed')
        self.trial_history = trial.copy()

    def reject(self):
        if self.used:
            raise RuntimeError('Transaction already consumed')
        self.used = True

    def commit(self, *, audits_passed):
        if self.used:
            raise RuntimeError('Transaction already consumed')
        self.used = True
        if audits_passed is not True:
            raise ValueError('Explicit successful external audits required')
        h = self.holder
        if not np.array_equal(h.objective_history.numpy(), self.before) or not np.array_equal(h.history.numpy(), self.before_mirror):
            raise RuntimeError('Stale transaction; committed history changed')
        try:
            wp.copy(h.objective_history, self.candidate)
            wp.copy(h.history, self.mirror)
            wp.synchronize_device(h.objective_history.device)
        except BaseException:
            h.objective_history.assign(self.before)
            h.history.assign(self.before_mirror)
            raise
        return self.trial_history.copy()
