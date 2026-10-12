"""Apply a manually researched official-address batch, preserving raw evidence."""
import argparse
import json
from collections import Counter
from pathlib import Path

import duckdb
from pyproj import Geod
from reviewed_address_text import reviewed_text_reference


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--review',required=True)
    args=parser.parse_args()
    plan=read(args.review)
    root=Path('data/name-research/unnamed-world')
    old={x['peak']:x for x in read(root/'address-name-review.json')['items']}
    evidence={x['peak']:x for x in read(root/'reference-reconciliation384.json')['items']}
    apfile=Path('docs/unnamed-world-name-approvals.json')
    approvals=read(apfile)
    if len(approvals['items'])!=plan['expected_adopted']:
        raise ValueError('Adoption count changed; do not replay an applied batch')
    existing={x['peak'] for x in approvals['items']}
    keys=[x['peak'] for x in plan['items']]
    if len(keys)!=len(set(keys)) or set(keys)&existing:
        raise ValueError('Duplicate/already approved peak')
    afile=Path('docs/unnamed-world-official-anchor-reviews.json')
    anchors=read(afile)
    original=afile.read_bytes()
    con=duckdb.connect()
    choices=[]
    for item in plan['items']:
        peak=item['peak']; e=evidence[peak]; p=old[peak]
        ref={**e['reference'],'supporting_pois':e['text_support'],
             'support_share':round(e['text_support']/e['near_pois'],3)}
        rows=[]
        for facility in item['anchors']:
            matches=con.execute('SELECT name,address,locality,country,longitude,latitude FROM read_parquet(?) WHERE fsq_place_id=?',
                                [str(root/'addresses.parquet'),facility['poi_id']]).fetchall()
            if len(matches)!=1:raise ValueError('Anchor POI not unique')
            row=matches[0]
            rows.append({**facility,'raw_identity':list(row[:4]),'raw_address':row[1],
                         'official_locality':ref['name'],
                         'distance_m':round(Geod(ellps='WGS84').inv(*p['coordinates'],row[-2],row[-1])[2])})
        if rows:
            anchors['items'].append({'peak':peak,'reference_id':ref['id'],'decision':'adopt','anchors':rows,'rationale':item['review_note']})
        choices.append({'peak':peak,'ref':ref,'ja_editorial':item['ja_editorial'],
                        'batch':plan['batch'],'policy':item.get('policy','reviewed_address_text_anchors'),
                        'reading_status':item['reading_status'],'reviewed_by':'Codex',
                        'review_note':item['review_note'],'official_anchor_review':afile.as_posix()})
        if 'cartographic_review' in item:
            choices[-1]['cartographic_review'] = item['cartographic_review']
    con.close()
    save(afile,anchors)
    try:
        for choice in choices:reviewed_text_reference(choice,old[choice['peak']])
    except Exception:
        afile.write_bytes(original)
        raise
    qfile=root/'remaining-review-queue.json'; queue=read(qfile)
    if not set(keys)<={x['peak'] for x in queue['items']}:
        afile.write_bytes(original)
        raise ValueError('Missing pending keys')
    approvals['items'].extend(choices)
    queue['items']=[x for x in queue['items'] if x['peak'] not in set(keys)]
    queue['remaining']=len(queue['items'])
    queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    save(apfile,approvals);save(qfile,queue)
    result={'batch':plan['batch'],'adopted':len(choices),'total_adopted':len(approvals['items']),
            'remaining':queue['remaining'],'items':choices}
    save(f'docs/unnamed-world-batch{plan["batch"]}-adoptions.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='items'}))


if __name__=='__main__':main()
