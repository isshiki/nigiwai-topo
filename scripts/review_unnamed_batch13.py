"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'2726412': ('アルステルブルー', 'https://runeberg.org/ortnamn/0008.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Alsterbro Kalm. alsterbro4」をOCRと原画像で確認。辞典の所属県と原POIのKalmarのAlstervägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2718401': ('ビュクセルクルーク', 'https://runeberg.org/ortnamn/0010.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Byxelkrok Kalm. bykselkro4k」をOCRと原画像で確認。辞典の所属県と原POIのKalmarのNeptunivägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2717878': ('デゲルハムン', 'https://runeberg.org/ortnamn/0011.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Degerhamn Kalm. degerhamn4」をOCRと原画像で確認。辞典の所属県と原POIのKalmarのSödra Möcklebyvägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2711861': ('グルンメルストレスク', 'https://runeberg.org/ortnamn/0013.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Glommersträsk Norrb. glomm3ersträsk2」をOCRと原画像で確認。辞典の所属県と原POIのNorrbottenのStorgatanを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '605474': ('ユンノスアンドー', 'https://runeberg.org/ortnamn/0016.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Junosuando Norrb. junnå-suand4å」をOCRと原画像で確認。辞典の所属県と原POIのNorrbottenのFolketshusvägen・Lautakoskivägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2694359': ('ロフスダーレン', 'https://runeberg.org/ortnamn/0020.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Lofsdalen Jämtl. låfs3da2len」をOCRと原画像で確認。辞典の所属県と原POIのJämtlandのLofsdalsvägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2694593': ('ユーガーン', 'https://runeberg.org/ortnamn/0020.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Ljugarn Gotl. ju3ga2rn」をOCRと原画像で確認。辞典の所属県と原POIのGotlandのStorvägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。'), '2726161': ('オムセレ', 'https://runeberg.org/ortnamn/0033.html', 'Sahlgren・Bergman著、Svenska språknämnden刊Svenska ortnamn med uttalsuppgifter（1968年第2版・1979年刷）の個別項目「Åmsele Västerb. åmm4sele」をOCRと原画像で確認。辞典の所属県と原POIのVästerbottenのByavägenを照合。辞典2–3頁の読み記号（oはkoの母音、g/kは硬音、数字は強勢と母音長の位置）に従う。日本語はCodexの編集音写で公式名ではない。古い辞典の標準語発音であり、現代の全地域方言を保証しない。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch12-review.json')
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
        item['address_rechecked_batch']=13
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=13)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=13, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=203, previous_holds_before=69,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==13} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch13-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映272峰の住所条件を再検証。スウェーデン語委員会の発音辞典の原画像・読み記号・所属県を確認した8峰を採用。公式日本語名としては扱わない。残りの読みの個別調査は未完了。',items=rows))
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
