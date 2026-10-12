/* Production shard query over HTTPS using Node HTTP, not browser automation. */
const assert=require('node:assert/strict'),fs=require('node:fs'),https=require('node:https'),vm=require('node:vm');
global.window={};
vm.runInThisContext(fs.readFileSync('web/peak-index.js','utf8'));
vm.runInThisContext(fs.readFileSync('web/config.js','utf8'));
const reports=[];
let bytes=0,requests=0;
function read(url) {
  return new Promise((resolve,reject)=>{
    const request=https.get(url,{headers:{Origin:'https://example.github.io'}},response=>{
      if(response.statusCode!==200) {response.resume();reject(Error(`HTTP ${response.statusCode}`));return;}
      try {assert.equal(response.headers['access-control-allow-origin'],'*');} catch(e) {response.resume();reject(e);return;}
      const chunks=[];
      response.on('data',chunk=>chunks.push(chunk));
      response.on('end',()=>{try {const buffer=Buffer.concat(chunks);bytes+=buffer.length;requests++;resolve(JSON.parse(buffer.toString('utf8')));}catch(e){reject(e);}});
      response.on('error',reject);
    });
    request.setTimeout(30000,()=>request.destroy(Error('HTTPS timeout')));
    request.on('error',reject);
  });
}
(async()=>{
  for(const [id,area] of Object.entries(window.NIGIWAI_CONFIG.areas)) {
    bytes=requests=0;
    const manifest=await read(area.dataBase+'manifest.json');
    const stations=await read(area.dataBase+'stations.json');
    await read(area.dataBase+'places.json');
    const item=manifest.datasets.find(d=>d.sigma===200&&d.category==='all');
    const url=new URL(item.peaks_index,area.dataBase).href;
    const index=new window.NigiwaiPeakIndex(new URL('.',url).href,await read(url),read);
    const full=JSON.parse(fs.readFileSync(`data/distribution/foursquare-${id}/${item.peaks_file}`,'utf8')).features;
    const [x,y]=area.center;
    let initialBytes;
    for(const bbox of [manifest.bbox,[x-.025,y-.025,x+.025,y+.025]]) {
      const result=await index.query(bbox,800,20);
      const expected=full.filter(f=>{const [lon,lat]=f.geometry.coordinates;return lon>=bbox[0]&&lon<=bbox[2]&&lat>=bbox[1]&&lat<=bbox[3]&&f.properties.density>=800;})
        .sort((a,b)=>b.properties.density-a.properties.density).slice(0,20);
      assert.deepEqual(result.map(f=>f.properties.density),expected.map(f=>f.properties.density));
      initialBytes??=bytes;
    }
    reports.push({region:id,stations:stations.length,initial_json_bytes:initialBytes,total_test_json_bytes:bytes,requests});
    console.log(id,'HTTPS shard ranking verified, initial JSON bytes',initialBytes);
  }
  fs.writeFileSync('data/validation/world-https-peaks.json',JSON.stringify(reports,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
