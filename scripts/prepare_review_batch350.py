"""Prepare the next guarded adoption using the established batch format."""
from pathlib import Path

source = Path('scripts/review_unnamed_batch348.py').read_text(encoding='utf-8')
source = source.replace('348', '350').replace('batch347-review', 'batch349-review')
start = source.index('CONFIRMED =')
end = source.index('\n\n\ndef read', start)
source = source[:start] + '''CONFIRMED = {'5320914': ('ウィキアップ', 'https://themooneyflyer.com/issues/2015-JunTMF.pdf', 'The Mooney Flyer Vol4 No6 June2015の公開原PDFを直接取得。PDF第17頁（印刷17頁）のWikieup(Wick-ee-up),Arizonaを確認。目次は記事I Smell a Lawsuitの執筆者をEditor Jim Priceと示し、教官一覧はChandler AZのCFII/MEI/ATPとして掲載。一般名詞wikiupや別地域の音声ではなく対象アリゾナ町名への発音説明に基づくウィキアップを編集音写として採用。公式日本語名や現地音声の実聴とは扱わない。Shell公式18183SHWY93/WIKIEUPは原4c45ea8f342c1b8d9613b589と一致。BLM2016公開告知のWikieup Post Office18170USHighway93は原5eea0b887bfc290008ee1bcaの施設名・番地道路町名と一致。Shellと同住所ATMは独立施設根拠として数えない。31/31地名支持、27住所、20座標、参照359m。密度や原座標は不変。')}

RESEARCHED_HOLDS = {'5968869': ('CBC改訂1959公開SearchWithinVolume2でHagensborgBC/PA15とhăg-ens-burgの発音表記を直接確認。読みに基づく編集候補ハゲンズバーグを記録するが現代音声や公式日本語名とは扱わない。観光公式Mercantile1801BC20と原1801Hwy20、BaileyBridge運営者2375SaloomptRoadと原2375SaloomptRiverRdの番地・町を再照合、道路表記差を保持。13/16の完全同座標問題は未解消で名称反映は保留。残り7町の公開検索0件は未収録の証明とはしない。', ['https://books.google.com/books?id=sbEvAAAAYAAJ&pg=PA15', 'https://bellacoola.ca/businesses/hagensborg-mercantile/', 'https://www.baileybridgecampsite.ca/map'])}
''' + source[end:]
source = source.replace('candidate_peaks_before=21', 'candidate_peaks_before=20')
source = source.replace("        item['address_rechecked_batch']=350", "        if ident in CONFIRMED or ident in RESEARCHED_HOLDS:\n            item['address_rechecked_batch']=350")
Path('scripts/review_unnamed_batch350.py').write_text(source, encoding='utf-8')
