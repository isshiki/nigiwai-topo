// Exercise the actual app resolver against all stored world/Japan peaks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const context=vm.createContext({window:{NIGIWAI_JAPANESE_NAMES:{world:{}}},area:{value:'world'}});
for(const name of ['world-japanese-names','world-name-overrides','world-reviewed-names','world-coordinate-names'])vm.runInContext(fs.readFileSync(`web/${name}.js`,'utf8'),context);
const app=fs.readFileSync('web/app.js','utf8');
vm.runInContext(app.slice(app.indexOf('function peakName('),app.indexOf('const dataRoot')),context);
const resolve=p=>{context.props=p;return vm.runInContext('peakName(props)',context);};
const root='data/distribution/'+(process.env.NIGIWAI_TEST_WORLD_FOLDER||'foursquare-world'),manifest=read(root+'/manifest.json');
let total=0,coordinates=0,coordinates800=0;
for(const package of manifest.packages)for(const f of read(`${root}/${package.id}/200-all-peaks.json`).features){
  total++;const name=resolve(f.properties);assert(name&&typeof name==='string');
  if(/^[\d\s.,°NSEW+\-]+$/.test(name)){coordinates++;if(f.properties.density>=800)coordinates800++;}
}
const japan=read('data/name-translation/world/coverage-japan-english.json').items;
let japanEnglish=0;
for(const r of japan){const name=resolve({name:r.original+'付近',name_source:r.source,name_source_ids:r.source_ids,place_distance_m:0});if(/[A-Za-z]/.test(name))japanEnglish++;}
assert.equal(japanEnglish,0);
context.area.value='japan';const national='data/distribution/foursquare-japan';let domesticCoordinate=0,domestic=0;
for(const d of read(national+'/manifest.json').datasets)for(const f of read(national+'/'+d.peaks_file).features){domestic++;if(/^[\d\s.,°NSEW+\-]+$/.test(resolve(f.properties)))domesticCoordinate++;}
assert.equal(domesticCoordinate,0);
const report={world_peaks:total,world_coordinate_labels_after:coordinates,world_coordinate_labels_floor800_after:coordinates800,japan_english_reference_labels_after:japanEnglish,japan_peak_records:domestic,japan_coordinate_labels_after:domesticCoordinate};
fs.writeFileSync('data/name-translation/world/display-coverage-check.json',JSON.stringify(report,null,2));console.log(report);
