const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
global.window={};
vm.runInThisContext(fs.readFileSync('web/peak-quality.js','utf8'));
vm.runInThisContext(fs.readFileSync('web/peak-index.js','utf8'));
const feature=(r)=>({type:'Feature',geometry:{type:'Point',coordinates:[...r.coordinates]},properties:{kind:'peak',name_source:'coordinates',name:r.peak,density:r.density}});
const held=window.NIGIWAI_PEAK_QUARANTINE.map(feature);
assert.equal(held.length,13);
const original=JSON.parse(fs.readFileSync('data/name-translation/world/coverage-coordinate-peaks.json','utf8')).items;
for(const heldFeature of held){
  const matches=original.filter(r=>r.properties.name===heldFeature.properties.name&&r.coordinates.every((v,i)=>Math.abs(v-heldFeature.geometry.coordinates[i])<1e-7));
  assert.equal(matches.length,1,'each excluded summit matches one real coverage record');
  const real={geometry:{coordinates:matches[0].coordinates},properties:matches[0].properties};
  assert(!window.nigiwaiPeakAllowed(real,'world'));
}
for(const f of held){
  assert(!window.nigiwaiPeakAllowed(f,'world'));
  assert(window.nigiwaiPeakAllowed(f,'japan'));
  const nearby=structuredClone(f);nearby.geometry.coordinates[0]+=0.0009;
  assert(window.nigiwaiPeakAllowed(nearby,'world')); // adjacent grid summit survives
  const named=structuredClone(f);named.properties.name_source='GeoNames';
  assert(window.nigiwaiPeakAllowed(named,'world'));
}
(async()=>{
  // Fully-contained top-100 summary hides a lower-ranked replacement.
  // Filtering its summary alone would return 99 instead of exact top-100.
  const points=Array.from({length:130},(_,i)=>({geometry:{coordinates:[i/1000,0]},properties:{density:1000-i}}));
  const nodes={0:{bbox:[0,0,1,1],top:points.slice(0,100),children:[1,2]},1:{bbox:[0,0,1,1],features:points.slice(0,65)},2:{bbox:[0,0,1,1],features:points.slice(65)}};
  const index=new window.NigiwaiPeakIndex('https://example.invalid/',{root:0,node_file_template:'{id}.json',summary_limit:100},async url=>nodes[Number(url.match(/(\d+)\.json$/)[1])]);
  const eligible=f=>f.properties.density!==1000;
  for(const limit of [20,100]){
    const actual=await index.query([-1,-1,2,2],800,limit,eligible);
    assert.deepEqual(actual,points.filter(eligible).slice(0,limit));
  }
  console.log('13 exact world exclusions, neighboring/Japan peaks, and replacement top-k verified');
})().catch(e=>{console.error(e);process.exitCode=1;});
