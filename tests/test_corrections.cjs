const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'../wusel/static');
const sandbox={navigator:{language:'en-GB'},localStorage:{getItem:()=>null},document:{querySelector:()=>null},assert};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(root+'/i18n.js','utf8'),sandbox);
vm.runInContext(`
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const state={today:'2026-10-26',timezone:'Europe/Zurich'};
const dayCount=c=>({tasks:c.routines.filter(r=>r.scheduled),done:c.routines.filter(r=>r.scheduled&&r.done).length});
const childHeading=()=>'',restNote=()=>'',undoFeedback=()=>'',weatherSummary=()=>'',childTools=()=>'',taskHelp=()=>'';
const taskIcon=r=>r.icon==='medicine'?'<span aria-hidden="true">medicine</span>':'';
`,sandbox);
const source=fs.readFileSync(root+'/app.js','utf8');
vm.runInContext(source.slice(source.indexOf('function pendingReview('),source.indexOf('function childChecklist(')),sandbox);
vm.runInContext(source.slice(source.indexOf('function parentStepControl('),source.indexOf('function today(')),sandbox);
vm.runInContext(`
const step={id:1,title:'Medicine <daily>',description:'Take with water <please>',first_action:'Get a glass',time:'07:00',icon:'medicine',locked:true,done:false,scheduled:true};
const child={name:'Alex',routines:[step]};
for(const lang of ['en','de']){
 language=lang;
 let html=childToday(child);
 assert(html.includes('Medicine &lt;daily&gt;'));
 assert(html.includes('Take with water &lt;please&gt;'));
 assert(html.includes('Get a glass')&&html.includes('medicine'));
 assert(html.includes(timeLabel('07:00')));
 assert(html.includes(t('This step is open again. Let’s check it together.')));
 assert(!html.includes('data-action="complete"'));
 child.routines=[step,{...step,id:2,title:'Breakfast',locked:false}];
 html=childToday(child);
 assert(html.includes('Breakfast')&&html.includes('Medicine &lt;daily&gt;'));
 assert(html.includes('data-id="2"')&&!html.includes('data-id="1"'));
 child.routines=[step,{...step,id:3,title:'Brush teeth'}];
 html=childToday(child);assert(html.includes('Brush teeth'));
 child.rest_day=true;assert(childToday(child).includes('Medicine &lt;daily&gt;'));child.rest_day=false;
 assert(parentStepControl({...step,done:true,locked:false}).includes(t('Reopen step')));
 assert(parentStepControl(step).includes(t('Confirm done')));
 assert(!parentStepControl(step).includes('disabled'));
 assert(parentStepControl({...step,locked:false}).includes(t('Mark done')));
 child.routines=[{...step,done:true,locked:false}];
 html=childToday(child);assert(!html.includes('review-pending'));
 child.routines=[step];
}
`,sandbox);
console.log('Child corrected-step details and consistent parent controls passed in English and German.');
