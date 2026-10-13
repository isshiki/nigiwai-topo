// Use the exact map peak density and resolver; never fabricate a score for missing peaks.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root='data/distribution/foursquare-world-v6';
const target='web/station-tier-data.json';
const data=JSON.parse(fs.readFileSync(target,'utf8'));
const owners=new Map();
for(const s of data.stations){for(const id of s.source_station_ids){assert(!owners.has(id));owners.set(id,s);}s.score=null;s.tier=null;s.peak=null;delete s.count;}
const context=vm.createContext({window:{},area:{value:'world'},URL});
for(const name of ['japanese-names','world-japanese-names','world-name-overrides','world-reviewed-names','world-display-names','world-coordinate-names','unnamed-world-peak-names','world-peak-locality-names','world-station-peak-names','peak-quality'])vm.runInContext(fs.readFileSync(`web/${name}.js`,'utf8'),context);
const app=fs.readFileSync('web/app.js','utf8');
vm.runInContext(app.slice(app.indexOf('function applyPeakLocalityNames('),app.indexOf('const dataRoot'))+';this.resolve={applyPeakLocalityNames,peakName};',context);
const manifestFile=path.join(root,'manifest.json'),manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
for(const p of manifest.packages){
 const [w,s,e,n]=p.bbox;if(e<122||w>154||n<20||s>46)continue;
 const raw=JSON.parse(fs.readFileSync(path.join(root,p.id,'200-all-peaks.json'),'utf8')).features;
 for(const f of context.resolve.applyPeakLocalityNames(raw)){
  const q=f.properties;if(q.name_source!=='国土数値情報 N02'||!context.window.nigiwaiPeakAllowed(f,'world'))continue;
  for(const id of q.name_source_ids||[]){const station=owners.get(String(id));if(!station)continue;
   assert(Number.isFinite(q.density)&&q.density>=0);
   if(station.score===null||q.density>station.score){station.score=q.density;station.peak={name:context.resolve.peakName(q),density:q.density,lon:f.geometry.coordinates[0],lat:f.geometry.coordinates[1],reference_station_id:String(id)};}
  }
 }
}
const matched=data.stations.filter(s=>s.score!==null),values=matched.map(s=>s.score).sort((a,b)=>a-b);
function quantile(p){const i=(values.length-1)*p,lower=Math.floor(i),fraction=i-lower;return values[lower]*(1-fraction)+values[Math.ceil(i)]*fraction;}
data.thresholds=Object.fromEntries(['SS','S','A','B','C'].map((t,i)=>[t,quantile([.99,.95,.8,.5,.2][i])]));
for(const s of matched)s.tier=Object.entries(data.thresholds).find(([,cutoff])=>s.score>=cutoff)?.[0]||'D';
for(const key of ['max_distance_m','weight_sigma_m','input_count','excluded_count','assigned_count','outside_count'])delete data[key];
data.metric='map_peak_density';data.unit='件/km²';data.map_build='foursquare-world-v6';data.matched_count=matched.length;data.unmatched_count=data.stations.length-matched.length;data.station_count=data.stations.length;
data.map_manifest_sha256=crypto.createHash('sha256').update(fs.readFileSync(manifestFile)).digest('hex');
fs.writeFileSync(target,JSON.stringify(data)+'\n');
const report={metric:data.metric,matched:data.matched_count,unmatched:data.unmatched_count,thresholds:data.thresholds,tier_counts:Object.fromEntries(['SS','S','A','B','C','D'].map(t=>[t,matched.filter(s=>s.tier===t).length])),above_map_floor:matched.filter(s=>s.score>=800).length};
fs.writeFileSync('data/validation/station-tier-map-density.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

require('node:child_process').execFileSync(process.env.NIGIWAI_PYTHON || 'python', ['scripts/pack_station_tier_data.py'], {stdio:'inherit'});
