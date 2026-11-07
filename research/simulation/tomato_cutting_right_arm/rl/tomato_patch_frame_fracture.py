"""Opt-in live-history candidate; not a qualified cutting integrator.

Prepared-history solver stays unchanged. This candidate solves into private
scratch state, proposes existing-law damage, and exposes both to a required
external acceptance audit. No state/history is published on rejection. Actual
contact-derived eligibility and coupled work qualification remain caller duties.
"""
import numpy as np
import warp as wp
from tomato_patch_frame_global import FailedSafeFractionCandidate
from tomato_fraction_boundary import FractionBoundaryCandidate
from tomato_patch_frame_transaction import HistoryTransaction

class LiveFractureCandidate(FailedSafeFractionCandidate):
    def step(self, *args, **kwargs):
        raise ValueError('Use audited_step with explicit accepted contact evidence')

    def audited_step(self, state_in, state_out, dt, *, eligibility, acceptance_audit):
        if not np.isfinite(dt) or dt <= 0 or not callable(acceptance_audit):
            raise ValueError('Positive interval and external acceptance audit required')
        mask = np.asarray(eligibility)
        if mask.dtype != np.bool_ or mask.shape != (self.holder.pairs.shape[0],):
            raise ValueError('Frozen accepted contact eligibility required per patch')
        if state_in is state_out or state_in.particle_q.ptr == state_out.particle_q.ptr:
            raise ValueError('Distinct input/output states required')
        h = self.holder
        old_mask = h.eligible.numpy().copy()
        old_history = h.objective_history.numpy().copy()
        old_mirror = h.history.numpy().copy()
        old_out_x = state_out.particle_q.numpy().copy()
        old_out_v = state_out.particle_qd.numpy().copy()
        scratch = self.state()
        try:
            h.eligible.assign(mask.astype(np.int32))
            # Existing nonlinear mechanics and convergence criteria, with live
            # incremental cohesive potential already implemented by that model.
            FractionBoundaryCandidate.step(self, state_in, scratch, None, None, dt)
            transaction = HistoryTransaction(h, scratch.particle_q, mask)
            verdict = acceptance_audit(state_in, scratch, old_history.copy(),
                                       transaction.trial_history.copy(), mask.copy(), dt)
            if verdict is not True:
                transaction.reject()
                raise ValueError('Candidate failed external acceptance audit')
            transaction.commit(audits_passed=True)
            wp.copy(state_out.particle_q, scratch.particle_q)
            wp.copy(state_out.particle_qd, scratch.particle_qd)
            wp.synchronize_device(scratch.particle_q.device)
        except BaseException:
            h.objective_history.assign(old_history)
            h.history.assign(old_mirror)
            state_out.particle_q.assign(old_out_x)
            state_out.particle_qd.assign(old_out_v)
            raise
        finally:
            h.eligible.assign(old_mask)
