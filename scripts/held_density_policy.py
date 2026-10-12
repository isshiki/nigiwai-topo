"""Explicit, reversible ID quarantine of the 13 reviewed coordinate clusters."""
import hashlib,json
from pathlib import Path
from collections import Counter
from fetch_world import write_json

POLICY=Path('docs/held-density-exclusions.json')

def load_policy():
    p=json.loads(POLICY.read_text(encoding='utf-8'))
    ids={r['id'] for r in p['records']}
    if len(ids)!=len(p['records']) or p['snapshot_id']!='2325979374271449319':raise ValueError('Invalid exclusion policy')
    return p,ids,hashlib.sha256(POLICY.read_bytes()).hexdigest()

def main():
    audit=json.loads(Path('data/name-research/held-poi-addresses/audit-detail.json').read_text(encoding='utf-8'))
    decisions=json.loads(Path('docs/held-peak-display-decisions.json').read_text(encoding='utf-8'))
    keys={r['peak'] for r in decisions['items']}
    records=[];groups=[]
    for group in audit['items']:
        if group['peak'] not in keys:raise ValueError('Unexpected review group')
        # A nearby same-name settlement is not a precise address fix. None of
        # these reviewed records has a matching locality within 2.5km.
        if any(r.get('nearest_references') and r['nearest_references'][0]['distance_m']<=2500 for r in group['records']):
            raise ValueError('A potentially local record requires individual review')
        states=Counter(r['status'] for r in group['records'])
        groups.append({'peak':group['peak'],'count':len(group['records']),'address_status':dict(states)})
        for r in group['records']:
            records.append({'id':r['fsq_place_id'],'peak':group['peak'],'coordinates':[r['longitude'],r['latitude']],'address_status':r['status']})
    if len(groups)!=13 or len(records)!=5436:raise ValueError('Review population changed')
    policy={'version':1,'snapshot_id':decisions['snapshot_id'],'reviewed_at':'2026-10-10',
        'decision':'exclude_from_density_as_reviewed_location_quality_hold',
        'basis':'13 reviewed concentrations contain distant addresses, many different addresses/localities on coincident or tightly clustered coordinates, or missing locality near country reference points. No matching locality reference within 2.5km was found in these records. This is a conservative cluster quality quarantine, not proof that every POI is incorrect. Missing/unmatched addresses are never automatically excluded outside these individually reviewed groups.',
        'limits':'Raw source retained. Exact snapshot, IDs and coordinates pinned; no radius masking, relocation, fuzzy city matching, worldwide automatic rule or claim of error rate. May omit genuine local registrations with poor address evidence. Restoring a record requires individual position evidence and a new density release.',
        'groups':groups,'records':sorted(records,key=lambda r:r['id'])}
    write_json(POLICY,policy)
    print('Reviewed density hold IDs:',len(records),flush=True)
if __name__=='__main__':main()
