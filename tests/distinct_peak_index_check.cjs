const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
global.window={};vm.runInThisContext(fs.readFileSync('web/peak-index.js','utf8'));
const peak=(name,density,x=0)=>({geometry:{coordinates:[x,0]},properties:{name,density}});
// Highest 100 raw peaks all share one name. Lower-ranked cities must survive.
const repeated=Array.from({length:120},(_,i)=>peak('台北市',10000-i));
const other=Array.from({length:30},(_,i)=>peak('別都市'+i,8000-i));
const all=[...repeated,...other];
const nodes=[{bbox:[-1,-1,1,1],top:all.slice(0,100),children:[1,2]},
 {bbox:[-1,-1,1,1],features:repeated}, {bbox:[-1,-1,1,1],features:other}];
(async()=>{
 let reads=0;
 const index=new window.NigiwaiPeakIndex('https://example.invalid/',{root:0,summary_limit:100,node_file_template:'{id}.json'},async u=>{reads++;return nodes[Number(u.match(/(\d+)\.json$/)[1])];});
 const rows=await index.query([-1,-1,1,1],800,20,()=>true,f=>f.properties.name);
 assert.equal(rows.length,20);assert.equal(new Set(rows.map(r=>r.properties.name)).size,20);
 assert.equal(rows[0].properties.name,'台北市');assert.equal(rows[0].properties.density,10000);
 assert.equal(rows[19].properties.name,'別都市18');assert.equal(reads,3);
 assert.equal((await index.query([-1,-1,1,1],9999,20,()=>true,f=>f.properties.name)).length,1);
 assert.equal((await index.query([-1,-1,1,1],800,20)).filter(r=>r.properties.name==='台北市').length,20);
 console.log('Distinct top20 descends through an unsafe repeated-name summary; maximum density retained');
})().catch(e=>{console.error(e);process.exitCode=1;});
