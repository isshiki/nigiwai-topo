"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5054800': ('イーグルビル', 'https://restaurants.subway.com/united-states/mo/eagleville/21022-state-highway-n', 'Eagleville US MO 峰40.466,-93.978。支持33/34、住所28、独立座標31、参照863m。原Subway53895cfc498eed7dcdacfade 21022 E State Hwy NをSubway公式Love’sTravelStop店舗21022 State Highway N Eagleville MO64442と照合。公式ではE方向が省略され文字列完全一致ではない。同住所のLove’sとSubwayを独立した位置証拠として水増ししない。CMU辞書eagle IY1 G AH0 L、ville V IH1 Lからイーグルビルを編集音写。当地固有の全語発音・音声実聴・公式日本語名は未確認。原位置密度不変。'), '4389012': ('グローブスプリング', 'https://mfalebanon.com/grovespring/', 'Grovespring US MO 峰37.400,-92.602。支持28/29、住所27、独立座標26、参照683m。原MFA Agri Services4e4eeb2818a8af30fd7e1642 2135 Highway M、37.4003938241,-92.6073879293を運営者MFA公式Grovespring店2135 State Hwy M Grovespring MO65662と照合。道路表記略記差はあるが番地・道路記号・施設・町州が対応。CMU辞書grove G R OW1 V、spring S P R IH1 NGからグローブスプリングを編集音写。モデルのグロブスプリングは採用しない。当地固有の全語発音・音声実聴・公式日本語名は未確認。学区本部のHartville住所を当該学校所在地として転用しない。原位置密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch205-review.json')
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
        item['address_rechecked_batch']=206
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=206)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='dictionary_informed_editorial', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=206, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=67, previous_holds_before=29,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==206} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch206-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='運営者公式住所と原POIを照合し、英語構成語辞書から編集音写。全語の当地発音とは区別。',items=rows))
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
