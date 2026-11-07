"""Reuse positive quadrature only while coverage and embedded errors pass.

The material, CAD, local absolute quadrature budgets and remap budgets are
unchanged. The caller must use the returned remaining domain bound in its
mechanical solve. Failed reuse falls back to the full reference refresh.
"""
import numpy as np
from tomato_gpu_packet_refresh import PacketEvaluator
from tomato_compiled_partition_refresh import refresh_packet as full_refresh


class ReusableQuadrature:
    def __init__(self):
        self.cache = None

    @staticmethod
    def evaluate(evaluator, packet, groups):
        value = evaluator(packet)
        force = evaluator.packet.sample_force.numpy().reshape(-1, 3, 3)
        bary = packet['barycentric'].reshape(-1, 3, 3)
        nodal = np.einsum('lqa,lqi->lai', bary, force)
        energy = evaluator.packet.energy.numpy().reshape(-1, 3).sum(1)
        return value, nodal.reshape(-1, groups, 3, 3).sum(1), energy.reshape(-1, groups).sum(1)

    def __call__(self, blade, cells, x, triangles, reference, rotation,
                 translation, com, previous_packet, *, padding_m=1e-5,
                 maximum_samples=2097152, lookahead=None):
        vertices = np.asarray(blade['vertices'])
        c = self.cache
        if c is not None and previous_packet is c['high'] and c['padding'] == padding_m:
            motion = float(np.linalg.norm(x-c['x'], axis=1).max())
            motion += float(np.linalg.norm(vertices@rotation.T+translation-c['blade'], axis=1).max())
            remaining = padding_m/2-motion
            states = [(x, translation)] + ([] if lookahead is None else [lookahead])
            valid = remaining >= padding_m/4
            reports = []
            current_value = None
            for xx, tt in states if valid else []:
                displacement = float(np.linalg.norm(xx-c['x'], axis=1).max())
                displacement += float(np.linalg.norm(vertices@rotation.T+tt-c['blade'], axis=1).max())
                if displacement > padding_m/2:
                    valid = False
                    break
                evaluator = PacketEvaluator(blade, xx, rotation, tt, com)
                low, lf, le = self.evaluate(evaluator, c['low'], 1)
                high, hf, he = self.evaluate(evaluator, c['high'], 4)
                fb = .01*max(np.linalg.norm(high['force_n']), 1e-12)+1e-5
                eb = .01*abs(high['energy_j'])+1e-11
                fe = float(np.linalg.norm((hf-lf).reshape(-1, 9), axis=1).sum())
                ee = float(abs(he-le).sum())
                reports.append(dict(force_error_n=fe, energy_error_j=ee,
                                    force_budget_n=fb, energy_budget_j=eb))
                if fe > .25*fb or ee > .25*eb:
                    valid = False
                    break
                if current_value is None:
                    current_value = high
            if valid:
                return c['high'], current_value, dict(passed=True, reused=True,
                    domain_bound_m=remaining/2, embedded_checks=reports,
                    energy_jump_j=0., padding_m=padding_m)
        exported = {}
        packet, value, report = full_refresh(blade, cells, x, triangles,
            reference, rotation, translation, com, previous_packet,
            padding_m=padding_m, maximum_samples=maximum_samples,
            lookahead=lookahead, cache_out=exported)
        self.cache = None
        if exported:
            self.cache = dict(exported, x=x.copy(),
                blade=vertices@rotation.T+translation, padding=padding_m)
        report.update(reused=False, domain_bound_m=padding_m/4)
        return packet, value, report
