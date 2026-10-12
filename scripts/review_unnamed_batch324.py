"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}

RESEARCHED_HOLDS = {'5992692': ("第323回の保健施設230/40CentreStreetの公式住所不一致は未解消。追加でKinusoMercantile運営者の物理住所227CenterStreet Kinuso Alberta T0G1K0、電話7807753517を直接確認。仕入先Annette'sKeepsakes店舗一覧はKinusoMercantile/VandS同番地同電話を直接確認し、原V&SDepartmentStore a1333b52e05b40a5b9ade968 227CentreStとの屋号対応を補強。Center/Centre表記差は記録し、同店舗の別屋号を独立施設数として追加しない。地名読みは由来語や人名の発音から転用せず保留。", ['https://www.kinusomercantile.ca/contact.html', 'https://www.annetteskeepsakes.com/pages/ab-retailers']), '6174638': ('従来HUB301MainSt住所照合根拠を保持。町公式Contactを直接確認し204MainSt Vonda Saskatchewan S0K4N0を町の所在地の補助資料として保存。元HUB301MainStとは別施設・別番地であり同一施設照合に使わない。Wiktionary直接本文はカナダ町語義あり、発音欄なし。検索のVondaCroissantは人名で、赤ちゃん名前サイトのVonda発音は町に限定されないため未採用。モデル候補ボンダを確定せず。', ['https://thetownofvonda.com/contact/', 'https://en.wiktionary.org/wiki/Vonda']), '5320914': ('従来の住所支持31/31、20座標を保持。英語百科事典WikieupArizona直接本文に地理座標とMohaveCounty Arizonaを確認、発音欄はない。発音検索は近隣Hualapai山名、Picacho別町、死亡pronounceddeadなど対象語不一致。一般名詞wikiupのIPAを町名に転用しない。読みは保留。', ['https://en.wikipedia.org/wiki/Wikieup,_Arizona'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch323-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    report = read(WORK/'address-name-review.json')
    evidence = {x['peak']:x for x in report['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    assert not ({p for x in rows for p in x['peak_keys']} & existing), 'Prior report resurrected adopted peaks'
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
        item['address_rechecked_batch']=324
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=324)
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
                ja_editorial=ja, batch=324, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=22, previous_holds_before=6,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==324} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch324-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='自治体・施設運営者住所と元POIを照合。対象町の日本語学術・旅行用例を参考に編集表記を採用、公開検索本文と直接取得を区別。',items=rows))
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
