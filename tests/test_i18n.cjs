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
