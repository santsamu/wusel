const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'../wusel/static');
const sandbox={assert,navigator:{language:'en-GB'},localStorage:{getItem:()=>null},document:{querySelector:()=>null}};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(root+'/icons.js','utf8'),sandbox);vm.runInContext(fs.readFileSync(root+'/i18n.js','utf8'),sandbox);
const source=fs.readFileSync(root+'/app.js','utf8');
vm.runInContext(`const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));`,sandbox);
vm.runInContext(source.slice(source.indexOf('const taskIcons='),source.indexOf('function scheduleEditor(')),sandbox);
vm.runInContext(source.slice(source.indexOf('const weatherIcons='),source.indexOf('function weatherAdvice(')),sandbox);
vm.runInContext(`
for(const [id] of taskIcons){const html=taskIcon({icon:id});assert(html.includes('data-icon="'+id+'"'));assert(html.includes('aria-hidden="true"'));}
assert.equal(taskIcon({icon:'<script>'}),'');
assert(svgIcon('<img src=x onerror=alert(1)>').includes('data-icon="help"'));assert(!svgIcon('<script>').includes('<script>'));
for(const id of Object.values(weatherIcons))assert(Object.hasOwn(WUSEL_ICONS,id));
assert(weatherIcon('not-a-condition').includes('data-icon="thermometer"'));
for(const lang of ['en','de'])for(const [id,,label] of taskIcons){language=lang;const picker=taskIconPicker({icon:id});assert.equal((picker.match(/type="radio"/g)||[]).length,22);assert(picker.includes('value="'+id+'" checked'));assert(picker.includes(t(label)));assert(picker.includes(t('No icon')));assert(picker.includes('<svg'));}
`,sandbox);
assert(!/[\p{Extended_Pictographic}]/u.test(source),'UI must render vectors, not OS emoji');
console.log('SVG task/badge registry, safe fallback, all weather mappings and accessible bilingual picker passed.');
