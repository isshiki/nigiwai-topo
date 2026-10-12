// Pure application logic test with DOM/MapLibre doubles; no browser or network.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Element {
  constructor(tag='div') {this.tag=tag;this.children=[];this.listeners={};this.value='';this.textContent='';this.disabled=false;this.checked=false;}
  append(...items) {this.children.push(...items);}
  replaceChildren(...items) {this.children=items;}
  get options() {return this.children.flatMap(e=>e.tag==='optgroup'?e.children:[e]);}
  get selectedOptions() {return this.options.filter(o=>o.value===this.value);}
  addEventListener(name,callback) {this.listeners[name]=callback;}
  getBoundingClientRect() {return {right:369,top:0};}
}
class FakeMap {
  constructor(options) {this.sources=new Map();this.layers=new Map();this.events=new Map();this.bbox=[122,20,154,46];for(const [id,s] of Object.entries(options.style.sources))this.addSource(id,s);for(const l of options.style.layers)this.addLayer(l);}
  addSource(id,s) {this.sources.set(id,{...s,setData(data){this.data=data;}});}
  getSource(id) {return this.sources.get(id);}
  removeSource(id) {this.sources.delete(id);}
  addLayer(layer,before) {if(before)assert(this.layers.has(before));this.layers.set(layer.id,layer);}
  getLayer(id) {return this.layers.get(id);}
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
class Overlay {setLngLat(){return this;}setPopup(){return this;}setText(){return this;}addTo(){return this;}remove(){}}
const ids=new Map();
const get=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
for(const [id,values] of [['category',['all','food','shopping','service']],['sigma',['200','400','800']],['floor',['100','800','1600']]]) {
  const select=get(id);select.tag='select';for(const value of values){const option=new Element('option');option.value=value;option.textContent=value;select.append(option);}select.value=id==='floor'?'800':values[0];
}
const config={dataBase:'https://example.invalid/foursquare-japan/',areas:{}};
for(const region of ['sg-singapore','gb-london','is-reykjavik'])config.areas[region]={name:region,dataBase:`https://example.invalid/foursquare-${region}/`};
const context=vm.createContext({window:{NIGIWAI_CONFIG:config},URL,URLSearchParams,Map,Set,Promise,Math,JSON,console,
  location:{href:'https://example.invalid/',search:''},history:{replaceState(){}},innerWidth:1200,innerHeight:900,navigator:{},
  document:{querySelector:selector=>get(selector),createElement:tag=>new Element(tag)},
  maplibregl:{Map:FakeMap,NavigationControl:class{},AttributionControl:class{},Marker:Overlay,Popup:Overlay,addProtocol(){}},
  pmtiles:{Protocol:class{tile(){}}},fetch:async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('data/distribution'+new URL(url).pathname,'utf8'))})});
// App uses selectors including # prefixes.
context.document.querySelector=selector=>get(selector.startsWith('#')?selector.slice(1):selector);
vm.runInContext(fs.readFileSync('web/peak-index.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/peak-quality.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/japanese-names.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/app.js','utf8'),context);
(async()=>{
  await vm.runInContext("map.events.get('load')()",context);
  for(const region of ['sg-singapore','gb-london','is-reykjavik','japan']) {
    get('area').value=region;
    await get('area').listeners.change();
    const state=vm.runInContext('({manifest,stations,places,peakIndex,map})',context);
    assert.equal(Boolean(state.manifest.pilot),region!=='japan');
    assert.equal(Boolean(state.peakIndex),region!=='japan');
    if(region!=='japan') assert.equal(state.manifest.region_id,region);
    assert(get('reference-credit').innerHTML.includes(region==='japan'?'国土数値情報':'OpenStreetMap'));
    const expectedRoot=config.areas[region]?.dataBase || config.dataBase;
    assert(state.map.getSource('density').url.startsWith('pmtiles://'+expectedRoot));
    const tileURL=state.map.getSource('base').tiles[0];
    assert(tileURL.includes(region==='japan'?'cyberjapandata.gsi.go.jp':'tile.openstreetmap.org'));
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
      assert.equal(vm.runInContext('peakName(nameFixture)',context),entry.name);
      context.nameFixture.place_distance_m=100;
      assert.equal(vm.runInContext('peakName(nameFixture)',context),entry.name+'付近');
      context.nameFixture.name_source_ids=['node/unknown'];
      assert.equal(vm.runInContext('peakName(nameFixture)',context),'Original');
    }
    if(region==='is-reykjavik') {
      assert.equal(state.stations.length,0);
      get('station-search').value=state.places[0].name;
      get('search').listeners.click();
      assert(state.map.lastFlyTo);
    }
    assert.equal(get('stats').textContent.includes('失敗'),false);
  }
  console.log('Japan and 3 pilots: all 48 choices x 3 floors, background, exact top20, zero-station city search verified');
})().catch(e=>{console.error(e);process.exitCode=1;});
