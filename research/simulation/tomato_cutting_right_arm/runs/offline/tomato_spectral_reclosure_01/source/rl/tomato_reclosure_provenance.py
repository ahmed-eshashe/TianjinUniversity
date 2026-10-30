"""Strict source/state bridge for the disclosed supported reclosure diagnostic."""
import json,hashlib
from pathlib import Path
ANCHOR=Path('runs/offline/tomato_spectral_withdrawal_01/withdrawal397_zero_seeded/attempt000')
ANCHOR_SHA='51bec9cc3e9b7fb7af75b7a024cfbf146b47e6c24aabe588bd7fd82e565d3f80'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def transition_sources(root):
 p=root/ANCHOR;s=json.loads((p/'summary.json').read_text())
 assert digest(p/'summary.json')==ANCHOR_SHA
 assert s['passed'] and s['backend']=='triangle_spectral_withdrawal_v1' and s['depth_mm']==0.
 assert json.loads((p.parent/(p.name+'_audit.json')).read_text())['passed']
 assert len(s['damage_states'])==47
 for base,mapping in [(root,s['source_hashes']),(p,s['state_hashes'])]:
  for n,h in mapping.items():assert digest(base/n)==h
 return list(s['source_hashes'])+['rl/offline_tomato_spectral_reclosure.py','rl/audit_tomato_spectral_reclosure.py','rl/tomato_reclosure_provenance.py']
def validate_transition(old,hashes,drive,cleared_depth):
 assert old['passed'] and len(old['damage_states'])==47
 if old['backend']=='triangle_spectral_withdrawal_v1':
  assert old['depth_mm']==0. and drive==0.
  assert all(hashes.get(n)==h for n,h in old['source_hashes'].items())
 elif old['backend']=='triangle_spectral_cleared_reclosure_v1':
  assert old['source_hashes']==hashes and old['depth_mm']==cleared_depth
  assert abs(drive-old['drive_mm'])<=.025000001
 else:raise AssertionError('Unsupported source backend')
