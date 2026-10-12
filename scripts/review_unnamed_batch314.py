"""Retire Smeaton review only after independently validated v3 is published."""
import json
from pathlib import Path
from collections import Counter

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    release=read('data/validation/world-v3-published.json')
    assert release['complete'] and release['range_cors_verified']
    assert release['base']=='https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v3/'
    validation=read('data/validation/held-density-release-v3.json')
    assert validation['smeaton_peaks_within_1km']==0 and validation['all_index_leaf_peaks']==319884
    prior=read('docs/unnamed-world-batch327-review.json')
    rows=[x for x in prior['items'] if x['decision']=='hold']
    target=next(x for x in rows if x['id']=='GeoNames:6149823')
    assert target['peak_keys']==['53.491, -104.807']
    target.update(decision='resolved_density_removed',resolved_batch=314,reason='Operator physical location differs from mailing locality. One snapshot-pinned Camp ID excluded; corrected peak drops below extraction floor50. V3 assembled, validated and published. No name invented; source record preserved.')
    summary=dict(prior['summary'])
    summary.update(remaining_candidate_peaks=21,remaining_previous_holds=4,added_total=0,published_total=875,unnamed_remaining=4480,resolved_by_density_rebuild=1)
    save('docs/unnamed-world-batch314-review.json',dict(snapshot=prior['snapshot'],summary=summary,policy=prior['policy'],items=rows))
    queue=read('data/name-research/unnamed-world/remaining-review-queue.json')
    assert queue['remaining']==4481
    queue['items']=[x for x in queue['items'] if x['peak']!='53.491, -104.807']
    assert len(queue['items'])==4480
    queue['remaining']=4480
    queue['resolved_density_peaks']=['53.491, -104.807']
    queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    save('data/name-research/unnamed-world/remaining-review-queue.json',queue)
    print(summary)
if __name__=='__main__':main()
