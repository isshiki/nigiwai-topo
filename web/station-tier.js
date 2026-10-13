'use strict';
const $ = id => document.getElementById(id), tiers = ['SS','S','A','B','C','D'], sections=[...tiers];
const normalized = value => value.normalize('NFKC').trim().toLocaleLowerCase();
let data;
function unpack(payload) {
 if(payload.format!=='compact-v1')return payload;
 const stations=payload.rows.map(r=>({id:r[0],name:r[1],lon:r[2],lat:r[3],pref_code:r[4],prefecture:payload.prefectures[r[4]],municipality:payload.cities[r[5]],score:r[6],tier:r[7],source_station_ids:r[8],lines:r[9].map(i=>payload.routes[i]),peak:r[10]===null?null:{name:r[10][0],lon:r[10][1],lat:r[10][2],reference_station_id:r[10][3],density:r[6]}}));
 return {...payload,stations};
}
let repeatedNames = new Set();
const points = value => Math.round(value).toLocaleString('ja-JP');
const stationName = s => s.id==='003844'?'明治神宮前〈原宿〉':s.name;
function routeCaption(s) {
 const companies={'東日本旅客鉄道':'JR東日本','西日本旅客鉄道':'JR西日本','東海旅客鉄道':'JR東海','北海道旅客鉄道':'JR北海道','四国旅客鉄道':'JR四国','九州旅客鉄道':'JR九州','東京地下鉄':'東京メトロ','東京都':'都営','大阪市高速電気軌道':'大阪メトロ','首都圏新都市鉄道':'つくばエクスプレス','南海電気鉄道':'南海','阪神電気鉄道':'阪神'};
 const first=s.lines[0];const company=companies[first.company]||first.company;
 const route=first.name.replace(/^\d+号線\((.*)\)$/,'$1').replace(/^\d+号線/,'');
 return `${company}${first.company==='首都圏新都市鉄道'?'':'・'+route}${s.lines.length>1?' ほか'+(s.lines.length-1)+'路線':''}`;
}
function tierReason(s) {
 if(s.score===null)return '対応する峰がないため、Tierは判定していません。密度0を意味するものではありません。';
 if(s.tier==='D')return '全国の駅周辺最大密度が、Cの基準未満のためDです。';
 const criterion=`全国の${s.tier}基準（約${points(data.thresholds[s.tier])}件/km²以上）に達しています。`;
 return s.tier==='SS'?criterion:criterion+`${tiers[tiers.indexOf(s.tier)-1]}の基準未満のため、このTierになります。`;
}
function option(value, text) {const o=document.createElement('option');o.value=value;o.textContent=text;return o;}
function text(tag,value){const n=document.createElement(tag);n.textContent=value;return n;}
function mapLink(s){return `./?region=pref-${s.pref_code}&lat=${s.peak?.lat??s.lat}&lon=${s.peak?.lon??s.lon}&zoom=13`;}
function regionStations(){return data.stations.filter(s=>(!$('prefecture').value||s.pref_code===$('prefecture').value)&&(!$('municipality').value||s.municipality===$('municipality').value));}
function municipalities(){const select=$('municipality'),prev=select.value;select.replaceChildren(option('','すべて'));select.disabled=!$('prefecture').value;const names=[...new Set(data.stations.filter(s=>s.pref_code===$('prefecture').value).map(s=>s.municipality).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ja'));for(const name of names)select.append(option(name,name));if(names.includes(prev))select.value=prev;}
function routes(){const list=$('route-options'),prev=$('line').value;list.replaceChildren();const names=[...new Set(regionStations().flatMap(s=>s.lines.map(l=>l.id)))].sort((a,b)=>a.localeCompare(b,'ja'));for(const name of names)list.append(option(name,name));if(prev&&!names.some(name=>normalized(name).includes(normalized(prev))))$('line').value='';}
function openDetail(s){
 const content=$('detail-content');content.replaceChildren(text('h2',`${stationName(s)} — ${s.tier}`),text('p',`${s.prefecture}・${s.municipality} / ${s.lines.map(l=>l.id).join('、')}`));
 content.append(text('p',`登録密度：${points(s.score)} 件/km²`),text('p',tierReason(s)));
 content.append(text('p','駅の代表位置から半径800m以内で最も高い登録密度です。地形図と同じ200mの平滑化・密度の面を使い、地図の対応する代表点にも同じ値を表示します。駅そのものの密度や店舗数ではありません。'));
 content.append(text('p','近隣の駅が同じ高密度地点を共有する場合があります。各駅に同じ半径を適用し、同名近接駅は統合、異名の駅は別扱いです。'));
 if(s.score<800)content.append(text('p','800件/km²未満のため、地図ではこの代表点や段彩を表示しません。お店がないという意味ではありません。'));
 content.append(text('p',`データ：${data.snapshot}。登録の偏りや位置・名称の誤りが残る可能性があります。`));
 const a=text('a','にぎわいの地形図で最大密度地点を開く');a.href=mapLink(s);a.className='map-link';content.append(a);$('detail').showModal();
}
function showTierInfo(tier) {
 const content=$('detail-content');content.replaceChildren(text('h2',tier==='none'?'峰なし':tier+'の基準'));
 if(tier==='none'){content.append(text('p',`対応する峰がない${data.unmatched_count.toLocaleString()}駅です。密度0や、店舗がないという意味ではありません。Tierは判定していません。`));}
 else {
  const ranges={SS:'上位約1%',S:'上位約1〜5%',A:'上位約5〜20%',B:'上位約20〜50%',C:'上位約50〜80%',D:'残りの約20%'};
  content.append(text('p',`全国${data.matched_count.toLocaleString()}駅の${ranges[tier]}です。`));
  const index=tiers.indexOf(tier),lower=data.thresholds[tier],upper=index?data.thresholds[tiers[index-1]]:null;
  content.append(text('p',lower===undefined?`密度は約${points(upper)}件/km²未満。`:`密度は約${points(lower)}件/km²以上${upper===null?'。':`、約${points(upper)}件/km²未満。`}`));
  const actual=data.stations.filter(s=>s.tier===tier).length;
  content.append(text('p',`現在の全国該当数：${actual.toLocaleString()}駅。同じ密度を境界で分けないため、割合はぴったり一致しません。地域・路線を絞ってもこの全国基準は変わりません。`),text('p','基準値は整数に丸めて表示しています。判定は元の値を使い、密度は人出・人気の順位を意味しません。'));
 }
 $('detail').showModal();
}
function render(){const q=normalized($('query').value),routeQuery=normalized($('line').value);$('route-value').textContent=$('line').value;$('route-value').hidden=!routeQuery;const filtered=regionStations().filter(s=>(!routeQuery||s.lines.some(l=>normalized(l.id).includes(routeQuery)))&&(!q||normalized(stationName(s)).includes(q))).sort((a,b)=>(b.score??-1)-(a.score??-1)||a.id.localeCompare(b.id));$('status').textContent=`${filtered.length.toLocaleString()}駅をすべて表示 · 全国基準のTier / 密度順`;$('status').className='';$('tier-table').replaceChildren();$('empty').hidden=filtered.length!==0;
 for(const tier of sections){const stations=filtered.filter(s=>tier==='none'?s.score===null:s.tier===tier),row=document.createElement('section');row.className=`tier-row tier-${tier}`;const heading=text('h2',tier==='none'?'峰なし':tier);heading.className='tier-heading';const tierButton=text('button',tier==='none'?'峰なし':tier);tierButton.type='button';tierButton.className='tier-info-button';tierButton.title=tier==='none'?'対応する峰がないため未判定。クリック・タップで説明':`${tier}：全国の${{SS:'上位約1%',S:'上位約1〜5%',A:'上位約5〜20%',B:'上位約20〜50%',C:'上位約50〜80%',D:'残り約20%'}[tier]}。クリック・タップで密度基準を見る`; tierButton.setAttribute('aria-label',`${tier==='none'?'峰なし':tier}の基準を説明`);tierButton.append(text('span',`${stations.length}駅`),text('span',tier==='none'?'対応峰なし':{SS:'上位約1%',S:'上位約1〜5%',A:'上位約5〜20%',B:'上位約20〜50%',C:'上位約50〜80%',D:'残り約20%'}[tier]));heading.replaceChildren(tierButton);tierButton.addEventListener('click',()=>showTierInfo(tier));const body=document.createElement('div');body.className='tier-body';const cards=document.createElement('div');cards.className='cards';
  for(const s of stations){const card=document.createElement('button');card.type='button';card.className='station-card';const icon=document.createElement('img');icon.src='train-icon.svg';icon.alt='';icon.className='train-icon';icon.width=26;icon.height=26;card.append(icon,text('strong',stationName(s)),text('small',`${s.prefecture}・${s.municipality}`),text('span',s.score===null?'—':`${points(s.score)} 件/km²`));card.lastChild.className='card-score';if(repeatedNames.has(s.name)){const caption=text('small',routeCaption(s));caption.className='card-route';card.append(caption);}card.setAttribute('aria-label',`${stationName(s)} ${s.prefecture} ${s.municipality} ${repeatedNames.has(s.name)?routeCaption(s):''} ${s.tier||'峰なし'} ${s.score===null?'未判定':points(s.score)+'件/km²'} 詳細`);card.addEventListener('click',()=>openDetail(s));cards.append(card);}
  body.append(cards);row.append(heading,body);$('tier-table').append(row);
 }
 const params=new URLSearchParams();params.set('pref',$('prefecture').value);if($('municipality').value)params.set('city',$('municipality').value);if($('line').value)params.set('line',$('line').value);if(q)params.set('q',$('query').value);history.replaceState(null,'',`station-tier.html${params.size?'?'+params:''}`);$('back-map').href=`./?region=${$('prefecture').value?'pref-'+$('prefecture').value:'japan'}`;
}
$('filters').addEventListener('submit',e=>e.preventDefault());$('close-detail').addEventListener('click',()=>$('detail').close());
(async()=>{try{const r=await fetch('station-tier-public.json?v=20261013-radius2');if(!r.ok)throw Error('駅データを取得できませんでした');data=unpack(await r.json());const occurrences=new Map();for(const s of data.stations)occurrences.set(s.name,(occurrences.get(s.name)||0)+1);repeatedNames=new Set([...occurrences].filter(([,count])=>count>1).map(([name])=>name));const prefs=new Map(data.stations.map(s=>[s.pref_code,s.prefecture]));for(const [code,name]of [...prefs].sort())$('prefecture').append(option(code,name));const p=new URLSearchParams(location.search);$('prefecture').value=p.has('pref')?p.get('pref'):'13';municipalities();if(p.has('city'))$('municipality').value=p.get('city');routes();if(p.has('line'))$('line').value=p.get('line');$('query').value=p.get('q')||'';render();$('prefecture').addEventListener('change',()=>{municipalities();routes();render();});$('municipality').addEventListener('change',()=>{routes();render();});$('line').addEventListener('input',render);$('query').addEventListener('input',render);$('filters').addEventListener('reset',()=>{setTimeout(()=>{$('prefecture').value='';municipalities();routes();render();},0);});}catch(e){$('status').className='';$('status').textContent=`読み込みに失敗しました。再読み込みしてください。${e.message}`;$('filters').querySelectorAll('input,select,button').forEach(n=>n.disabled=true);}})();
