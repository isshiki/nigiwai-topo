// Exercise the real renderer against the full station data, without truncation.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync('web/station-tier-data.json','utf8'));
class Element {
 constructor(){this.value='';this.children=[];this.listeners={};this.className='';}
 append(...items){this.children.push(...items);}
 get lastChild(){return this.children.at(-1);}
 replaceChildren(...items){this.children=items;}
 addEventListener(name,fn){this.listeners[name]=fn;}
 setAttribute(name,value){this[name]=value;}
 showModal(){} close(){} querySelectorAll(){return [];}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const context=vm.createContext({console,URLSearchParams,setTimeout,location:{search:'?pref=13'},history:{replaceState(){}},document:{getElementById:get,createElement:()=>new Element()},fetch:async()=>({ok:true,json:async()=>data})});
const cards=()=>get('tier-table').children.flatMap(row=>row.children[1].children[0].children);
(async()=>{
 await vm.runInContext(fs.readFileSync('web/station-tier.js','utf8'),context);
 assert.equal(cards().length,data.stations.filter(s=>s.pref_code==='13').length);
 assert(cards().length>30);
 get('query').value='池袋';get('query').listeners.input();
 assert.equal(cards().length,data.stations.filter(s=>s.pref_code==='13'&&s.name.includes('池袋')).length);
 assert.equal(cards().filter(c=>c.children[1].textContent==='池袋').length,1);
 const ikebukuro=cards().find(c=>c.children[1].textContent==='池袋');
 assert.equal(ikebukuro.children[0].src,'train-icon.svg');
 assert.equal(ikebukuro.children[3].textContent,'15,952 件/km²');
 ikebukuro.listeners.click();
 assert(!get('detail-content').children.some(c=>String(c.textContent).includes('上位Tier')));
 assert(!get('detail-content').children.some(c=>String(c.textContent).includes('SSの基準未満')));
 get('line').value='副都心線';get('line').listeners.input();
 assert.equal(cards().length,1);
 assert.match(cards()[0]['aria-label'],/池袋/);
 get('query').value='';get('query').listeners.input();
 assert.equal(cards().length,data.stations.filter(s=>s.pref_code==='13'&&s.lines.some(l=>l.id.includes('副都心線'))).length);
 get('line').value='';get('prefecture').value='';get('prefecture').listeners.change();
 assert.equal(cards().length,data.stations.length);
 const asakusa=cards().filter(c=>c.children[1].textContent==='浅草');
 assert.equal(asakusa.length,2);
 assert(asakusa.every(c=>c.children.some(n=>n.className==='card-route')));
 assert.notEqual(asakusa[0].children.at(-1).textContent,asakusa[1].children.at(-1).textContent);
 for(const row of get('tier-table').children)assert.equal(row.children[1].children.length,1,'No load-more button');
 const unmatched=cards().filter(c=>c.children[3].textContent==='未判定');assert.equal(unmatched.length,data.unmatched_count);
 get('query').value='原宿';get('query').listeners.input();
 assert(cards().some(c=>c.children[1].textContent==='明治神宮前〈原宿〉'));
 assert(cards().some(c=>c.children[1].textContent==='原宿'));
 vm.runInContext("showTierInfo('SS')",context);
 assert(get('detail-content').children.some(c=>String(c.textContent).includes('上位約1%')));
 assert(get('detail-content').children.some(c=>String(c.textContent).includes('5,406')));
 console.log('All nationwide cards rendered; Tokyo, Ikebukuro, partial route search, and no truncation PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
