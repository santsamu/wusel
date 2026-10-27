const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'../wusel/static');
const sandbox={navigator:{language:'en-GB'},localStorage:{getItem:()=>null},document:{querySelector:()=>null},assert};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(root+'/icons.js','utf8'),sandbox);
vm.runInContext(fs.readFileSync(root+'/i18n.js','utf8'),sandbox);
vm.runInContext(`
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let focusChoice=null;
const state={today:'2026-10-26',timezone:'Europe/Zurich'};
const dayCount=c=>({tasks:c.routines.filter(r=>r.scheduled),done:c.routines.filter(r=>r.scheduled&&r.done).length});
const childHeading=()=>'',restNote=()=>'',undoFeedback=()=>'',weatherSummary=()=>'',childTools=()=>'',taskHelp=()=>'';
const taskIcon=r=>r.icon==='medicine'?'<span aria-hidden="true">medicine</span>':'';
`,sandbox);
const source=fs.readFileSync(root+'/app.js','utf8');
vm.runInContext(source.slice(source.indexOf('function pendingReview('),source.indexOf('function childChecklist(')),sandbox);
vm.runInContext(source.slice(source.indexOf('function parentStepControl('),source.indexOf('function today(')),sandbox);
vm.runInContext(`
const at=new Date('2026-10-26T11:00:00Z'); // Noon in Zurich.
const task=(id,time,extra={})=>({id,time,title:'Step '+id,scheduled:true,done:false,locked:false,...extra});
const c={id:2,name:'Alex',routines:[task(1,'07:00'),task(2,'11:30'),task(3,'12:01')]};
let model=childTaskModel(c,at);
assert.equal(model.next.id,2);assert.deepEqual(model.earlier.map(r=>r.id),[1]);
assert.equal(childTaskModel({...c,routines:[task(1,'07:00'),task(3,'12:01')]},at).next.id,3);
model=childTaskModel({...c,routines:[task(1,'07:00')]},at);assert.equal(model.next,undefined);assert.equal(model.earlier.length,1);
for(const lang of ['en','de']){
 language=lang;let html=childTaskContent(c,at);
 assert(html.includes(t('Now it’s time')));
 assert(html.includes('<details class="earlier-steps">'));assert(!html.includes('<details class="earlier-steps" open'));
 assert(html.includes(t('From earlier · {count} step',{count:1})));
 assert(html.includes('data-action="do-next" data-id="1"'));
 const onlyEarlier=childTaskContent({...c,routines:[task(1,'07:00')]},at);
 assert(onlyEarlier.includes(t('Nothing due right now')));assert(!onlyEarlier.includes('focus-done'));
}
focusChoice={child:2,day:state.today,routine:1};
assert.equal(childTaskModel(c,at).next.id,1);
assert.equal(childTaskModel(c,at).earlier.length,0);
assert.equal(childTaskModel({...c,id:3},at).next.id,2);
focusChoice.day='2026-10-25';assert.equal(childTaskModel(c,at).next.id,2);
focusChoice={child:2,day:state.today,routine:1};
assert.equal(childTaskModel({...c,routines:[task(1,'07:00',{done:true}),task(2,'11:30')]},at).next.id,2);
assert.equal(childTaskModel({...c,routines:[task(1,'07:00',{locked:true}),task(2,'11:30')]},at).next.id,2);
focusChoice=null;
const chronological={...c,routines:[task(1,'11:30'),task(2,'12:15')]};
assert.equal(childTaskModel(chronological,at).next.id,1);
assert.equal(childTaskModel(chronological,new Date('2026-10-26T11:01:00Z')).next.id,2);
assert.notEqual(childTaskModel(chronological,at).signature,childTaskModel(chronological,new Date('2026-10-26T11:01:00Z')).signature);
const deferred={...c,routines:[task(2,'11:45'),task(1,'11:30',{defer_order:1})]};
assert.equal(childTaskModel(deferred,at).next.id,2);
// Saved deferrals must remain outside automatic focus after a page reload clears manual choice.
const deferredCurrent={...c,routines:[task(3,'12:01'),task(2,'11:45',{defer_order:1})]};
focusChoice=null;
assert.equal(childTaskModel(deferredCurrent,at).next.id,3);
assert.deepEqual(childTaskModel(deferredCurrent,at).earlier.map(r=>r.id),[2]);
language='de';assert(childTaskContent(deferredCurrent,at).includes('Für später'));
focusChoice={child:2,day:state.today,routine:2};assert.equal(childTaskModel(deferredCurrent,at).next.id,2);
focusChoice=null;
const onlyDeferred={...c,routines:[task(2,'11:45',{defer_order:1})]};
assert.equal(childTaskModel(onlyDeferred,at).next,undefined);
assert.equal(childTaskModel(onlyDeferred,at).earlier.length,1);

assert(childTaskContent({...c,rest_day:true},at).includes(t('Optional today')));
assert(!childTaskContent({...c,routines:[]},at).includes('earlier-steps'));
assert(!childTaskContent({...c,routines:[task(1,'07:00',{done:true})]},at).includes('earlier-steps'));
`,sandbox);
console.log('Time-aware selection, collapsed earlier steps, explicit choice, expiry, deferral, rest days and live boundaries passed.');
