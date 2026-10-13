const region = document.querySelector('#region');
const worldOnly = window.NIGIWAI_CONFIG.worldOnly === true;
const area = worldOnly ? document.createElement('select') : document.querySelector('#area');
const requestedRegion = new URLSearchParams(location.search).get('region') || (worldOnly ? 'world' : 'japan');
const stationViewParams = new URLSearchParams(location.search);
const stationView = ['lat','lon','zoom'].every(k=>stationViewParams.has(k)) ? {lat:Number(stationViewParams.get('lat')),lon:Number(stationViewParams.get('lon')),zoom:Number(stationViewParams.get('zoom'))} : null;
const areas = {japan:{name:'日本',dataBase:window.NIGIWAI_CONFIG.dataBase}, ...(window.NIGIWAI_CONFIG.areas || {})};
for (const [id,entry] of Object.entries(areas)) {const option=document.createElement('option'); option.value=id; option.textContent=entry.name; area.append(option);}
const requestedArea = new URLSearchParams(location.search).get('area') || (areas[requestedRegion] ? requestedRegion : 'japan');
area.value = worldOnly ? 'world' : (areas[requestedArea] ? requestedArea : 'japan');
let regions = {};
maplibregl.addProtocol('pmtiles', new pmtiles.Protocol().tile);
const map = new maplibregl.Map({container: 'map', center: areas[area.value].center || [139.5,35.7], zoom: 9.5, attributionControl: false,
  style: {version: 8, sources: {base: {type: 'raster', tiles: area.value==='japan'?['https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png']:[window.NIGIWAI_CONFIG.worldRaster || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, maxzoom:area.value==='japan'?18:19,
    attribution: area.value==='japan'?'<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>':'<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>'}},
    layers: [{id: 'base', type: 'raster', source: 'base', paint: {'raster-opacity': 0.42}}]}});
map.addControl(new maplibregl.NavigationControl(), 'top-right');
let initialLoading = true, peaksLoading = false, tilesLoading = false;
function renderLoading() {
  const busy = initialLoading || peaksLoading || tilesLoading;
  document.querySelector('#loading-status').hidden = !busy;
  document.querySelector('#loading-text').textContent = initialLoading ? '地図データを読み込み中…' : peaksLoading ? '地名とランキングを更新中…' : '地図を読み込み中…';
  document.querySelector('#map').setAttribute('aria-busy', String(busy));
}
map.on('dataloading', () => {tilesLoading = true; renderLoading();});
map.on('sourcedata', () => {tilesLoading = !map.areTilesLoaded(); renderLoading();});
map.on('idle', () => {tilesLoading = false; renderLoading();});
map.on('error', () => {tilesLoading = !map.areTilesLoaded(); renderLoading();});
document.querySelector('#panel-toggle').addEventListener('click', () => {
  const button = document.querySelector('#panel-toggle');
  const expanded = button.getAttribute('aria-expanded') !== 'true';
  button.setAttribute('aria-expanded', String(expanded));
  document.querySelector('#map-panel').dataset.expanded = String(expanded);
  document.querySelector('#panel-toggle-label').textContent = expanded ? '閉じる' : '開く';
});

const fsqAttribution = '<a href="licenses/Foursquare-NOTICE.txt">© 2026 Foursquare Labs, Inc.</a> · <a href="licenses/Apache-2.0.txt">Apache 2.0</a>';
let attributionControl = new maplibregl.AttributionControl({compact:false,customAttribution:fsqAttribution});
map.addControl(attributionControl,'bottom-right');
const palette = ['step', ['get', 'density'], '#dce9c2', 800, '#cadd9e', 1600, '#b8cf86', 2000, '#e2df94', 4000, '#ecd17f', 6000, '#dbb36b', 8000, '#c99a5d', 12000, '#b78050', 16000, '#995f40', 20000, '#79432f'];
let manifest, geo, peakGeo, selectedItem, stations = [], markers = [], ticket = 0, initialized = false, viewportTicket = 0;
let rankingPopup;
let places = [], peakIndex = null;
const chunkCache = new Map();
const overviewCache = new Map();
const empty = () => ({type: 'FeatureCollection', features: []});
function applyPeakLocalityNames(features) {
  return features.map(f => {
    let entry = area.value === 'world' && (window.NIGIWAI_PEAK_LOCALITY_NAMES || []).find(r =>
      r.coordinates.every((v,i) => Math.abs(v-f.geometry.coordinates[i]) < 1e-7) &&
      f.properties.name_source === r.source_id.split(':')[0] &&
      (f.properties.name_source_ids || []).map(String).includes(r.source_id.split(':')[1]));
    if(area.value==='world' && !entry){
      const key=f.geometry.coordinates.map(v=>v.toFixed(7)).join(',');
      const candidate=window.NIGIWAI_STATION_PEAK_NAMES?.[key];
      if(candidate && candidate.original_source===f.properties.name_source &&
        JSON.stringify(candidate.original_source_ids)===JSON.stringify(f.properties.name_source_ids || [])) entry=candidate;
    }
    const properties = {...f.properties};
    delete properties.reviewed_peak_locality;
    if(entry) properties.reviewed_peak_locality = entry;
    return {...f,properties};
  });
}
function originalPeakName(props) {
  if(area.value === 'world' && props.reviewed_peak_locality) return props.reviewed_peak_locality.name;
  if (area.value === 'japan' && props.municipality && /^[\d\s.,°NSEW+\-]+$/.test(props.name || '')) {
    return props.municipality + (props.admin_nearby ? '付近' : '');
  }
  if (area.value === 'world' && props.name_source === 'coordinates') {
    const entry=window.NIGIWAI_COORDINATE_NAMES?.[props.name];
    if(entry)return entry.name;
    const [lat,lon]=props.name.split(',').map(Number);
    if(Number.isFinite(lat)&&Number.isFinite(lon))return `地名未登録〔${lat>=0?'北緯':'南緯'}${Math.abs(lat).toFixed(3)}度・${lon>=0?'東経':'西経'}${Math.abs(lon).toFixed(3)}度〕`;
    return '地名未登録';
  }
  const dictionary = window.NIGIWAI_JAPANESE_NAMES?.[area.value] || {};
  const entry = (props.name_source_ids || []).map(id => dictionary[area.value === 'world' ? `${props.name_source}:${id}` : id]).find(Boolean);
  return entry ? (entry.display_name || entry.name) : props.name;
}
function peakName(props) {
  if(props.shared_reference) return props.display_name;
  if(props.name_source==='国土数値情報 N02' && (props.name_source_ids||[]).map(String).includes('003844')) return '明治神宮前〈原宿〉';
  return originalPeakName(props).replace(/駅付近|付近/gu,'');
}
function peakGroupKey(f) {
  if(f.properties.shared_reference) return f.properties.display_name;
  const props=applyPeakLocalityNames([f])[0].properties;
  return peakName(props);
}
function peakOriginal(props) {
  if (peakName(props) === props.name) return '';
  if(area.value === 'world' && props.reviewed_peak_locality) return `。元の名称: ${props.name}。${props.reviewed_peak_locality.basis}`;
  const entry = area.value === 'world' ? (props.name_source === 'coordinates' ? window.NIGIWAI_COORDINATE_NAMES?.[props.name] : (props.name_source_ids || []).map(id=>window.NIGIWAI_JAPANESE_NAMES?.world?.[`${props.name_source}:${id}`]).find(Boolean)) : null;
  return `。元の名称: ${props.name}${entry?.basis && props.name_source !== 'coordinates' ? '。'+entry.basis : ''}`;
}
function peakBasis(props) {
  if(area.value === 'world' && props.reviewed_peak_locality) return props.reviewed_peak_locality.station_distance_m===undefined?'周辺の商圏・施設名を参照した架空峰':'近隣駅名を参照した架空峰（峰の位置は駅と異なります）';
  if (area.value === 'world' && props.name_source === 'coordinates') {
    return window.NIGIWAI_COORDINATE_NAMES?.[props.name]?.basis || window.NIGIWAI_COORDINATE_WARNINGS?.[props.name]?.basis || props.name_basis || '架空峰';
  }
  if (area.value === 'world') {
    const entry=(props.name_source_ids || []).map(id=>window.NIGIWAI_JAPANESE_NAMES?.world?.[`${props.name_source}:${id}`]).find(Boolean);
    if(entry?.reference_kind === 'natural_landmark') return '近隣の自然地形名を参照した架空峰。参照地形の実標高ではありません';
  }
  return props.name_basis || '架空峰';
}
const dataRoot = () => new URL(areas[area.value].dataBase, location.href).href;
const selectedRegionId = () => worldOnly && region.value === 'japan' ? (document.querySelector('#subregion').value || 'japan') : region.value;
const saveURL = () => {
  history.replaceState(null,'',`${worldOnly ? '?' : '?area='+encodeURIComponent(area.value)+'&'}region=${encodeURIComponent(selectedRegionId())}`);
  const link=document.querySelector('#station-tier-link');
  if(link) link.href='station-tier.html?pref='+(selectedRegionId().startsWith('pref-')?selectedRegionId().slice(5):'13');
};
function subdivisionOptions() {
  if(!worldOnly) return;
  const select=document.querySelector('#subregion');select.replaceChildren();
  const all=document.createElement('option');all.value='';all.textContent='日本全域';select.append(all);
  for(const kind of ['japan-region','prefecture']) {
    const entries=Object.entries(regions).filter(([,r])=>r.parent==='japan' && r.group===kind);
    if(!entries.length) continue;
    const group=document.createElement('optgroup');group.label=kind==='prefecture'?'都道府県':'地方';
    for(const [id,r] of entries) {const option=document.createElement('option');option.value=id;option.textContent=r.name;group.append(option);}
    select.append(group);
  }
  select.value='';document.querySelector('#subregion-row').hidden=false;
}
const viewPadding = () => {
  const panel = document.querySelector('aside').getBoundingClientRect();
  return innerWidth > 680 ? {top:40,bottom:65,left:Math.ceil(panel.right+24),right:40} : {top:40,bottom:Math.ceil(innerHeight-panel.top+20),left:20,right:20};
};
const activeRegion = () => regions[selectedRegionId()] || Object.values(regions)[0];
const inRegion = f => {
  if(worldOnly){const [w,s,e,n]=activeRegion().bbox;const [x,y]=f.geometry?.coordinates || [f.properties.lon,f.properties.lat];return x>=w&&x<=e&&y>=s&&y<=n;}
  return !activeRegion()?.pref_codes?.length || activeRegion().pref_codes.includes(f.properties.pref_code);
};
function visiblePeaks() {
  const bounds = map.getBounds(), floor = Number(document.querySelector('#floor').value);
  const seen=new Set();
  return ((peakGeo || geo)?.features.filter(f => f.properties.kind === 'peak' && window.nigiwaiPeakAllowed(f,area.value) && f.properties.density >= floor && window.nigiwaiContainsPoint(bounds,f.geometry.coordinates)).sort((a,b) => b.properties.density - a.properties.density) || []).filter(f=>{const key=peakName(f.properties);if(seen.has(key))return false;seen.add(key);return true;});
}
const focusOffset = () => {const p = viewPadding(); return [(p.left-p.right)/2,(p.top-p.bottom)/2];};
function overview() {
  if (!manifest) return;
  const b = activeRegion().bbox;
  map.setPadding({top:0,bottom:0,left:0,right:0});
  map.fitBounds([[b[0], b[1]], [b[2], b[3]]], {padding:viewPadding(),duration:600});
}
function peakPopupContent(feature) {
  const props = feature.properties;
  const [lon, lat] = feature.geometry.coordinates;
  const content = document.createElement('section'); content.className = 'peak-popup';
  const title = document.createElement('h2'); title.textContent = peakName(props);
  const label = document.createElement('p'); label.className = 'metric-label'; label.textContent = 'お店・施設の登録密度';
  const value = document.createElement('p'); value.className = 'metric-value'; value.textContent = props.density.toLocaleString() + ' 件/km²';
  const description = document.createElement('p'); description.textContent = props.shared_reference ? '名前の参照点から半径800m以内で、登録密度が最も高い地点です。ならす広さは200mで、Tier表も同じ値を使います。' : '周辺の登録がどれだけ集まっているかの目安です。';
  const links = document.createElement('div'); links.className = 'popup-links';
  if (Number.isFinite(lon) && Number.isFinite(lat) && Math.abs(lon)<=180 && Math.abs(lat)<=90) {
    const coordinates = lat.toFixed(6) + ',' + lon.toFixed(6);
    for (const [text, path, parameter] of [['Googleマップで開く', 'search/', 'query'], ['ここへの経路', 'dir/', 'destination']]) {
      const url = new URL('https://www.google.com/maps/' + path);
      url.searchParams.set('api','1'); url.searchParams.set(parameter,coordinates);
      const link = document.createElement('a'); link.textContent=text; link.href=url.href;
      link.target='_blank'; link.rel='noopener noreferrer'; links.append(link);
    }
  }
  const note = document.createElement('p'); note.className='popup-note'; note.textContent=props.shared_reference ? 'リンク先は範囲内の最大密度地点です。駅の位置や実在の山頂ではありません。近隣の駅・地名が同じ地点を共有する場合があります。' : 'リンク先は▲の地点です。駅の入口や施設の場所とは異なる場合があります。';
  content.append(title,label,value,description,links,note);
  return content;
}
function labels() {
  markers.forEach(m => m.remove()); markers = [];
  const peaks = peakGeo || geo;
  if (!peaks) return;
  const floor = Number(document.querySelector('#floor').value);
  const occupied = [], usedNames = new Set();
  const bounds = map.getBounds();
  for (const f of peaks.features.filter(f => f.properties.kind === 'peak' && window.nigiwaiPeakAllowed(f,area.value) && f.properties.density >= floor).sort((a,b) => b.properties.density - a.properties.density)) {
    if (!window.nigiwaiContainsPoint(bounds,f.geometry.coordinates)) continue;
    const p = map.project(f.geometry.coordinates);
    if (occupied.some(q => Math.abs(p.x - q.x) < 100 && Math.abs(p.y - q.y) < 58)) continue;
    if (usedNames.has(peakName(f.properties))) continue;
    occupied.push(p); usedNames.add(peakName(f.properties));
    const el = document.createElement('div'); el.className = 'peak-label';
    for (const [cls, value] of [['triangle', f.properties.shared_reference ? '●' : '▲'], ['place', peakName(f.properties)], ['value', f.properties.density.toLocaleString()]]) {
      const node = document.createElement('div'); node.className = cls; node.textContent = value; el.append(node);
    }
    const props = f.properties;
    markers.push(new maplibregl.Marker({element: el}).setLngLat(f.geometry.coordinates).setPopup(new maplibregl.Popup({offset:16,maxWidth:'320px',className:'reader-popup'}).setDOMContent(peakPopupContent(f))).addTo(map));
    if (markers.length >= 100) break;
  }
}
function ranking() {
  const list = document.querySelector('#ranking-list'); list.replaceChildren();
  const floor = Number(document.querySelector('#floor').value);
  const peaks = visiblePeaks();
  const category = document.querySelector('#category').selectedOptions[0].textContent;
  document.querySelector('#ranking-title').textContent = `表示中の地名トップ20`;
  for (const f of peaks.slice(0,20)) {
    const li = document.createElement('li');
    const button = document.createElement('button'); button.type = 'button';
    const name = document.createElement('span'); name.textContent = peakName(f.properties);
    const value = document.createElement('span'); value.textContent = f.properties.density.toLocaleString();
    button.append(name, value); button.title = `${peakName(f.properties)} / ${f.properties.density.toLocaleString()} 件/km²`;
    button.addEventListener('click', () => {rankingPopup?.remove(); map.flyTo({center:f.geometry.coordinates,zoom:13,padding:0,offset:focusOffset(),duration:1200}); rankingPopup = new maplibregl.Popup({maxWidth:'320px',className:'reader-popup'}).setLngLat(f.geometry.coordinates).setDOMContent(peakPopupContent(f)).addTo(map);});
    li.append(button); list.append(li);
  }
}
function styleFloor() {
  const floor = Number(document.querySelector('#floor').value);
  for (const prefix of ['',...worldSources].map(id=>id?id+'-':'')) {
    for (const [id, kind] of [['bands', 'band'], ['terraces', 'band'], ['contours', 'contour']]) map.setFilter(prefix+id, ['all', ['==', 'kind', kind], ['>=', 'density', floor]]);
    map.setPaintProperty(prefix+'terraces', 'fill-extrusion-height', ['*', 6, ['sqrt', ['max', 0, ['-', ['get', 'density'], floor]]]]);
  }
  map.setPaintProperty('terraces', 'fill-extrusion-height', ['*', 6, ['sqrt', ['max', 0, ['-', ['get', 'density'], floor]]]]);
  document.querySelector('#floor-note').textContent = `${floor.toLocaleString()}件/km²未満は色を付けません。お店がないという意味ではありません。${map.getZoom() < 9 ? '概観では段彩を簡略表示。拡大すると等高線も表示します。' : ''}${manifest?.pilot?'試作範囲外は未計算です。':''}`;
  labels(); ranking();
}
async function viewport() {
  if (!peakIndex) return;
  worldDensity();
  const current = ++viewportTicket, index = peakIndex;
  peaksLoading = true; renderLoading();
  const bounds = map.getBounds(), floor = Number(document.querySelector('#floor').value);
  const boxes = window.nigiwaiViewBoxes(bounds);
  try {
    // Keep the raw top100 for map labels, and supplement it with the exact
    // distinct top20 so a single city's many peaks cannot starve the ranking.
    const eligible=f=>window.nigiwaiPeakAllowed(f,area.value);
    const results = await Promise.all(boxes.flatMap(b=>[
      index.query(b,floor,100,eligible),
      index.query(b,floor,20,eligible,peakGroupKey)
    ]));
    if (current !== viewportTicket || index !== peakIndex) return;
    const unique = new Map();
    for (const f of results.flat()) unique.set(f.properties.reference_id || JSON.stringify(f.geometry.coordinates),f);
    peakGeo = {type:'FeatureCollection',features:applyPeakLocalityNames([...unique.values()])};
    if(manifest?.world) {const options=document.querySelector('#station-options');options.replaceChildren();for(const name of new Set([...stations.map(s=>s.name),...peakGeo.features.map(f=>peakName(f.properties))])) {const option=document.createElement('option');option.value=name;options.append(option);}}
    labels(); ranking();
  } catch (e) {if(current===viewportTicket) {peakGeo=empty(); labels(); ranking(); document.querySelector('#stats').textContent='峰データの読み込みに失敗しました。地図を動かすと再試行します。';}} finally {if(current===viewportTicket) {peaksLoading=false;renderLoading();}}
}
function background() {
  const overseas = !!(manifest.pilot || manifest.world);
  map.removeLayer('base'); map.removeSource('base');
  map.addSource('base',{type:'raster',tileSize:256,maxzoom:overseas?19:18,
    tiles:overseas?[window.NIGIWAI_CONFIG.worldRaster || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png']:['https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png'],
    attribution:overseas?'<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>':'<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>'});
  map.addLayer({id:'base',type:'raster',source:'base',paint:{'raster-opacity':.42}},'bands');
  map.removeControl(attributionControl);
  attributionControl=new maplibregl.AttributionControl({compact:false,customAttribution:fsqAttribution+' | '+(overseas?'<a href="licenses/OSM-NOTICE.txt">駅・地名: OpenStreetMap / ODbL</a>':'<a href="https://nlftp.mlit.go.jp/ksj/">国土数値情報（国土交通省）加工</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>')});
  map.addControl(attributionControl,'bottom-right');
  document.querySelector('#reference-credit').innerHTML=overseas?'駅・都市・地区名と背景: <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors / ODbL</a>。駅の重複統合と近隣名による補完を実施。山の日本語名を<a href="https://www.wikidata.org/wiki/Wikidata:Licensing">Wikidata（CC0）</a>で補完。<a href="licenses/OSM-NOTICE.txt">加工内容・ライセンス</a>。背景を透過表示し密度図を重ねています。':'駅・行政区域: <a href="https://nlftp.mlit.go.jp/ksj/">国土数値情報（国土交通省）</a>加工 / CC BY 4.0。背景: <a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>を透過表示。';
  document.querySelector('#name-note').textContent=overseas?'▲はOSMの近隣駅名（1.5km以内）。駅が遠い場合は都市・地区名に「付近」を付ける参考表示で、行政区域の包含判定ではありません。山の名前はOSM・Wikidataの日本語名を優先し、未登録なら現地名。背景の文字と青い参照駅は元の表記です。':'▲は近隣駅名（1.5km以内）。駅から遠い峰は所属市区町村名。区域外1.5km以内は「付近」、参照できなければ座標表示。青い点は駅です。';
  document.querySelector('#station-search').placeholder=overseas?'駅・都市名を候補から選択':'駅名（例: 立川、渋谷）';
  document.querySelector('#method-scope').textContent=overseas?'地域中心の正積投影と100m格子で密度を計算。国境で入力を切らず、最大σ800mに対して3,750mの計算余白を取得。描画と峰は試作範囲で切り出しており、範囲外は未計算です。国ごとに登録状況が違うため実際のにぎわいの国際順位には使えません。':'100m格子、4σ以上の余白で登録密度を計算。県境で密度を切らず全国共通の計算を使用。地域選択は移動先を切り替え、ランキングは現在の表示範囲で更新します。中部に新潟・北陸・甲信・東海、近畿に三重を含みます。';
  if(manifest.world) {
    document.querySelector('#coverage').textContent='世界（極域を除く）・お店と施設の登録密度';
    document.querySelector('#reference-credit').innerHTML='背景: <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>。山の名称: GeoNames / CC BY 4.0、Natural Earth / public domain、Wikidata / CC0、国土数値情報、取得済みOSM駅。<a href="licenses/World-Names-NOTICE.txt">名称の出典と加工内容</a>';
    document.querySelector('#station-search').placeholder='駅名・表示中の山の名前';
    document.querySelector('#name-note').textContent='▲は参照地名を使った架空峰の代表点です。日本はN02、韓国は取得済みOSM駅、その他は都市・地区などの参照名を使用します。地名が示す区域の中心や実在の山ではありません。同じ地名は表示範囲で最大密度の峰を一度だけ表示し、別地域の同名地名は地域等を併記します。日本語登録名を優先し、未登録分は言語モデル等の音写を使います。公的な日本語名として全件確認した意味ではありません。元表記・距離・出典・音写の区別は峰を押して確認できます。背景の文字は元表記です。';
    document.querySelector('#method-scope').textContent='世界共通の約0.0009度格子を用い、緯度に応じた距離と面積で密度を近似計算。区画を重ねて計算し境界の峰を補正。極域は表示対象外です。国・地域で登録状況が異なるため実際の人出の国際順位には使えません。';
    map.removeControl(attributionControl);attributionControl=new maplibregl.AttributionControl({compact:false,customAttribution:fsqAttribution+' | <a href="licenses/World-Names-NOTICE.txt">名称: GeoNames / CC BY 4.0 · N02 · OSM</a>'});map.addControl(attributionControl,'bottom-right');
  }
  document.querySelector('#category-note').textContent=worldOnly?'業種はすべて、ならす広さはσ200mで共通です。表示下限は描画する密度の下限を変え、密度の計算条件は変えません。':'サービスは理美容・修理・金融・不動産などの業務サービスと医療で、事務所・製造業も含みます。'+(overseas?'海外はFoursquareの上位分類を使い、複数分類は飲食・買い物・サービスの順で1区分にします。「すべて」にはその他の施設も含むため、3業種の合計とは異なります。':'飲食・買い物は従来の名称による分類を維持し、サービスと一部重複するため業種別件数は足し合わせられません。');
}
const worldSources = new Set();
function worldDensity() {
  if (!manifest?.world) return;
  const boxes=window.nigiwaiViewBoxes(map.getBounds());
  const needed=new Set(map.getZoom()>=8 ? manifest.packages.filter(p=>boxes.some(([w,s,e,n])=>p.bbox[2]>=w&&p.bbox[0]<=e&&p.bbox[3]>=s&&p.bbox[1]<=n)).map(p=>p.id) : []);
  for (const id of [...worldSources]) if(!needed.has(id)) {for(const kind of ['bands','terraces','contours']) map.removeLayer(id+'-'+kind);map.removeSource(id);worldSources.delete(id);}
  for (const p of manifest.packages) if(needed.has(p.id)&&!worldSources.has(p.id)) {
    map.addSource(p.id,{type:'vector',url:'pmtiles://'+new URL(p.pmtiles,dataRoot()).href,minzoom:9,maxzoom:12});
    for(const kind of ['bands','terraces','contours']) {const layer=structuredClone(map.getStyle().layers.find(l=>l.id===kind));layer.id=p.id+'-'+kind;layer.source=p.id;layer.minzoom=9;layer.maxzoom=24;map.addLayer(layer,'station-points');}
    worldSources.add(p.id);
  }
}
function densitySource(item) {
  for(const id of worldSources) {for(const kind of ['bands','terraces','contours']) map.removeLayer(id+'-'+kind);map.removeSource(id);}
  worldSources.clear();
  for (const id of ['bands','terraces','contours']) if (map.getLayer(id)) map.removeLayer(id);
  if (map.getSource('density')) map.removeSource('density');
  map.addSource('density', {type:'vector', url:'pmtiles://' + new URL(item.pmtiles_file, dataRoot()).href});
  const three = document.querySelector('#three').checked;
  map.addLayer({id:'bands',type:'fill',source:'density','source-layer':'density',layout:{visibility:three?'none':'visible'},paint:{'fill-color':palette,'fill-opacity':0.66}},'station-points');
  map.addLayer({id:'terraces',type:'fill-extrusion',source:'density','source-layer':'density',layout:{visibility:three?'visible':'none'},paint:{'fill-extrusion-color':palette,'fill-extrusion-height':0,'fill-extrusion-opacity':0.9}},'station-points');
  map.addLayer({id:'contours',type:'line',source:'density','source-layer':'density',paint:{'line-color':'#887955','line-width':['case',['get','index'],1.15,0.55],'line-opacity':0.75}},'station-points');
}
async function read(url) {
  const response = await fetch(url, {cache:'no-cache'});
  if (!response.ok) throw Error('地図データを取得できませんでした。通信状況を確認して再読み込みしてください。');
  return response.json();
}
async function update(sourceChanged = false) {
  const current = ++ticket;
  rankingPopup?.remove();
  initialLoading=true; renderLoading();
  const root = dataRoot();
  try {
    if (sourceChanged || !manifest) {
      manifest = null; geo = null; peakGeo = null; peakIndex = null; selectedItem = null; ++viewportTicket; peaksLoading=false; chunkCache.clear(); overviewCache.clear(); labels(); ranking();
      const [newManifest, newStations, newRegions] = await Promise.all([read(root + 'manifest.json'), read(root + 'stations.json'), read(root + 'regions.json')]);
      const newPlaces = newManifest.reference_names ? await read(root+'places.json') : [];
      if (current !== ticket) return;
      regions = worldOnly ? {...newRegions,...window.NIGIWAI_WORLD_REGIONS} : newRegions;
      region.replaceChildren();
      const groups = [document.createElement('optgroup'), document.createElement('optgroup'), document.createElement('optgroup')];
      groups.forEach((g,i) => {g.label = worldOnly ? ['世界・大陸','国・地域','その他'] : newManifest.world ? ['世界・大陸','地域','区域'] : newManifest.pilot ? ['海外試作','地方','行政区域'][i] : ['全国','地方','都道府県'][i]; if(!worldOnly || i<2)region.append(g);});
      for (const [key,value] of Object.entries(regions)) {if(worldOnly && value.parent)continue; const option=document.createElement('option'); option.value=key; option.textContent=value.name; groups[worldOnly?(value.group==='country'?1:0):key==='japan'||newManifest.pilot||newManifest.world?0:key.startsWith('pref-')?2:1].append(option);}
      region.value = !initialized && requestedRegion === 'tokyo' && area.value==='japan' ? 'pref-13' : (!initialized && regions[requestedRegion] ? requestedRegion : Object.keys(regions)[0]);
      if(worldOnly) {
        const target=!initialized?(requestedRegion==='tokyo'?'pref-13':requestedRegion):region.value;
        region.value=regions[target]?.parent || (regions[target]?target:'world');
        subdivisionOptions();if(regions[target]?.parent)document.querySelector('#subregion').value=target;
      }
      if (current !== ticket) return;
      manifest = newManifest; stations = worldOnly ? [...newStations,...(window.NIGIWAI_REFERENCE_STATIONS || [])] : newStations; places = newPlaces;
      document.querySelector('#source').textContent = `Foursquare OS Places · ${manifest.snapshots.places.timestamp.slice(0,10)}版（閉店判明分除外）`;
      const qualityNote=document.querySelector('#quality-note');
      qualityNote.hidden=true;
      qualityNote.textContent=manifest.world?(manifest.density_quality?`位置品質を個別に確認した地点の${manifest.density_quality.excluded_ids.toLocaleString()}件を計算保留にして地形を再生成しました。全件の誤位置が確定した意味ではなく、住所不足の正常な登録が含まれる可能性もあります。`:'位置品質に問題が疑われる13峰は▲・名称・数値・ランキングから保留しています（8峰は強い疑い、5峰は暫定保留）。段彩・等高線・3Dには元の登録密度が残ります。'):'';
      document.querySelector('#coverage').textContent = `${manifest.world || manifest.pilot ? manifest.coverage : '日本全国（離島を含む）'}・参照 ${manifest.station_groups.toLocaleString()}駅グループ${manifest.pilot?'（周辺余白を含む）':''}`;
      for (const id of ['sigma','category']) {
        const select = document.querySelector('#'+id);
        for (const option of select.options) option.disabled = !manifest.datasets.some(d => String(d[id]) === option.value);
        if (select.selectedOptions[0].disabled) select.value = [...select.options].find(o=>!o.disabled).value;
      }
      document.querySelector('#poi-credit').textContent = '© 2026 Foursquare Labs, Inc. / Apache 2.0。選択地域と周辺の登録を抽出し、分類・閉店判明分除外・密度計算・等高線化を実施。';
      const options = document.querySelector('#station-options'); options.replaceChildren();
      [...new Set([...stations,...places].flatMap(s => [s.name, ...(s.osm_ids || []).map(id=>window.NIGIWAI_JAPANESE_NAMES?.[area.value]?.[id]?.name).filter(Boolean)]))].sort().forEach(name => {const option = document.createElement('option'); option.value = name; options.append(option);});
      map.getSource('stations').setData({type: 'FeatureCollection', features: stations.map(s => ({type: 'Feature', geometry: {type: 'Point', coordinates: [s.lon, s.lat]}, properties: {name: s.name, source:s.source || (manifest.pilot?'OSM':'N02')}}))});
      background(); overview(); initialized = true;
      saveURL();
    }
    const item = manifest.datasets.find(d => d.sigma === Number(document.querySelector('#sigma').value) && d.category === document.querySelector('#category').value && (d.status || 'all') === 'exclude');
    if (!item) throw Error('閉店条件のデータを生成中です。少し後で再読み込みしてください。');
    let nextGeo = empty(), nextIndex = null;
    if (item.peaks_index) {
      const url=window.NIGIWAI_CONFIG.referenceIndex || new URL(item.peaks_index,root).href;
      nextIndex=new window.NigiwaiPeakIndex(new URL('.',url).href,await read(url),read);
    } else nextGeo=await read(root + (item.peaks_file || item.file));
    if (current !== ticket) return;
    ++viewportTicket; selectedItem = item; peakGeo = {...nextGeo,features:applyPeakLocalityNames(nextGeo.features)}; peakIndex = nextIndex;
    densitySource(item);
    if(manifest.world) for(const id of ['bands','terraces','contours']) map.setLayerZoomRange(id,0,9);
    styleFloor();
    document.querySelector('#stats').textContent = '';
    await viewport();
  } catch (e) {if (current === ticket) {document.querySelector('#stats').textContent = e.message; manifest = null;}} finally {if(current===ticket) {initialLoading=false;renderLoading();}}
}
map.on('load', async () => {
  map.addSource('density', {type: 'geojson', data: empty()});
  map.addLayer({id: 'bands', type: 'fill', source: 'density', paint: {'fill-color': palette, 'fill-opacity': 0.66}});
  map.addLayer({id: 'terraces', type: 'fill-extrusion', source: 'density', layout: {visibility: 'none'}, paint: {'fill-extrusion-color': palette, 'fill-extrusion-height': 0, 'fill-extrusion-opacity': 0.9}});
  map.addLayer({id: 'contours', type: 'line', source: 'density', paint: {'line-color': '#887955', 'line-width': ['case', ['get', 'index'], 1.15, 0.55], 'line-opacity': 0.75}});
  map.addSource('stations', {type: 'geojson', data: empty()});
  map.addLayer({id: 'station-points', type: 'circle', source: 'stations', minzoom: 10.5, paint: {'circle-radius': 2, 'circle-color': '#52647b', 'circle-opacity': 0.7}});
  map.on('click', 'station-points', e => new maplibregl.Popup({className:'reader-popup'}).setLngLat(e.lngLat).setText(e.features[0].properties.name + '（駅）').addTo(map));
  area.addEventListener('change',()=>update(true));
  region.addEventListener('change', () => {subdivisionOptions(); rankingPopup?.remove(); saveURL(); overview(); labels(); ranking();});
  if(worldOnly) document.querySelector('#subregion').addEventListener('change',()=>{region.value='japan';rankingPopup?.remove();saveURL();overview();labels();ranking();});
  for (const id of ['category', 'sigma']) document.querySelector('#' + id).addEventListener('change', () => update());
  document.querySelector('#floor').addEventListener('change',()=>{styleFloor(); viewport();});
  document.querySelector('#three').addEventListener('change', e => {
    for(const prefix of ['',...worldSources].map(id=>id?id+'-':'')) {map.setLayoutProperty(prefix+'terraces', 'visibility', e.target.checked ? 'visible' : 'none');map.setLayoutProperty(prefix+'bands', 'visibility', e.target.checked ? 'none' : 'visible');}
    map.easeTo({pitch: e.target.checked ? 45 : 0});
  });
  document.querySelector('#overview').addEventListener('click', overview);

  let locationMarker;
  document.querySelector('#locate').addEventListener('click', () => {
    const status = document.querySelector('#search-status');
    if (!navigator.geolocation) {status.textContent='このブラウザでは現在地を利用できません'; return;}
    status.textContent='現在地を取得中…';
    navigator.geolocation.getCurrentPosition(position => {
      const coords=[position.coords.longitude,position.coords.latitude];
      locationMarker?.remove(); locationMarker=new maplibregl.Marker({color:'#277cb8'}).setLngLat(coords).addTo(map);
      map.flyTo({center:coords,zoom:13,padding:0,offset:focusOffset()});
      status.textContent='現在地へ移動（位置情報は保存しません）';
    }, error => {status.textContent=({1:'位置情報の利用が許可されていません',2:'現在地を取得できません',3:'現在地の取得が時間切れになりました'})[error.code] || '現在地を取得できません';}, {enableHighAccuracy:true,timeout:10000,maximumAge:60000});
  });
  let searchMarker;
  function markSearch(coords, name) {
    searchMarker?.remove();
    const label = document.createElement('div');
    label.className = 'search-position-label';
    label.textContent = name;
    searchMarker = new maplibregl.Marker({color:'#1768ac'})
      .setLngLat(coords)
      .setPopup(new maplibregl.Popup({offset:28,closeButton:false,className:'search-position-popup'}).setDOMContent(label))
      .addTo(map);
    searchMarker.togglePopup();
    map.flyTo({center:coords,zoom:13,padding:0,offset:focusOffset(),duration:1200});
  }
  function search() {
    const typed = document.querySelector('#station-search').value.trim().replace(/駅$/, '');
    const value = typed === 'お茶の水' ? '御茶ノ水' : typed;
    const station = stations.find(s => s.name === value && inRegion({properties:s})) || stations.find(s => s.name === value) || places.find(s=>s.name===value) || [...stations,...places].find(s=>(s.osm_ids || []).some(id=>window.NIGIWAI_JAPANESE_NAMES?.[area.value]?.[id]?.name===value));
    const worldPeak=manifest?.world && peakGeo?.features.find(f=>peakName(f.properties)===value);
    if (station) {markSearch([station.lon, station.lat], station.name + (stations.includes(station) ? '駅' : '')); document.querySelector('#search-status').textContent = station.name + 'の位置を青いマーカーで表示';}
    else if(worldPeak) {markSearch(worldPeak.geometry.coordinates,value);document.querySelector('#search-status').textContent=value+'の位置を青いマーカーで表示';}
    else document.querySelector('#search-status').textContent = '駅・都市名を候補から選んでください';
  }
  document.querySelector('#search').addEventListener('click', search);
  document.querySelector('#station-search').addEventListener('keydown', e => {if (e.key === 'Enter') search();});
  map.on('moveend', () => {styleFloor(); viewport();});
  await update(true);
  if(stationView && Object.values(stationView).every(Number.isFinite) && Math.abs(stationView.lat)<=85 && Math.abs(stationView.lon)<=180 && stationView.zoom>=0 && stationView.zoom<=19){
    map.stop();map.jumpTo({center:[stationView.lon,stationView.lat],zoom:stationView.zoom,padding:0});await viewport();
  }
  document.querySelector('#controls').disabled = false;
});
