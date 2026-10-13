// Inventory actual reference coordinates before applying a uniform radius worldwide.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root='data/distribution/foursquare-world-v6';
const out='data/shared-density';fs.mkdirSync(out,{recursive:true});
const context=vm.createContext({window:{},area:{value:'world'},URL});
for(const name of ['japanese-names','world-japanese-names','world-name-overrides','world-reviewed-names','world-display-names','world-coordinate-names','unnamed-world-peak-names','world-peak-locality-names','world-station-peak-names','peak-quality','world-reference-stations'])vm.runInContext(fs.readFileSync(`web/${name}.js`,'utf8'),context);
const app=fs.readFileSync('web/app.js','utf8');
vm.runInContext(app.slice(app.indexOf('function applyPeakLocalityNames('),app.indexOf('const dataRoot'))+';this.resolve={applyPeakLocalityNames,peakName};',context);
const references=new Map();
for(const r of JSON.parse(fs.readFileSync('data/raw/geonames/places.json','utf8')))references.set('GeoNames:'+r.id,r);
if(fs.existsSync(path.join(out,'extra-geonames.json')))for(const r of JSON.parse(fs.readFileSync(path.join(out,'extra-geonames.json'),'utf8')))references.set('GeoNames:'+r.id,r);
for(const r of JSON.parse(fs.readFileSync('docs/held-peak-investigation.json','utf8')).items||[])if(r.reference&&r.source_id)references.set(r.source_id,r.reference);
for(const r of context.window.NIGIWAI_REFERENCE_STATIONS||[]){
 if(r.source==='N02')references.set('国土数値情報 N02:'+r.id,r);
 for(const id of r.osm_ids||[])references.set('OpenStreetMap:'+id,r);
}
for(const folder of fs.readdirSync('data/raw/world-names',{withFileTypes:true}).filter(d=>d.isDirectory())){
 for(const file of ['stations.json','places.json']){
  const name=path.join('data/raw/world-names',folder.name,file);if(!fs.existsSync(name))continue;
  for(const r of JSON.parse(fs.readFileSync(name,'utf8')))for(const id of r.osm_ids||[])references.set('OpenStreetMap:'+id,r);
 }
}
const japanese=JSON.parse(fs.readFileSync('web/station-tier-data.json','utf8')).stations;
const merged=new Map(japanese.flatMap(s=>s.source_station_ids.map(id=>[String(id),s])));
const records=new Map(japanese.map(s=>['station:'+s.id,{id:'station:'+s.id,name:s.id==='003844'?'明治神宮前〈原宿〉':s.name,lon:s.lon,lat:s.lat,source:'国土数値情報 N02',source_ids:s.source_station_ids,station_id:s.id}]));
const unresolved=[],manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
let visible=0;
for(const entry of manifest.packages){
 const raw=JSON.parse(fs.readFileSync(path.join(root,entry.id,'200-all-peaks.json'),'utf8')).features;
 for(const f of context.resolve.applyPeakLocalityNames(raw)){
  const p=f.properties;if(p.density<800||!context.window.nigiwaiPeakAllowed(f,'world'))continue;
  visible++;
  if(p.name_source==='国土数値情報 N02'&&(p.name_source_ids||[]).some(id=>merged.has(String(id))))continue;
  const reviewed=p.reviewed_peak_locality;
  const coordinate=context.window.NIGIWAI_COORDINATE_NAMES?.[p.name];
  const keys=reviewed?.source_id?[reviewed.source_id]:coordinate?.source_id?[coordinate.source_id]:(p.name_source_ids||[]).map(id=>p.name_source+':'+id);
  const key=keys.find(k=>references.has(k)),reference=references.get(key);
  if(!reference){unresolved.push({name:context.resolve.peakName(p),coordinates:f.geometry.coordinates,keys,reviewed:reviewed||null});continue;}
  if(!records.has(key))records.set(key,{id:key,name:context.resolve.peakName(p),lon:reference.lon,lat:reference.lat,source:p.name_source,source_ids:p.name_source_ids});
 }
}
const report={radius_m:800,sigma_m:200,visible_old_peaks:visible,references:records.size,japanese_stations:japanese.length,unresolved_peaks:unresolved.length};
fs.writeFileSync(path.join(out,'references.json'),JSON.stringify({report,records:[...records.values()],unresolved}));
fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
