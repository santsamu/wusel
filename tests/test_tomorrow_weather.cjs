const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'../wusel/static'),source=fs.readFileSync(root+'/app.js','utf8');
const sandbox={assert,navigator:{language:'de-CH'},localStorage:{getItem:()=>null},document:{querySelector:()=>null}};
vm.createContext(sandbox);for(const file of ['icons.js','i18n.js'])vm.runInContext(fs.readFileSync(root+'/'+file,'utf8'),sandbox);
vm.runInContext(`
let instant=Date.parse('2026-10-28T16:59:42Z');const RealDate=Date;Date=class extends RealDate{constructor(...args){super(...(args.length?args:[instant]));}static now(){return instant;}};
let state={user:{id:2,role:'child'},timezone:'Europe/Zurich'},view='today',weatherData=null,delay,callback,requests=0;
const parent=()=>state.user.role==='parent',current=()=>({day_view:'focus'}),loadWeather=()=>requests++;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const setTimeout=(fn,ms)=>{callback=fn;delay=ms;return 1;},clearTimeout=()=>{callback=null;};
const document={hidden:false,querySelector:()=>null};
`,sandbox);
vm.runInContext(source.slice(source.indexOf('function compactWeatherAdvice('),source.indexOf('function render(quiet=')),sandbox);
vm.runInContext(source.slice(source.indexOf('const weatherIcons='),source.indexOf('function weatherSetup(')),sandbox);
vm.runInContext(`
const row=(hour,temperature,condition='cloudy')=>({datetime:'2026-10-29T'+hour+':00:00+01:00',temperature,condition,rain_probability:null});
weatherData={status:'ok',date:'2026-10-28',unit:'°C',current:{condition:'snowy',temperature:-5},hourly:[],daily:null,fetched_at:'2026-10-28T16:50:00Z',tomorrow:{date:'2026-10-29',forecast_status:'hourly',hourly:[row('02',-9,'rainy'),row('07',15),row('12',18),row('17',16)]}};
assert(!weatherSummary().includes('tomorrow-preview'));assert.equal(selectedWeatherDay(),'today');
instant+=18000;assert(isWeatherEvening());assert.equal(selectedWeatherDay(),'tomorrow');
for(const lang of ['en','de']){
 language=lang;const summary=weatherSummary();assert(summary.includes('tomorrow-preview'));assert(summary.includes(t('Today')));assert(summary.includes(t('Prepare for tomorrow')));
 const info=tomorrowInfo(weatherData);assert.equal(info.low,15);assert.equal(info.high,18);assert.equal(info.condition,'cloudy');assert(!info.hints.includes(t('Lay out a warm layer.')));assert(!info.hints.includes(t('Have your raincoat ready.')));
 const html=weatherPanel();assert(html.includes('id="weather-day-today"'));assert(html.includes('id="weather-day-tomorrow"'));assert(html.includes(t('Morning and daytime')));assert(!html.includes('-9°C'));
 weatherData.tomorrow.hourly[1]=row('07',8,'rainy');assert(tomorrowInfo(weatherData).hints.includes(t('Have your raincoat ready.')));assert(tomorrowInfo(weatherData).hints.includes(t('Lay out a warm layer.')));
 weatherData.stale=true;assert(!tomorrowPreview().includes(t('Lay out a warm layer.')));assert(tomorrowWeatherPanel().includes(t('Forecast needs checking with a parent.')));weatherData.stale=false;
 weatherData.tomorrow.hourly[1]=row('07',15);
}
weatherData.tomorrow.forecast_status='daily';weatherData.tomorrow.daily={low:2,high:18,condition:'cloudy'};
assert(!tomorrowInfo(weatherData).hints.includes(t('Lay out a warm layer.')));assert(tomorrowWeatherPanel().includes(t('The daily low can include overnight temperatures.')));
weatherData.tomorrow.daily={low:null,high:null,condition:'unknown'};assert.equal(tomorrowInfo(weatherData).low,null);assert(!tomorrowSummary().includes('0°C'));
weatherData.unit='°F';weatherData.tomorrow.daily={low:30,high:45,condition:'rainy'};assert(tomorrowInfo(weatherData).hints.includes(t('Lay out a warm layer.')));
state.user.role='parent';assert.equal(selectedWeatherDay(),'today');weatherSelection={date:weatherLocalDate(),day:'tomorrow'};assert.equal(selectedWeatherDay(),'tomorrow');
scheduleWeatherDisplay();assert.equal(delay,60000);assert.equal(requests,0);document.hidden=true;scheduleWeatherDisplay();assert.equal(callback,null);document.hidden=false;
instant=Date.parse('2026-10-28T23:00:00Z');assert.equal(weatherLocalDate(),'2026-10-29');assert.equal(nextWeatherDate(),'2026-10-30');assert.equal(selectedWeatherDay(),'today');assert.equal(tomorrowInfo(weatherData),null);assert.equal(weatherForNow().status,'unavailable');
state.user.role='child';assert(!weatherSummary().includes('tomorrow-preview'));
weatherData.tomorrow=null;assert(tomorrowPreview().includes(t('Tomorrow’s forecast is unavailable.')));
for(const [iso,next] of [['2026-03-28T22:00:00Z','2026-03-29'],['2026-10-24T21:00:00Z','2026-10-25']])assert.equal(nextWeatherDate(new Date(iso)),next);
`,sandbox);
console.log('Tomorrow weather: evening/midnight/DST, separate daytime advice, daily fallback, Fahrenheit/nulls, stale/missing data, bilingual selectors and independent timer passed.');
