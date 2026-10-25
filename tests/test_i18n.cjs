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
