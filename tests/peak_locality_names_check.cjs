const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({window:{},area:{value:'world'}});
vm.runInContext(fs.readFileSync('web/world-peak-locality-names.js','utf8'),context);
if(process.env.NIGIWAI_PUBLIC_WORLD)vm.runInContext(fs.readFileSync('web/world-station-peak-names.js','utf8'),context);
const app=fs.readFileSync('web/app.js','utf8');
vm.runInContext(app.slice(app.indexOf('function applyPeakLocalityNames('),app.indexOf('const dataRoot')),context);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const root='data/distribution/foursquare-world-v2';let matches=0;
for(const package of read(root+'/manifest.json').packages){
 const original=read(`${root}/${package.id}/200-all-peaks.json`).features;
 context.features=original;
 const result=vm.runInContext('applyPeakLocalityNames(features)',context);
 for(let i=0;i<result.length;i++){
  assert.deepEqual(result[i].geometry,original[i].geometry);assert.equal(result[i].properties.density,original[i].properties.density);
  assert(!original[i].properties.reviewed_peak_locality,'Must not mutate source');
  if(!result[i].properties.reviewed_peak_locality)continue;
  matches++;context.props=result[i].properties;
  assert.equal(vm.runInContext('peakName(props)',context),result[i].properties.reviewed_peak_locality.name.replace(/駅付近|付近/g,''));
  assert.match(vm.runInContext('peakOriginal(props)',context),/元の名称/);
 }
}
assert.equal(matches,process.env.NIGIWAI_PUBLIC_WORLD?1013:6);
if(process.env.NIGIWAI_PUBLIC_WORLD){
 const [key,p]=Object.entries(context.window.NIGIWAI_STATION_PEAK_NAMES)[0];
 context.features=[{geometry:{coordinates:key.split(',').map(Number)},properties:{name_source:p.original_source,name_source_ids:p.original_source_ids}}];
 assert(vm.runInContext('applyPeakLocalityNames(features)[0].properties.reviewed_peak_locality',context));
 context.features[0].properties.name_source_ids=['different'];
 assert(!vm.runInContext('applyPeakLocalityNames(features)[0].properties.reviewed_peak_locality',context));
}
const entry=context.window.NIGIWAI_PEAK_LOCALITY_NAMES[0];
context.features=[{geometry:{coordinates:[entry.coordinates[0]+0.001,entry.coordinates[1]]},properties:{name_source:'GeoNames',name_source_ids:[entry.source_id.split(':')[1]]}}];
assert(!vm.runInContext('applyPeakLocalityNames(features)[0].properties.reviewed_peak_locality',context));
context.features[0].geometry.coordinates=entry.coordinates;context.features[0].properties.name_source_ids=['different'];
assert(!vm.runInContext('applyPeakLocalityNames(features)[0].properties.reviewed_peak_locality',context));
context.features[0].properties.name_source_ids=[entry.source_id.split(':')[1]];context.area.value='japan';
assert(!vm.runInContext('applyPeakLocalityNames(features)[0].properties.reviewed_peak_locality',context));
console.log(`${matches} actual peaks renamed; coordinates/source guards and original density preserved`);
