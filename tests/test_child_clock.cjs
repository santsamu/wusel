const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'../wusel/static'),source=fs.readFileSync(root+'/app.js','utf8');
const sandbox={assert,navigator:{languages:['de-CH'],language:'de'},localStorage:{getItem:()=>null},document:{querySelector:()=>null}};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(root+'/i18n.js','utf8'),sandbox);
vm.runInContext(`
let instant=Date.parse('2026-10-28T13:35:42.500Z');
const RealDate=Date;Date=class extends RealDate{constructor(...args){super(...(args.length?args:[instant]));}static now(){return instant;}};
let state={user:{role:'child'},timezone:'Europe/Zurich'},delay,callback,cleared=0;
const clock={textContent:'',dateTime:''};
const document={hidden:false,querySelector:()=>clock};
const setTimeout=(fn,ms)=>{callback=fn;delay=ms;return 1;},clearTimeout=()=>{cleared++;callback=null;};
const esc=s=>s;
assert.equal(currentTimeLabel('Europe/Zurich'),'14:35');
navigator.languages=['en-US'];assert.equal(currentTimeLabel('Europe/Zurich'),'2:35 PM');
navigator.languages=['de-CH'];
for(const [iso,expected] of [['2026-03-29T00:59:00Z','1:59'],['2026-03-29T01:00:00Z','3:00'],['2026-10-25T00:59:00Z','2:59'],['2026-10-25T01:00:00Z','2:00'],['2026-10-28T23:00:00Z','0:00']])assert.equal(currentTimeLabel('Europe/Zurich',new Date(iso)),expected);
`,sandbox);
vm.runInContext(source.slice(source.indexOf('let headerClockTimer;'),source.indexOf('function updateChildGreeting(')),sandbox);
vm.runInContext(`
for(const lang of ['en','de']){language=lang;const html=headerClock();assert(html.includes(t('Current time')));assert(html.includes('14:35'));assert(!html.includes('aria-live'));assert(!html.includes('role="status"'));}
scheduleHeaderClock();assert.equal(clock.textContent,'14:35');assert.equal(delay,17500);
instant+=17500;callback();assert.equal(clock.textContent,'14:36');assert.equal(delay,60000);assert.equal(clock.dateTime,'2026-10-28T13:36:00.000Z');
document.hidden=true;scheduleHeaderClock();assert.equal(callback,null);
instant+=5*60000;document.hidden=false;scheduleHeaderClock();assert.equal(clock.textContent,'14:41');
state.timezone='America/New_York';scheduleHeaderClock();assert.equal(clock.textContent,'9:41');
state.user.role='parent';scheduleHeaderClock();assert.equal(clock.textContent,'9:41');assert.equal(delay,60000);instant+=60000;callback();assert.equal(clock.textContent,'9:42');
state.user=null;scheduleHeaderClock();assert.equal(callback,null);
assert(cleared>=7);
`,sandbox);
console.log('Shared header clock: regional formats, configured timezone, DST/midnight, minute alignment, hidden/resume and role lifecycle passed.');
