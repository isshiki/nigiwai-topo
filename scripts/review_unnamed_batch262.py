"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}

RESEARCHED_HOLDS = {'606354': ('第262回：Ulf Lundström2015、Umeå universitet Nordsvenska23 Bebyggelsenamnen i Bureå Burträsks och Lövångers socknar358頁公開PDFを取得。本文86頁Bygdsiljum項の原画像と87頁の地理説明を確認。BNに複数の全名方言形、Lindgrenに短縮形、IIに別の全名形が併記されるため一つを現標準形として選ばない。87頁Bygdsiljetは湾内側の別地名でありBygdsiljumの読みへ転用しない。ISOF現行地名辞典のBygdsiljum項は当該集落、旧SiljumとBygdの識別理由、湖湾の関係を説明するがIPAなし。NEも現集落情報のみ。SverigesRadio6365170は2016年2月11日の当該地名を扱う2分48秒の研究職員出演番組であることを本文確認、録音未聴取。PDFの文字抽出では独自音声字形が私用領域に化けるため原画像を保存、IPAとして自動変換しない。今回新たにまとまった大学研究と現行公的辞典の対象対応を確保。凡例・現標準形と古い方言形の対応が未解決で保留。住所ICA Robertsforsvägen4照合の既存根拠は維持、周辺郵便都市のPOIを町中心施設とみなさない。追加0。', ['https://umu.diva-portal.org/smash/get/diva2:812812/FULLTEXT03.pdf', 'https://www.isof.se/namn/ortnamn/sol/ortnamnslexikon/backa-bosarp', 'https://www.sverigesradio.se/artikel/6365170', 'https://www.ne.se/uppslagsverk/encyklopedi/l%C3%A5ng/bygdsiljum'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch261-review.json')
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
        item['address_rechecked_batch']=262
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=262)
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
                ja_editorial=ja, batch=262, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=39, previous_holds_before=24,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==262} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch262-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='公開大学研究の原画像と現行公的地名辞典を照合。別の湾名と短縮方言形を区別し、音声記号を推測変換しない。',items=rows))
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
