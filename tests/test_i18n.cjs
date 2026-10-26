const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2]||require('path').join(__dirname,'../wusel/static');
const sandbox={navigator:{language:'en-GB'},localStorage:{getItem:()=>null},document:{querySelector:()=>null}};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(root+'/i18n.js','utf8'),sandbox);
vm.runInContext(`
for(const [key,value] of Object.entries(CATALOG.en)){
 if(!CATALOG.de[key])throw Error('Missing German: '+key);
 const params=s=>[...s.matchAll(/\\{(\\w+)\\}/g)].map(m=>m[1]).sort().join(',');
 if(params(value)!==params(CATALOG.de[key]))throw Error('Placeholder mismatch: '+key);
}
language='de';
if(t('Hello, {name} ☀️',{name:'Alex'})!=='Hallo, Alex ☀️')throw Error('Interpolation');
if(errorText('Password must be 10–128 characters.')!=='Passwort muss 10–128 Zeichen lang sein.')throw Error('Validation');
if(auditText('Created child account: alex')!=='Konto für Kind erstellt: alex')throw Error('Audit');
`,sandbox);
const source=fs.readFileSync(root+'/app.js','utf8');let count=0;
for(const m of source.matchAll(/\b(?:t|tx)\((["'])([^\n]*?)\1/g)){
 const key=m[2];sandbox.lookupKey=key;
 assert(vm.runInContext('Object.hasOwn(CATALOG.en,lookupKey)',sandbox),'Missing key: '+key);count++;
}
console.log('Catalog and interpolation checks passed; '+count+' direct UI lookups checked.');

// Device region remains independent of the UI language, and wall-clock times do not shift.
vm.runInContext(`
navigator.languages=['en-US'];language='de';
if(locale()!=='en-US')throw Error('Browser region');
if(timeLabel('19:05')!=='7:05 PM')throw Error('US time');
if(!dateLabel('2026-10-25').includes('October 25, 2026'))throw Error('Full US date');
if(dayNames()[0]!=='Monday')throw Error('Full weekday');
navigator.languages=['de-CH'];language='en';
if(timeLabel('19:05')!=='19:05')throw Error('Swiss time');
if(!dateLabel('2026-10-25').includes('25. Oktober 2026'))throw Error('Full Swiss date');
if(dayNames()[0]!=='Montag')throw Error('Full German weekday');
if(!dateTimeLabel('2026-10-25T18:05:00Z','Europe/Zurich').includes('19:05'))throw Error('App timezone');
for(const [value,unit,expected] of [[9.6,'°C','10°C'],[-1.5,'°C','-2°C'],[-0.2,'°C','0°C'],[72.3,'°F','72°F'],[null,'°C','—']]){
 if(temperatureLabel(value,unit)!==expected)throw Error('Whole temperature: '+value);
}
`,sandbox);
console.log('Regional date, time and temperature checks passed.');

vm.runInContext(`
for(const [hour,key] of [[0,'Hello, {name}'],[4,'Hello, {name}'],[5,'Good morning, {name}'],[11,'Good morning, {name}'],[12,'Hello, {name}'],[17,'Hello, {name}'],[18,'Good evening, {name}'],[21,'Good evening, {name}'],[22,'Hello, {name}']]){
 const now=new Date(Date.UTC(2026,0,2,hour-1));
 if(greetingKey('Europe/Zurich',now)!==key)throw Error('Greeting boundary: '+hour);
 for(const lang of ['de','en'])if(!CATALOG[lang][key])throw Error('Missing greeting translation');
}
const summer=new Date('2026-07-01T03:00:00Z');
if(greetingKey('Europe/Zurich',summer)!=='Good morning, {name}')throw Error('Summer timezone');
if(greetingKey('America/New_York',summer)!=='Hello, {name}')throw Error('Configured timezone must control greeting');
language='de';if(t(greetingKey('Europe/Zurich',summer),{name:'Alex'})!=='Guten Morgen, Alex')throw Error('German greeting');
language='en';if(t(greetingKey('Europe/Zurich',summer),{name:'Alex'})!=='Good morning, Alex')throw Error('English greeting');
`,sandbox);
console.log('Greeting boundaries, configured timezone, summer offset and English/German checks passed.');

vm.runInContext(`
language='de';
if(auditText('Reset child account: alex')!=='Kinderkonto zurückgesetzt: alex')throw Error('Reset audit translation');
if(t('Lagoon')!=='Lagune')throw Error('Lagoon translation');
language='en';if(t('Lagoon')!=='Lagoon')throw Error('English Lagoon name');
`,sandbox);
console.log('Child-reset audit and Lagoon naming checks passed.');

vm.runInContext(`
const at=new Date('2026-10-26T11:00:00Z');
if(taskTimingKey('12:01','Europe/Zurich',at)!=='Later today')throw Error('Future step timing');
if(taskTimingKey('12:00','Europe/Zurich',at)!=='Now it’s time')throw Error('Due step timing');
if(taskTimingKey('07:00','Europe/Zurich',at)!=='Still open')throw Error('Earlier step timing');
if(taskTimingKey('11:30','Europe/Zurich',at)!=='Now it’s time')throw Error('30 minute boundary');
if(taskTimingKey('11:29','Europe/Zurich',at)!=='Still open')throw Error('31 minute boundary');
if(taskTimingKey('08:00','America/New_York',at)!=='Later today')throw Error('Step timezone');
`,sandbox);
console.log('Task due/future boundaries and configured timezone passed.');

vm.runInContext(source.slice(source.indexOf('function restRanges('),source.indexOf('function pauseEditor(')),sandbox);
vm.runInContext(`
const dates=Array.from({length:400},(_,i)=>new Date(Date.UTC(2026,0,1+i)).toISOString().slice(0,10));
const ranges=restRanges(dates);
if(ranges.length!==2||ranges[0].end!==dates[365]||ranges[1].start!==dates[366])throw Error('Long rest ranges must remain removable within API limits');
`,sandbox);
console.log('Long rest-range grouping stays within API limits.');

vm.runInContext("function esc(value){return String(value??'');}",sandbox);
vm.runInContext(source.slice(source.indexOf('const taskIcons='),source.indexOf('function scheduleEditor(')),sandbox);
vm.runInContext(`
if(taskIcon({icon:''})!==''||taskIcon({icon:'<script>'})!=='')throw Error('No unknown or empty icon rendering');
if(!taskIcon({icon:'medicine'}).includes('💊')||!taskIcon({icon:'medicine'}).includes('aria-hidden="true"'))throw Error('Medicine icon with preserved accessible text');
language='de';if(!taskIconPicker({icon:'medicine'}).includes('Medikament'))throw Error('German icon label');
language='en';if(!taskIconPicker({icon:'medicine'}).includes('Medicine'))throw Error('English icon label');
`,sandbox);
console.log('Optional task icon rendering and English/German medicine label passed.');
