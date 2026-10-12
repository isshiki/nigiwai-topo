"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'2993513': ('モリーヌ（ケーラス）', 'https://www.eu-alps.com/o-site/do-2002/620/620ville-vieille-aiguilles.htm', 'Molines-en-Queyras FR GeoNames2993513、支持23/26=.885、住所23、独立座標21、距離20m。元POI6881c6ab5b8b152daf1968faLaBanquePostale235rueDuSerreをLaPoste公式 https://localiser.laposte.fr/hautes-alpes/molines-en-queyras/molines-en-queyras-intercommunale-050770 の235RUEDUSERRE05350MOLINESENQUEYRASに照合。原施設ブランドと公式郵便局名は違うが同局はLaBanquePostale銀行サービスを明記。北村峠一のEUAlps公開日本語紀行 https://www.eu-alps.com/o-site/do-2002/620/620ville-vieille-aiguilles.htm に翻訳書引用としてモリーヌの村、同ページにQueyrasケーラス渓谷と周辺町の位置関係を確認。地域観光局 https://lequeyras.com/en/at-the-ends-of-the-earth/molines-en-queyras/ は対象村のMolines短称を使用する。日本語用例の短称モリーヌに地域名ケーラスを括弧で添えモリーヌ（ケーラス）とする編集識別ラベル。Molines-en-ChampsaurやGapのMolinesと混同しない。正式名称全体の音写やenの現地発音を確定したという意味ではない。引用元の岩波翻訳書そのものは未実見なので直接確認と主張しない。著者の音声や法定日本語名でもない。モデルモリーヌアンケイラスを採用しない。元参照IDと座標・密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch76-review.json')
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
        item['address_rechecked_batch']=77
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=77)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='editorial_japanese_usage', reason=note,
            japanese_label_type='editorial_japanese_usage')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=77, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                editorial_usage_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=135, previous_holds_before=45,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==77} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch77-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Molines-en-Queyrasの公式住所と公開日本語短称を照合し地域識別を添えた編集ラベルを反映。',items=rows))
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
