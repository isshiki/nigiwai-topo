"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5970216': ('ハンリー', 'https://hanley.ca/pdfs/newsletter/Hermes%20-%20September%202014.pdf', 'Hanley CA SK GeoNames5970216峰51.628,-106.440支持39/45=.867住所42独立座標28参照142m。原48dfeeecf59f4a901b653b1f TownOfHanley107LincolnStを町広報2014年9月PDFindex11印刷12頁 TownOffice107LincolnStreetHanleySKに直接再照合。現行公式107LincolnAveとの差は記録し同一表記と断定しない。CMU公式辞書 https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict hanley HH AE1 N L IY0を基に編集音写ハンリー。辞書は米英語の語読みでカナダ当地固有の読み・現地実聴・公式日本語名の証明ではない。大学地名百科は英国同名町由来を記載しないためその由来は採用根拠に含めない。同住所のRM/教会を独立した3位置証明に数えず元位置密度不変。')}
RESEARCHED_HOLDS = {'4758111': ('Fairfield原McDonalds44SterrettRd公式店舗URLを通常HTTPSで取得したが403。回避は試さず一次住所確認未了として保留。CMU辞書fairfield発音収録は地理的同一性の証明ではない。次はDGMarket25CastleCt等の別運営者資料で住所確認。', ['https://www.mcdonalds.com/us/en-us/location/VA/FAIRFIELD/44-STERRETT-ROAD/8192.html'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch183-review.json')
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
        item['address_rechecked_batch']=184
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=184)
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
                ja_editorial=ja, batch=184, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=94, previous_holds_before=34,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==184} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch184-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Hanley原役場住所を町広報に再照合。CMU辞書編集音写と当地読みを区別。Fairfield公式403は住所確認成功としない。',items=rows))
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
