// Pure application logic test with DOM/MapLibre doubles; no browser or network.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const worldFolder=process.env.NIGIWAI_TEST_WORLD_FOLDER || 'foursquare-world';
const distributionPath=p=>'data/distribution'+p.replace('/foursquare-world/','/'+worldFolder+'/');
class Element {
  constructor(tag='div') {this.tag=tag;this.children=[];this.listeners={};this.value='';this.textContent='';this.disabled=false;this.checked=false;}
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children=items;}
  get options() {return this.children.flatMap(e=>e.tag==='optgroup'?e.children:[e]);}
  get selectedOptions() {return this.options.filter(o=>o.value===this.value);}
  addEventListener(name,callback) {this.listeners[name]=callback;}
  setAttribute(name,value) {this[name]=value;}
  getBoundingClientRect() {return {right:369,top:0};}
}
class FakeMap {
  constructor(options) {this.sources=new Map();this.layers=new Map();this.events=new Map();this.bbox=[122,20,154,46];for(const [id,s] of Object.entries(options.style.sources))this.addSource(id,s);for(const l of options.style.layers)this.addLayer(l);}
  addSource(id,s) {this.sources.set(id,{...s,setData(data){this.data=data;}});}
  getSource(id) {return this.sources.get(id);}
  removeSource(id) {this.sources.delete(id);}
  addLayer(layer,before) {if(before)assert(this.layers.has(before));this.layers.set(layer.id,layer);}
  getLayer(id) {const layer=this.layers.get(id);return layer?{...layer,serialize:()=>layer}:undefined;}
  setLayerZoomRange(id,min,max) {this.layers.get(id).minzoom=min;this.layers.get(id).maxzoom=max;}
  getStyle() {return {layers:[...this.layers.values()]};}
  removeLayer(id) {this.layers.delete(id);}
  on(name,...args) {this.events.set(name,args.at(-1));}
  addControl() {} removeControl() {} setFilter() {} setPaintProperty() {} setLayoutProperty() {} setPadding() {} easeTo() {}
  fitBounds(b) {this.bbox=[...b[0],...b[1]];}
  flyTo(options) {this.lastFlyTo=options;}
  getBounds() {const b=this.bbox;return {getWest:()=>b[0],getSouth:()=>b[1],getEast:()=>b[2],getNorth:()=>b[3]};}
  getZoom() {return 11;}
  project([x,y]) {return {x:x*2000,y:y*2000};}
}
class Overlay {setLngLat(coords){this.coords=coords;return this;}setPopup(popup){this.popup=popup;return this;}setText(){return this;}setDOMContent(content){this.content=content;return this;}addTo(){return this;}togglePopup(){this.open=true;return this;}remove(){}}
const ids=new Map();
const get=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
for(const [id,values] of [['category',['all','food','shopping','service']],['sigma',['200','400','800']],['floor',['100','800','1600']]]) {
  const select=get(id);select.tag='select';for(const value of values){const option=new Element('option');option.value=value;option.textContent=value;select.append(option);}select.value=id==='floor'?'800':values[0];
}
const config={dataBase:'https://example.invalid/foursquare-japan/',areas:{}};
if(process.env.NIGIWAI_PUBLIC_WORLD)config.worldOnly=true;
for(const region of ['world','sg-singapore','gb-london','is-reykjavik'])config.areas[region]={name:region,dataBase:`https://example.invalid/foursquare-${region}/`};
const context=vm.createContext({window:{NIGIWAI_CONFIG:config},URL,URLSearchParams,Map,Set,Promise,Math,JSON,console,structuredClone,
  location:{href:'https://example.invalid/',search:''},history:{replaceState(){}},innerWidth:1200,innerHeight:900,navigator:{},
  document:{querySelector:selector=>get(selector),createElement:tag=>new Element(tag)},
  maplibregl:{Map:FakeMap,NavigationControl:class{},AttributionControl:class{},Marker:Overlay,Popup:Overlay,addProtocol(){}},
  pmtiles:{Protocol:class{tile(){}}},fetch:async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(distributionPath(new URL(url).pathname),'utf8'))})});
// App uses selectors including # prefixes.
context.document.querySelector=selector=>get(selector.startsWith('#')?selector.slice(1):selector);
vm.runInContext(fs.readFileSync('web/peak-index.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/peak-quality.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/japanese-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-japanese-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-name-overrides.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-reviewed-names.js','utf8'),context);
if(config.worldOnly)vm.runInContext(fs.readFileSync('web/world-display-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-coordinate-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-peak-locality-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-regions.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-station-peak-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-reference-stations.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/app.js','utf8'),context);
(async()=>{
  await vm.runInContext("map.events.get('load')()",context);
  if(config.worldOnly){
    assert.equal(vm.runInContext('area.value',context),'world');
    get('region').value='japan';get('region').listeners.change();
    assert.equal(get('subregion').options.length,57);
    for(const id of ['pref-13','pref-40','kanto']){
      get('subregion').value=id;get('subregion').listeners.change();
      assert.equal(vm.runInContext('selectedRegionId()',context),id);
      assert.equal(vm.runInContext('manifest.world',context),true);
      assert(vm.runInContext('dataRoot()',context).includes('foursquare-world/'));
      assert(vm.runInContext('activeRegion().bbox.length',context)===4);
      await vm.runInContext('viewport()',context);
      assert(get('ranking-list').children.length<=20);
    }
    get('region').value='country-kr';get('region').listeners.change();
    assert.equal(get('subregion-row').hidden,false);
    assert.equal(get('subregion').options.length,57);
    assert.equal(get('subregion').value,'');
    assert.equal(vm.runInContext('activeRegion().country_code',context),'KR');
    get('subregion').value='pref-13';get('subregion').listeners.change();
    assert.equal(get('region').value,'japan');
    assert.equal(vm.runInContext('selectedRegionId()',context),'pref-13');
    assert(vm.runInContext("stations.some(s=>s.name==='渋谷' && s.source==='N02')",context));
    get('station-search').value='お茶の水駅';
    get('search').listeners.click();
    const ochanomizu=vm.runInContext("stations.find(s=>s.name==='御茶ノ水')",context);
    assert(ochanomizu);
    assert.deepEqual(Array.from(vm.runInContext('map.lastFlyTo.center',context)),[ochanomizu.lon,ochanomizu.lat]);
    assert.equal(get('search-status').textContent,'御茶ノ水の位置を青いマーカーで表示');
    assert(vm.runInContext("stations.some(s=>s.name==='ホンデイック' && s.source==='OSM')",context));
    const labels=context.window.NIGIWAI_STATION_PEAK_NAMES;
    assert.equal(Object.keys(labels).length,1007);
    assert(Object.values(labels).every(p=>p.station_distance_m<=1500 && p.source_urls[0].startsWith('https://www.openstreetmap.org/')));
    const report=JSON.parse(fs.readFileSync('data/validation/world-station-labels.json','utf8'));
    assert.equal(report.seoul_top20_unique_after,20);
    assert(!report.seoul_top20.some(p=>/^(Seoul|Yongsan|ソウル|ヨンサン)/.test(p.after)));
    console.log('Unified world source: Japan 9 regions/47 prefectures, Korea navigation, viewport top20 verified');
    return;
  }
  for(const region of ['world','sg-singapore','gb-london','is-reykjavik','japan']) {
    get('area').value=region;
    await get('area').listeners.change();
    const state=vm.runInContext('({manifest,stations,places,peakIndex,map})',context);
    assert.equal(Boolean(state.manifest.pilot || state.manifest.world),region!=='japan');
    assert.equal(Boolean(state.peakIndex),region!=='japan');
    if(region!=='japan') assert.equal(state.manifest.region_id,region);
    assert(get('reference-credit').innerHTML.includes(region==='japan'?'国土数値情報':'OpenStreetMap'));
    const expectedRoot=config.areas[region]?.dataBase || config.dataBase;
    assert(state.map.getSource('density').url.startsWith('pmtiles://'+expectedRoot));
    const tileURL=state.map.getSource('base').tiles[0];
    assert(tileURL.includes(region==='japan'?'cyberjapandata.gsi.go.jp':'tile.openstreetmap.org'));
    if(region==='world') {
      if(state.manifest.density_quality)assert(get('quality-note').textContent.includes(state.manifest.density_quality.excluded_ids.toLocaleString()));
      context.nameFixture={name_source:'coordinates',name:Object.keys(context.window.NIGIWAI_COORDINATE_NAMES)[0]};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),context.window.NIGIWAI_COORDINATE_NAMES[context.nameFixture.name].name);
      context.nameFixture={name_source:'coordinates',name:'99.999, 99.999'};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'99.999, 99.999');
      context.nameFixture={name_source:'coordinates',name:'37.449, 126.452',name_basis:'15km以内に参照地名なし'};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'インチョン国際空港付近');
      assert(vm.runInContext('peakBasis(nameFixture)',context).includes('ID 6300433'));
      assert(!vm.runInContext('peakBasis(nameFixture)',context).includes('参照地名なし'));
      context.nameFixture={name_source:'coordinates',name:'31.878, 53.438'};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'31.878, 53.438');
      assert(vm.runInContext('peakBasis(nameFixture)',context).includes('位置精度'));
      context.nameFixture={name:'Nago付近',name_source:'GeoNames',name_source_ids:['1856068'],place_distance_m:20};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'名護市付近');
      assert(vm.runInContext('peakOriginal(nameFixture)',context).includes('元の地区名の翻訳ではありません'));
      for(const [id,name] of [['1841988','クリ'],['1842859','コチャン'],['1809858','広州'],['1805753','済南'],['4498303','ウェスト・ローリー']]) {
        context.nameFixture={name:'Original',name_source:'GeoNames',name_source_ids:[id],place_distance_m:200};
        assert.equal(vm.runInContext('peakName(nameFixture)',context),name+'付近');
      }
      assert.equal(get('category').options.filter(o=>!o.disabled).length,1);
      assert(state.map.layers.size>6);
      for(const [id,l] of state.map.layers) if(id.startsWith('global-')) assert(l.minzoom===9 && l.maxzoom>12);
      for(const bbox of [[-180,-85,180,85],[139.6,35.5,139.9,35.8],[170,-30,190,0]]) {
        state.map.bbox=bbox;
        await vm.runInContext('styleFloor(); viewport()',context);
        const boxes=context.window.nigiwaiViewBoxes(state.map.getBounds());
        const expected=[];
        for(const part of state.manifest.packages) if(boxes.some(([w,s,e,n])=>part.bbox[2]>=w&&part.bbox[0]<=e&&part.bbox[3]>=s&&part.bbox[1]<=n)) {
          const full=JSON.parse(fs.readFileSync(distributionPath('/foursquare-world/'+part.id+'/200-all-peaks.json'),'utf8')).features;
          expected.push(...full.filter(f=>context.window.nigiwaiPeakAllowed(f,region)&&f.properties.density>=Number(get('floor').value)&&context.window.nigiwaiContainsPoint(state.map.getBounds(),f.geometry.coordinates)));
        }
        expected.sort((a,b)=>b.properties.density-a.properties.density);
        assert.deepEqual(get('ranking-list').children.map(li=>Number(li.children[0].children[1].textContent.replaceAll(',',''))),expected.slice(0,20).map(f=>f.properties.density));
      }
      continue;
    }
    for(const item of state.manifest.datasets) {
      get('category').value=item.category;get('sigma').value=String(item.sigma);
      await get('category').listeners.change();
      const full=JSON.parse(fs.readFileSync(`data/distribution/foursquare-${region}/${item.peaks_file}`,'utf8')).features;
      for(const floor of [100,800,1600]) {
        get('floor').value=String(floor);
        await vm.runInContext('styleFloor(); viewport()',context);
        const expected=full.filter(f=>f.properties.density>=floor).sort((a,b)=>b.properties.density-a.properties.density).slice(0,20).map(f=>f.properties.density);
        const actual=get('ranking-list').children.map(li=>Number(li.children[0].children[1].textContent.replaceAll(',','')));
        assert.deepEqual(actual,expected);
      }
    }
    if(region!=='japan') {
      const entries=Object.entries(context.window.NIGIWAI_JAPANESE_NAMES[region]);
      assert(entries.length>0);
      const [id,entry]=entries[0];
      context.nameFixture={name:'Original',name_source_ids:[id]};
      if(region==='world') {
        const split=id.indexOf(':');
        context.nameFixture.name_source=id.slice(0,split);
        context.nameFixture.name_source_ids=[id.slice(split+1)];
      }
      assert.equal(vm.runInContext('peakName(nameFixture)',context),entry.name);
      context.nameFixture.place_distance_m=100;
      assert.equal(vm.runInContext('peakName(nameFixture)',context),entry.name+'付近');
      context.nameFixture.name_source_ids=['node/unknown'];
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'Original');
    }
    if(region==='japan') {
      context.nameFixture={name:'36.14°N 139.54°E',municipality:'羽生市',admin_nearby:false};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'羽生市');
      context.nameFixture={name:'JR松山駅前',municipality:'松山市'};
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'JR松山駅前');
    }
    if(region==='is-reykjavik') {
      assert.equal(state.stations.length,0);
      get('station-search').value=state.places[0].name;
      get('search').listeners.click();
      assert(state.map.lastFlyTo);
    }
    assert.equal(get('stats').textContent.includes('失敗'),false);
  }
  console.log('World source switching and exact top20 (global, Tokyo, date-line) plus Japan/pilot regressions verified');
})().catch(e=>{console.error(e);process.exitCode=1;});
