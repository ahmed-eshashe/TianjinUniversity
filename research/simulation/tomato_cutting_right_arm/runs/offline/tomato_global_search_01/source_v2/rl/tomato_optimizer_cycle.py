"""Fingerprint only uncommitted restart state; never accept a physical state."""
import hashlib,json

def restart_fingerprint(candidate):
    if candidate['passed'] is not False or candidate['optimization_only'] is not True:
        raise ValueError('Only uncommitted optimizer candidates may be fingerprinted')
    keys=('depth_mm','previous_summary_sha256','guess_sha256','trial_damage_states','optimizer_active_rows','source_hashes')
    payload={k:candidate[k] for k in keys}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()
