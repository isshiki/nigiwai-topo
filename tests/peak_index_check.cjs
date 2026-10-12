const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
global.window={};
vm.runInThisContext(fs.readFileSync('web/peak-index.js','utf8'));
const fixture=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let active=0,maxActive=0;
const read=async url=>{
  active++; maxActive=Math.max(maxActive,active);
  await new Promise(resolve=>setTimeout(resolve,1));
  active--;
  return fixture.index.nodes[Number(url.match(/(\d+)\.json$/)[1])];
};
(async()=>{
  const index=new window.NigiwaiPeakIndex('https://example.invalid/',{root:fixture.index.root,node_file_template:'{id}.json',summary_limit:100},read);
  for(const bbox of fixture.boxes) for(const floor of [0,800,1195]) {
    const actual=(await index.query(bbox,floor,20)).map(f=>f.properties.density);
    const expected=fixture.features.filter(f=>{const [x,y]=f.geometry.coordinates;return x>=bbox[0]&&x<=bbox[2]&&y>=bbox[1]&&y<=bbox[3]&&f.properties.density>=floor;})
      .sort((a,b)=>b.properties.density-a.properties.density).slice(0,20).map(f=>f.properties.density);
    assert.deepEqual(actual,expected);
  }
  assert(maxActive<=4);
  const bounds={getWest:()=>170,getEast:()=>190,getSouth:()=>-10,getNorth:()=>10};
  assert.deepEqual(window.nigiwaiViewBoxes(bounds),[[170,-10,180,10],[-180,-10,-170,10]]);
  assert(window.nigiwaiContainsPoint(bounds,[-175,0]));
  assert(!window.nigiwaiContainsPoint(bounds,[0,0]));
  console.log('JS viewport rankings match full scan; date-line split and max 4 requests verified');
})().catch(e=>{console.error(e);process.exitCode=1;});
