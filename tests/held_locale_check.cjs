const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const audit=JSON.parse(fs.readFileSync('docs/held-locale-final-review.json','utf8'));
const context=vm.createContext({window:{NIGIWAI_JAPANESE_NAMES:{world:{}}},area:{value:'world'}});
for(const name of ['world-japanese-names','world-name-overrides','world-reviewed-names','world-coordinate-names'])vm.runInContext(fs.readFileSync(`web/${name}.js`,'utf8'),context);
const app=fs.readFileSync('web/app.js','utf8');
vm.runInContext(app.slice(app.indexOf('function originalPeakName('),app.indexOf('const dataRoot')),context);
let adopted=0,held=0,natural=0;
for(const row of audit.items){
  context.props={name:row.original,name_source:'GeoNames',name_source_ids:[row.id.split(':')[1]]};
  const resolved=vm.runInContext('peakName(props)',context);
  if(row.decision==='adopt'){
    adopted++;assert.equal(resolved,row.name,row.id);
    if(row.reference_kind==='natural_landmark'){natural++;assert.match(vm.runInContext('peakBasis(props)',context),/自然地形名/);}
  }else{held++;assert.equal(resolved,row.original,row.id);}
}
assert.equal(adopted,20);assert.equal(held,4);assert.equal(natural,2);
console.log({adopted,held,natural,actual_app_resolver:true});
