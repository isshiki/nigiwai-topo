"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'2697052': ('ロングヴィクスモーン', 'https://www4.isof.se/NAU/bilder/_s2yx001/622307c1/p3/0000138a.pdf', 'Långviksmon SE GeoNames2697052峰63.631,18.695支持32/34=.941住所31独立座標33参照85m。元5bed3b961822230032d8d117 Handlar n Lomvägen2をチェーン公式 https://www.handlarn.se/butiker/storsjobygdens-lanthandel/ LOMVÄGEN2 LÅNGVIKSMONに直接照合。ISOF公開Björna目録622307c1のLångviksmon delavbyカードp3/0000138a.pdf原画像でH.O.Fahlgren1923、Björna sn Ångermanlands北部の地理的文脈と発音記録を確認。åをアとしないロングヴィクスモーンと編集音写。歴史的現地記録であり現在録音聴取・公式日本語名とは称さない。町の原施設と参照位置の対応条件は再検証。位置密度不変。')}
RESEARCHED_HOLDS = {'2702619': ('第153回：ISOF Håsjö目録610218c1から現集落cardp3/0000181a.pdf1974と旧教区総称cardp3/0000189a.pdf1920を原画像確認。1974カードは自治体合併の記述で発音なし。1920カードはHåsjö/Hällesjö教区総称、Revsundで採録した方言語の複数形の説明で、現在の鉄道集落名そのものの発音と同一視しない。モデルカールネ未採用、集落・鉄道駅カードの参照先を次に確認。', ['https://www4.isof.se/NAU/scans/_s1zx001/610218c1.htm', 'https://www4.isof.se/NAU/scans/_s2zx001/610218c1/p3/0000181a.pdf', 'https://www4.isof.se/NAU/scans/_s2zx001/610218c1/p3/0000189a.pdf']), '2722465': ('第153回：ISOF Fors目録610222d1のBispgården by cardp3/0000018a.pdf原画像確認。E.Burman1931がH.Geger1905 Ulma88:83の記録を参照し、短縮した方言形bisgan等を記録。標準形Bispgårdenと方言形は区別が必要でモデルビスペガーデンを採用しない。現集落カードと方言記号の凡例をさらに照合。', ['https://www4.isof.se/NAU/bilder/_s1zx001/610222d1.htm', 'https://www4.isof.se/NAU/bilder/_s2zx001/610222d1/p3/0000018a.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch152-review.json')
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
        item['address_rechecked_batch']=153
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=153)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='local_pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=153, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=108, previous_holds_before=38,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==153} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch153-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Långviksmonの現地発音カードとHandlarn番地を照合して反映。KälarneとBispgårdenの記録対象・方言形を確認し保留。',items=rows))
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
