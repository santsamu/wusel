const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const source=fs.readFileSync(path.join(__dirname,'../wusel/static/app.js'),'utf8');
const sandbox={assert};vm.createContext(sandbox);
vm.runInContext(`
let state={user:{role:'child',id:2},revision:1,today:'2026-10-27',timezone:'Europe/Zurich'};
let liveTimer,liveInFlight=false,liveAgain=false,liveDelay=10000,mutationEpoch=0,activeWrites=0,refreshRequests=0,busy=false,syncKind='idle';
let calls=0,refreshes=0,timerDelay,fail=null,marker={revision:1,day:state.today,timezone:state.timezone},modal=false,refreshFailure=false,expireRefresh=false;
const document={hidden:false,querySelector:()=>modal?{}:null};
const clearTimeout=()=>{},setTimeout=(fn,delay)=>{timerDelay=delay;return 1;};
const liveIdentity=()=>state.user?state.user.role+':'+state.user.id:'';
const api=async()=>{calls++;if(fail)throw fail;return marker;};
const refresh=async()=>{refreshes++;if(refreshFailure)throw new Error('state offline');if(expireRefresh)state.user=null;state.revision=marker.revision;state.today=marker.day;state.timezone=marker.timezone;};
const updateChildGreeting=()=>{},updateTaskTiming=()=>{},updateUndoControls=()=>{},loadWeather=()=>{};
const syncStatus=(kind)=>syncKind=kind;
`,sandbox);
vm.runInContext(source.slice(source.indexOf('function scheduleLive('),source.indexOf('const field =')),sandbox);
(async()=>{
await vm.runInContext(`(async()=>{
for(const role of ['child','parent']){
 state.user.role=role;marker.revision=state.revision;let before=refreshes;
 await checkLiveUpdates();assert.equal(refreshes,before);assert.equal(timerDelay,10000);
 marker.revision++;await checkLiveUpdates();assert.equal(refreshes,before+1);
}
busy=true;let before=calls;await checkLiveUpdates();assert.equal(calls,before);busy=false;
refreshRequests=1;await checkLiveUpdates();assert.equal(calls,before);refreshRequests=0;
document.hidden=true;await checkLiveUpdates();assert.equal(calls,before);document.hidden=false;
modal=true;marker.revision++;before=refreshes;await checkLiveUpdates();assert.equal(refreshes,before);modal=false;
await checkLiveUpdates();assert.equal(refreshes,before+1);
fail=new Error('offline');await checkLiveUpdates();assert.equal(liveDelay,20000);await checkLiveUpdates();assert.equal(liveDelay,30000);
fail=null;await checkLiveUpdates();assert.equal(liveDelay,10000);
liveInFlight=true;before=calls;await checkLiveUpdates();assert.equal(calls,before);liveInFlight=false;
wakeLive();assert.equal(timerDelay,0);
fail=Object.assign(new Error('expired'),{status:401});refreshFailure=true;await checkLiveUpdates();assert.equal(liveDelay,20000);
refreshFailure=false;expireRefresh=true;await checkLiveUpdates();assert.equal(state.user,null);
})()`,sandbox);
// Serialized state refreshes reject a snapshot obtained before a local mutation.
const serial={assert};vm.createContext(serial);
vm.runInContext(`
let state={user:{id:2,role:'child',language:'en'},revision:1},mutationEpoch=0,activeWrites=0,busy=false,refreshRequests=0,refreshChain=Promise.resolve(),liveInFlight=false,liveAgain=false;
let release;const renders=[];let requests=0;
const api=async()=>{requests++;if(requests===1)return await new Promise(resolve=>release=resolve);return {user:{id:2,role:'child',language:'en'},revision:3};};
const syncChildUndo=()=>{},scheduleLive=()=>{},updateChildGreeting=()=>{},updateTaskTiming=()=>{},updateUndoControls=()=>{},loadWeather=()=>{};
const render=()=>renders.push(state.revision);
let language='en';
`,serial);
vm.runInContext(source.slice(source.indexOf('function refresh(quiet='),source.indexOf('function nodeKey(')),serial);
await vm.runInContext(`(async()=>{
 const old=refresh(true);await Promise.resolve();mutationEpoch++;
 const latest=refresh(false);release({user:{id:2,role:'child',language:'en'},revision:2});
 await Promise.all([old,latest]);assert.deepEqual(renders,[3]);assert.equal(state.revision,3);assert.equal(refreshRequests,0);
})()`,serial);
console.log('Both-role 10-second polling, unchanged markers, busy/hidden/modal guards, backoff and serialized stale-state rejection passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
