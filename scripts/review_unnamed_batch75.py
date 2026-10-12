"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}
RESEARCHED_HOLDS = {'2993513': ('元LaBanquePostale6881c6ab5b8b152daf1968fa235rueDuSerreをLaPoste公式235RUEDUSERRE05350MOLINESENQUEYRASに照合。公式は郵便局名だが銀行サービスを明記するので原ブランド差と共用所在地を記録。EUAlpsのAiguilles紀行にはモリーヌとケーラス渓谷があるがMolines-en-Queyras全体の日本語表記はない。別Molines-en-Champsaurを区別し、全称の読みを確認するまでモデルモリーヌアンケイラスを採用しない。次は地方観光局の地名録音または全称を使用する実訪紀行。', ['https://localiser.laposte.fr/hautes-alpes/molines-en-queyras/molines-en-queyras-intercommunale-050770', 'https://www.eu-alps.com/o-site/do-2002/620/620ville-vieille-aiguilles.htm']), '3010343': ('GallandSports原ef3541e3164f49b0a74605dfPontdelaPlaceに対しBolle公式販売店一覧はPontDeLaPlaceD985A、地方観光局はPontlaplace05800LaChapelleenValgaudemar。検索本文一致を確認したがBolle直接本文はcachemiss、外部個別住所は本文再取得が必要。Airbnb日本語同ページでエンバルガウデマールとアンヴァルゴデマールが混在し自動翻訳用例を単独採用しない。原国立公園POIのlocalityLArgentiereLaBessee不一致も追加の支持根拠に使わない。次は観光局住所本文と対象村のフランス語録音。', ['https://stores.bolle.com/fr-fr/magasin/1582/galland-sports', 'https://www.champsaur-valgaudemar.com/offres/galland-sports-la-chapelle-en-valgaudemar-fr-2152647/']), '2997050': ('市役所公式住所LE VILLAGE26620LUSLACROIXHAUTE DROMEを確認したが原CampinglaCondaminelAllevaと同施設の住所照合ではない。Airbnb/Vrboはリュス、リュ、ルスが混在しモデルの根拠にしない。ORTOLANGのEthnotextesLUSLACROIXHAUTE42頁PDFを新規発見、本文文字層0のため現時点で発音や全文内容は未確認。次はPDF画像と対応する原録音の資源IDを確認し、地元話者が町名を発音する箇所を確認する。', ['https://www.lus-la-croix-haute.fr/', 'https://repository.ortolang.fr/api/content/recherches-francais-parle/v1/pdf/volume_2/163_2_RSFP.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch74-review.json')
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
        item['address_rechecked_batch']=75
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=75)
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
                ja_editorial=ja, batch=75, policy='address_review_85', reviewed_by='Codex',
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
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==75} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch75-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='フランス3件の住所と日本語用例を再照合し全称・本文・録音の未確認事項と次の資料を記録。',items=rows))
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
