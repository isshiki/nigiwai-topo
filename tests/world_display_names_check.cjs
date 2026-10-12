// Exhaustive audit of the real application resolver on every generated world peak.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({window:{},area:{value:'world'},URL});
for(const name of ['japanese-names','world-japanese-names','world-name-overrides','world-reviewed-names','world-display-names','world-coordinate-names','unnamed-world-peak-names','world-peak-locality-names','world-station-peak-names'])vm.runInContext(fs.readFileSync('web/'+name+'.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/peak-quality.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/world-regions.js','utf8'),context);
vm.runInContext(fs.readFileSync('web/peak-index.js','utf8'),context);
const code=fs.readFileSync('web/app.js','utf8');
vm.runInContext(code.slice(code.indexOf('function applyPeakLocalityNames('),code.indexOf('const dataRoot'))+';this.resolve={applyPeakLocalityNames,peakName,peakGroupKey};',context);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const root=process.env.NIGIWAI_WORLD_ROOT||'data/distribution/foursquare-world-v2',manifest=read(root+'/manifest.json');
const report={peaks:0,forbidden_suffix:0,foreign_named_peaks:0,foreign_high_density:0,coordinate_only:0,coordinate_high_density:0,foreign_references:{},samples:[],regions:{}};
const boxes={taiwan:[118,21.8,122.1,26.4],northAmerica:[-125,15,-60,60],japan:[122,20,154,46],seoul:[126.5,37.1,127.3,37.9]};
const groups=Object.fromEntries(Object.keys(boxes).map(k=>[k,new Map()]));
const registry=process.env.NIGIWAI_VERIFY_ALL_REGIONS?Object.entries(context.window.NIGIWAI_WORLD_REGIONS).map(([id,r])=>({id,bbox:r.bbox,peaks:new Map()})):[];
for(const p of manifest.packages){
 const intersecting=registry.filter(r=>p.bbox[2]>=r.bbox[0]&&p.bbox[0]<=r.bbox[2]&&p.bbox[3]>=r.bbox[1]&&p.bbox[1]<=r.bbox[3]);
 const original=read(root+'/'+p.id+'/200-all-peaks.json').features;
 const translated=context.resolve.applyPeakLocalityNames(original);
 translated.forEach((f,i)=>{
  const name=context.resolve.peakName(f.properties),props=f.properties,xy=f.geometry.coordinates;
  assert.equal(props.density,original[i].properties.density);assert.deepEqual(xy,original[i].geometry.coordinates);
  assert(!original[i].properties.reviewed_peak_locality);
  report.peaks++;
  if(/付近/.test(name))report.forbidden_suffix++;
  const coordinates=props.name_source==='coordinates'&&!context.window.NIGIWAI_COORDINATE_NAMES?.[props.name];
  if(coordinates){report.coordinate_only++;if(props.density>=800)report.coordinate_high_density++;}
  else if(!/[ぁ-ヺ一-鿿]/.test(name)||[...name].some(ch=>/\p{L}/u.test(ch)&&!/[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}ー々]/u.test(ch))){
   report.foreign_named_peaks++;if(props.density>=800)report.foreign_high_density++;
   const key=props.name_source+':'+(props.name_source_ids?.[0]||props.name);report.foreign_references[key]=name;
   if(report.samples.length<20)report.samples.push({name,density:props.density,xy,key});
  }
  for(const [region,[w,s,e,n]]of Object.entries(boxes))if(xy[0]>=w&&xy[0]<=e&&xy[1]>=s&&xy[1]<=n&&props.density>=800){
   const prior=groups[region].get(name);if(!prior||props.density>prior.density)groups[region].set(name,{name,density:props.density,xy});
  }
  if(context.window.nigiwaiPeakAllowed(f,'world')&&props.density>=100)for(const r of intersecting){
   const [w,s,e,n]=r.bbox;if(xy[0]<w||xy[0]>e||xy[1]<s||xy[1]>n)continue;
   const prior=r.peaks.get(name);if(!prior||props.density>prior.density)r.peaks.set(name,{name,density:props.density});
  }
 });
}
for(const [region,g]of Object.entries(groups))report.regions[region]=[...g.values()].sort((a,b)=>b.density-a.density).slice(0,20);
fs.writeFileSync('data/validation/world-display-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,foreign_references:Object.keys(report.foreign_references).length,regions:undefined,samples:undefined}));
if(process.env.NIGIWAI_STRICT_NAMES){assert.equal(report.forbidden_suffix,0);assert.equal(report.foreign_named_peaks,0);assert.equal(report.coordinate_high_density,0);}
if(registry.length)(async()=>{
 const index=new context.window.NigiwaiPeakIndex('https://example.invalid/',read(root+'/'+manifest.datasets[0].peaks_index),async url=>read(root+'/world-peak-index/'+new URL(url).pathname.split('/').at(-1)));
 let checks=0;
 for(const region of registry)for(const floor of [100,800,1600]){
  const actual=await index.query(region.bbox,floor,20,f=>context.window.nigiwaiPeakAllowed(f,'world'),context.resolve.peakGroupKey);
  const expected=[...region.peaks.values()].filter(f=>f.density>=floor).sort((a,b)=>b.density-a.density).slice(0,20);
  assert.deepEqual(Array.from(actual,f=>f.properties.density),expected.map(f=>f.density),region.id+' floor '+floor);
  assert.equal(new Set(actual.map(context.resolve.peakGroupKey)).size,actual.length,region.id);
  checks++;
 }
 report.index_checks=checks;report.checked_regions=registry.length;
 fs.writeFileSync('data/validation/world-display-audit.json',JSON.stringify(report,null,2));
 console.log('Full-data distinct index verified: '+registry.length+' regions x 3 floors = '+checks+' checks');
})().catch(e=>{console.error(e);process.exitCode=1;});
