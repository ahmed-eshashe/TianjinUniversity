"""Research-only composition of bounded CAD pressure and audited live history.

Retains the original five-micrometre coverage bound and original material law.
Not a cutting qualification: measured accepted eligibility, packet-refresh and
coupled impulse/work acceptance must still be supplied by the experiment.
"""
from tomato_bounded_cad_interval import BoundedCADInterval
from tomato_live_fracture_candidate import LiveFractureCandidate

class LiveCADCandidate(BoundedCADInterval, LiveFractureCandidate):
    def step(self, *args, **kwargs):
        raise ValueError('Use audited_step; live CAD stepping requires explicit external audits')
