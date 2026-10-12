"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5270327': ('セント・ジャーメイン', 'https://oneidacountywi.com/documents/oneida-county-visitor-guide-2012.pdf', 'SaintGermain US WI GeoNames5270327峰45.900,-89.486支持69/73=.945住所54独立座標63参照205m。原51d2f23d498e954bb4549f3c Mobil102StateHighway70EをStGermainChamberofCommerce2026DestinationGuide PDFindex38 LittleSaintExpressMartMobil102Hwy70 StGermainWI54558に照合。公式名簿はE方向記載なしで文字列完全一致とはしない。OneidaCounty地域観光局2012VisitorGuide PDFindex5は当該StGermainをsaint jer-meynと明示し町の英語読みを直接裏付ける。セント・ジャーメインを掲載読みから編集音写。フランスの同名町発音やモデルサン・ジェルメインは転用しない。当地音声実聴・公的日本語指定ではない。根拠https://oneidacountywi.com/documents/oneida-county-visitor-guide-2012.pdf 、住所https://st-germain.com/wp-content/uploads/2026/01/26StGermainVG.pdf 。原位置密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch204-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    report = read(WORK/'address-name-review.json')
    evidence = {x['peak']:x for x in report['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    found = set()
    for item in rows:
        ident = item['id'].split(':')[1]
        for peak in item['peak_keys']:
            p = evidence[peak]
            c = p['candidates'][0]
            assert c == next(x['reference'] for x in item['evidence'] if x['peak']==peak)
            assert p['status']=='candidate_supported' and c['id']==ident
            assert c['support_share']>=.85 and c['supporting_pois']>=6 and c['distance_m']<=1000
            assert p['distinct_coordinates']>=4 and p['with_address']>=4
        item['address_rechecked_batch']=205
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=205)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='published_local_pronunciation_editorial', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=205, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=67, previous_holds_before=30,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==205} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch205-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='SaintGermain地域観光局の当該町読みと地元商工会議所の原Mobil住所を照合。',items=rows))
    save('docs/unnamed-world-name-approvals.json',approvals)
    queue=read(WORK/'remaining-review-queue.json')
    queue['items']=[x for x in queue['items'] if x['peak'] not in existing]
    queue['remaining']=len(queue['items'])
    queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    assert queue['remaining']==5356-len(existing)
    save(WORK/'remaining-review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    main()
