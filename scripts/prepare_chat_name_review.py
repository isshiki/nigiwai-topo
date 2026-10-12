"""Materialize the explicit native-name decisions reviewed in the Codex chat.

These are editorial glyph normalization / phonetic spellings, not claims that
Japanese conventional names were independently established for every locality.
"""
import json
from pathlib import Path
from collections import Counter

# Japanese glyphs selected after reading the native aliases. No romanization is
# used to infer Chinese characters. Ambiguous simplified forms stay unresolved.
GLYPHS=str.maketrans(dict(zip(
 '广门东桥马岛阳阴县边进华庆兴宁齐济吴苏郑刘赵张陈镇汤泾营长礼黑临关绿园宽满岗厦头镜观胜卢绥娄狮沧鲁鸳鸯庙尔滨乌诸萨龙乡区来双玛云毓颍贯莲潍萍赣宫锦护瘦维阊穗联仓贝伦则库犁鸠爱应枫丽坏鸡掖滩顺风国顺',
 '広門東橋馬島陽陰県辺進華慶興寧斉済呉蘇鄭劉趙張陳鎮湯涇営長礼黒臨関緑園寛満崗廈頭鏡観勝盧綏婁獅滄魯鴛鴦廟爾浜烏諸薩龍郷区来双瑪雲毓潁貫蓮濰萍贛宮錦護痩維閶穂聯倉貝倫則庫犁鳩愛応楓麗壊鶏掖灘順風国順')))
GLYPHS.update({ord(pair[0]):pair[1] for pair in '沟溝 區区 电電 鱼魚 窑窯 纳納 汉漢 冈岡 农農 怀懐 凤鳳 琼瓊 闵閔 荡蕩 转転 窝窩 扬揚 灵霊 红紅 铺鋪 义義 盘盤 沥瀝 驾駕 德徳 惠恵 围囲 舍舎'.split()})

# Explicit source-ID readings. Same-sounding names are never joined by spelling.
KR={
 '1846918':'アンサン','1838524':'プサン','1842485':'コヤン','1841810':'クァンジュ',
 '1845759':'チョナン','1834203':'トンネ','1833747':'ウルサン','1842936':'キンポ',
 '1846326':'チャンウォン','1843847':'ファソン','1842225':'クミ','1832830':'ヤンピョン',
 '1833105':'ウォンジュ','11523293':'セジョン','1841603':'キョンジュ','1842943':'キメ',
 '1832847':'ヤンジュ','1833466':'ワンジュ','1833788':'ウィジョンブ','1839726':'アサン',
 '1846052':'チンジュ','1836553':'ソクチョ','1842025':'クンサン','1845033':'チュンジュ',
 '1846898':'アニャン','1832828':'ヤンサン','1841598':'キョンサン','1845457':'チョンジュ',
 '1832743':'ヨジュ','1845136':'チュンチョン','1843137':'カンヌン','1846912':'アンソン',
 '1842944':'キムチョン','1884138':'ヨス','13439582':'ヨス','1841066':'モクポ',
 '1846986':'アンドン','1835447':'ポリョン','1835515':'テベク','1841149':'ミリャン',
 '1843491':'イクサン','1845142':'チュムンジン','11124627':'ウェポ','1832215':'ヨニル',
 '1840536':'ナジュ','1843210':'カムポ','1832384':'ヨンジュ','1832771':'イェサン',
 '1835648':'スンチョン','1835895':'ソサン','1884178':'クァンヤン','1893857':'オチョン',
 '1897122':'ナミャンジュ','8607799':'ハソン','8693393':'クァンジョク','1839071':'ポハン',
 '1840886':'ムンギョン','1845519':'チョンソン','1832578':'ヨンドク','1832798':'イェチョン',
 '1839168':'ピイン','1840887':'ムンギョン','8716274':'トンネ','11823111':'ヘリョン',
 '1837707':'サンジュ','1840211':'ノンサン','1845556':'チョンゴク','1846266':'チェジュ',
 '1846419':'チャンピョン','6903078':'チャンニョン','1842016':'クヌィ','11674727':'ポソン',
 '11762608':'ヨンアム','11863735':'ハドン','1838469':'ピョンチャン','1839110':'ポブォン',
 '1841962':'クリョンポ','1843841':'ファスン','1846114':'チナン','1846223':'チド',
 '1846544':'チャンフン','9806499':'ヘアン','9864040':'シンソ','11828625':'クジョン',
 '11840723':'チョソン','11840754':'ウェソ','11840871':'オクコク','11841016':'チョンニャン',
 '11841433':'サンサ','11842524':'トンミョン','13405660':'ペンニョンド','1839011':'ポルギョ',
 '1843163':'カンファ','1843585':'イムシル','1844045':'ファチョン','1897000':'ソンナム',
 '1845604':'チョンジュ','1948005':'クァンミョン','1841811':'クァンジュ','1844191':'ホンチョン',
 '1844751':'ヘナム','1838716':'プチョン','1839652':'オサン','1834946':'タミャン',
 '1846371':'チャンソン','1832642':'ヨンアン','1832699':'ヨンチョン','1832909':'ヤング'
}
KR.update({'1842016':'クンウィ','1843082':'カピョン','1842030':'クンポ','1844174':'ホンソン',
 '1836208':'ソンファン','1833514':'ウェグァン','1840179':'コソン','1843731':'ヒョンプン',
 '1835096':'テサンリ','1842518':'コソン','1842800':'クェサン','1841888':'クァンチョン',
 '6896435':'ソサン','6896737':'ピョンゴク','1835967':'ソンサン','1837706':'サンジュ',
 '1839873':'オクチョン','1842153':'クムサン','1845492':'チョンヤン','1836649':'ソゴムリ',
 '1846355':'チャンス','6891725':'ファンガン','6901737':'テハプ','6800487':'ヨンサンドン',
 '1838508':'プヨ','1832440':'ヨンファ'})

# Parent district aliases must not replace the actual locality being named.
CN_ALIAS={'8527332':'爱民','8527335':'东安','1529506':'博峰','1529435':'伊宁','1279715':'日喀则',
 '1785623':'崑山','1807553':'潢川','7845495':'夏阳','6732240':'法石','6567631':'九里',
 '1815848':'柴村','1804618':'拉卜楞','1808535':'河沥溪'}
HOLD={'2052474':'原表記Haoxinyingと原語毫沁営の対応が不明。別地点への転用を避けて追加確認。',
      '1842754':'Kyosaiは旧外名の可能性があるため現在の巨済の地名・範囲との対応を要確認。',
      '1840379':'Nangenは旧外名の可能性があるため現在の南原の地名・範囲との対応を要確認。'}
ROMAN_KR={'6621166':'ソグィポ','1883990':'ポンゲドン','1925936':'ネソ','1897118':'ファド',
 '1892823':'トンヘ','1845020':'トンヨン','1844308':'ハヤン','1912205':'ウンサン',
 '1846852':'アラドン','1882056':'シンヒョン','1840413':'ナムサ','1840862':'ムンサン',
 '1841775':'クァンヤン','1844954':'チュンピョン','1842939':'キムジェ','1837547':'サンジ',
 '1840982':'ムアン','1838722':'プアン'}

def main():
    refs={r['id']:r for r in json.loads(Path('data/name-translation/world/dictionary.json').read_text(encoding='utf-8'))['items']}
    decisions_path=Path('docs/world-native-name-review.json')
    if decisions_path.exists():
        prior=json.loads(decisions_path.read_text(encoding='utf-8'))
        rows=[{**refs[key],'native_aliases':entry['native_aliases']} for key,entry in prior.items()]
    else:
        rows=json.loads(Path('data/name-research/native-locale-review.json').read_text(encoding='utf-8'))['items']
    country_refs=json.loads(Path('data/name-research/country-locale-aliases.json').read_text(encoding='utf-8'))['references']
    decisions={}
    for row in rows:
        key=row['id'];sid=key.split(':')[-1];ref=refs[key];aliases=row['native_aliases']
        aliases=list(aliases)
        country_ref=country_refs.get(key)
        if country_ref:
            if country_ref['country']!=ref['country']:raise ValueError('Country reference mismatch')
            for name in country_ref['names']:
                if name not in {a['name'] for a in aliases}:aliases.append({'name':name,'source_url':country_ref['source_url'],'language':'native_script_country_alias','country_record_modified':country_ref['modified']})
        entry={k:ref[k] for k in ('original','country','lon','lat')}
        entry.update(review_method='Codex editorial review against source-ID-linked native aliases',reviewed_at='2026-10-10',native_aliases=aliases)
        if sid in HOLD:
            entry.update(decision='hold',reason=HOLD[sid])
        elif row['country']=='KR' and sid in ROMAN_KR:
            entry.update(decision='adopt',name=ROMAN_KR[sid],status='reviewed_roman_transliteration',source='GeoNames / CC BY 4.0 + Codex reviewed transliteration',source_name=ref['original'],basis='GeoNames参照地点の原表記をカタカナに音写した編集表記。原語別名が不足するため、公式日本語名の確認済み表記とは区別しています。')
        elif row['country']=='KR' and sid in KR and any('가'<=c<='힣' for a in aliases for c in a['name']):
            entry.update(decision='adopt',name=KR[sid],status='reviewed_native_transliteration',source='GeoNames alternateNames ko / CC BY 4.0 + Codex reviewed transliteration',basis='出典ID付き韓国語別名を確認してカタカナに音写した編集表記。全件の公式日本語慣用名を確認したものではありません。')
        elif row['country']=='CN' and aliases:
            if sid in CN_ALIAS and not any(a['name']==CN_ALIAS[sid] for a in aliases):raise ValueError('Missing selected native alias')
            chosen=next((a for a in aliases if a['name']==CN_ALIAS.get(sid)),aliases[0])
            name=chosen['name'].translate(GLYPHS)
            entry.update(decision='adopt',name=name,status='reviewed_native_glyphs',source='GeoNames native aliases / CC BY 4.0 + Codex reviewed Japanese glyphs',source_alias_id=chosen.get('alternate_id'),source_name=chosen['name'],basis='出典ID付き中国語別名の文字を日本語字形へ整理した編集表記。日本語の慣用名・行政区域の現状を全面的に保証するものではありません。')
            if chosen.get('source_url'):entry['native_source_url']=chosen['source_url']
        else:entry.update(decision='hold',reason='出典ID付き原語別名が不足。ローマ字からの漢字推測・旧外名の読みの転用を避け、追加の資料を確認。')
        if entry['decision']=='adopt':entry['source_url']='https://download.geonames.org/export/dump/alternateNamesV2.zip'
        decisions[key]=entry
    decisions_path.write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(Counter((r['country']+':'+r['decision']) for r in decisions.values()))))

if __name__=='__main__':main()
