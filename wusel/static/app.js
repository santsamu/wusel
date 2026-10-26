'use strict';
let state, view = 'today', selected, editing = null, busy = false;
const app = document.querySelector('#app');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const parent = () => state.user?.role === 'parent';
const current = () => state.children?.find(c => c.id === selected) || state.children?.[0];
let noticeTimer;
function notify(message,duration=6500) { document.querySelector('#notice').classList.remove('level-up'); clearTimeout(noticeTimer); document.querySelector('#notice').textContent = message; noticeTimer=setTimeout(()=>document.querySelector('#notice').textContent='',duration); }
let syncKind='idle',syncKey='',syncTimer,undoTimer,lastCompletion=null;
function paintSyncStatus(){
 let box=document.querySelector('#sync-status');
 if(!box){box=document.createElement('div');box.id='sync-status';box.setAttribute('role','status');box.setAttribute('aria-live','polite');document.body.append(box);}
 box.hidden=syncKind==='idle';box.dataset.status=syncKind;
 box.innerHTML=syncKind==='idle'?'':`<span>${tx(syncKey)}</span>${syncKind==='review'?`<button type="button" data-dismiss-sync>${tx('OK')}</button>`:''}${['offline','uncertain'].includes(syncKind)?`<button type="button" data-reconnect>${tx('Check connection')}</button>`:''}`;
}
function syncStatus(kind,key=''){
 clearTimeout(syncTimer);syncKind=kind;syncKey=key;paintSyncStatus();
 if(kind==='saved')syncTimer=setTimeout(()=>syncStatus('idle'),4000);
}
async function api(path,body,track=true){
 const tracked=track&&path!=='weather',writing=body!==undefined;
 if(tracked&&writing)syncStatus('saving','Saving…');
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),12000);
 let response,data;
 try{
  response=await fetch('api/'+path,{...(writing?{method:'POST',headers:{'Content-Type':'application/json','X-Garden-Request':'1','X-CSRF-Token':state?.csrf||''},body:JSON.stringify(body)}:{cache:'no-store'}),signal:controller.signal});
  data=await response.json();
 }catch{
  if(tracked)syncStatus(writing?'uncertain':'offline',writing?'Save status unknown. Check your connection.':'Connection lost. Your list may be out of date.');
  throw new Error(t(writing?'Could not confirm the save. Check the connection before trying again.':'Connection lost. Your list may be out of date.'));
 }finally{clearTimeout(timeout);}
 if(!response.ok){if(tracked&&writing)syncStatus('error','Not saved.');throw new Error(errorText(data.error||'Could not save. Please try again.'));}
 if(tracked&&writing)syncStatus('saved','Saved.');
 else if(path==='state'&&syncKind==='uncertain')syncStatus('review','Connected again. Please check your last change.');
 else if(path==='state'&&syncKind==='offline')syncStatus('saved','Connected again.');
 return data;
}
function clearUndo(){clearTimeout(undoTimer);lastCompletion=null;document.querySelector('.completion-feedback')?.remove();}
function rememberCompletion(r){
 clearUndo();lastCompletion={routine:r.id,title:r.title,child:state.user.id,day:state.today};
 function expire(){const feedback=document.querySelector('.completion-feedback');if(feedback?.contains(document.activeElement)){undoTimer=setTimeout(expire,5000);return;}clearUndo();}
 undoTimer=setTimeout(expire,15000);
}
function undoFeedback(){
 if(!lastCompletion||lastCompletion.child!==state.user?.id||lastCompletion.day!==state.today)return '';
 return `<div class="completion-feedback" role="status"><span>${tx('Completed: {task}',{task:lastCompletion.title})}</span><button data-action="undo-last">${tx('Undo')}</button></div>`;
}
function restNote(c){return c.rest_day?`<p class="rest-note">${tx('Today is a rest day. Your series is safe; steps are optional.')}</p>`:'';}
async function refresh(quiet=false) { const fresh=await api('state'); if(quiet && JSON.stringify(fresh)===JSON.stringify(state)){updateChildGreeting();updateTaskTiming();loadWeather();return;} state=fresh; if(state.user && !state.user.language){try{await api('preferences',{language},false);}catch{}state.user.language=language;} if(state.user?.language) language=state.user.language; if (!state.user) {clearUndo();view='today'; selected=null;weatherData=null;weatherFetched=0;} render(); if(state.user)loadWeather(); }
const field = (label,name,type='text',extra='') => `<label>${esc(t(label))}<input name="${name}" type="${type}" ${extra} required></label>`;
function auth() {
  const setup = state.needs_setup;
  return `<main class="auth">${languagePicker()}<a class="brand" href="./"><span class="brand-icon">🌱</span> <span class="brand-name">Wusel<small>${tx('by Wild & Weich')}</small></span></a>
    <div class="auth-grid"><section class="welcome"><p class="eyebrow">${tx("SMALL STEPS. BRIGHTER DAYS.")}</p><h1>${tx("A little structure.")}<br>${tx("A lot of growing.")}</h1><p>${tx("A calm place for your family's daily routines. One small step at a time.")}</p><div class="garden-art" aria-hidden="true">🌱 <span>🌷</span> 🌿</div><p class="muted">${tx("Your family. Your pace. Your garden.")}</p></section>
    <section class="panel login"><p class="eyebrow">${setup?t("LET’S GET GROWING"):t("WELCOME BACK")}</p><h2>${setup?t("Create your parent account"):t("Sign in to your garden")}</h2><p>${setup?t("Find the setup code in the Home Assistant app logs."):t("Parents and children each use their own account.")}</p>
    <form data-form="${setup?'setup':'login'}">${setup?field(t("Setup code"),'code','text','autocomplete="off"')+field(t("Your name"),'name','text','maxlength="50" autocomplete="name"'):''}
    ${field(t("Username"),'username','text','minlength="3" maxlength="40" autocomplete="username" autocapitalize="none" spellcheck="false"')}
    ${field(t("Password"),'password','password',`minlength="4" maxlength="128" autocomplete="${setup?'new-password':'current-password'}"`)}
    <button class="primary full" type="submit">${setup?t("Create my garden"):t("Sign in")} <span aria-hidden="true">→</span></button></form>
    <p class="small muted">${setup?t("Passwords need at least 4 characters."):t("Forgot a child’s password? A parent can reset it in Family.")}</p></section></div></main>`;
}
function progress(c) {
  const p=c.progress;
  return `<section class="growth panel"><div class="grow-icon" aria-hidden="true">🌿</div><div><p class="eyebrow">${tx("YOUR GARDEN IS GROWING")}</p><h3>${tx("Level {level} · Little steps add up",{level:p.level})}</h3><progress max="100" value="${p.level_progress}" aria-label="${tx("Progress to next level")}"></progress><p class="small muted">${tx("{xp} points earned · {remaining} to level {level}",{xp:p.xp,remaining:100-p.level_progress,level:p.level+1})}</p></div><span class="pill">${tx(p.count===1?"{count} step taken":"{count} steps taken",{count:p.count})}</span></section>`;
}
function today(c) {
  const tasks=c.routines.filter(r=>r.scheduled), done=tasks.filter(r=>r.done).length, next=tasks.find(r=>!r.done&&!r.locked);
  return `<div class="heading"><div><p class="eyebrow">${esc(dateLabel(state.today))}</p><h1>${tx(parent()?"{name}’s day":"Hello, {name} ☀️",{name:c.name})}</h1><p>${tx("One thing at a time. You’ve got this.")}</p></div><div class="daily-count"><strong>${done}<span> / ${tasks.length}</span></strong><span>${tx("steps completed")}</span></div></div>
  ${restNote(c)}${parentWeather()}
  <section class="today-layout"><div><div class="section-heading"><h2>${tx("Today’s little steps")}</h2><span class="muted small">${tx("10 points per step")}</span></div>
  ${tasks.length?tasks.map(r=>`<article class="task ${r.done?'done':''} ${next?.id===r.id?'next':''}"><div class="task-time">${esc(timeLabel(r.time))}${next?.id===r.id?`<span class="next-label">${tx("UP NEXT")}</span>`:''}</div><div class="task-content"><h3>${taskIcon(r)}${esc(r.title)}</h3>${r.description?`<p>${esc(r.description)}</p>`:''}${r.locked?`<p class="small">${tx("This step is open again. Let’s check it together.")}</p>`:''}</div><button class="check" data-action="complete" data-id="${r.id}" aria-pressed="${r.done}" aria-label="${r.done?t("Undo"):t("Complete")} ${esc(r.title)}" ${r.locked?'disabled':''}>${r.done?'✓':`<span aria-hidden="true">○</span>`}</button></article>`).join(''):`<div class="panel empty"><span aria-hidden="true">☁️</span><h3>${tx("A little breathing room")}</h3><p>${parent()?t("Add a routine in Weekly plan to get started."):t("No steps planned for today. Enjoy your day!")}</p></div>`}
  ${tasks.length&&done===tasks.length?`<div class="celebrate" role="status">${tx("🌻 All your steps are done. Look at you grow!")}</div>`:''}</div>
  <aside class="panel encouragement"><span class="sun" aria-hidden="true">☀️</span><p class="eyebrow">${tx("A LITTLE REMINDER")}</p><h2>${tx("Progress grows")}<br>${tx("one step at a time.")}</h2><p>${tx("You don’t have to do everything at once. Just start with your next little step.")}</p><div class="divider"></div><p class="small muted">${tx("Every new day is a fresh start.")}</p></aside></section>${progress(c)}`;
}
function scheduleLabel(r) {return r.specific_date?dateLabel(r.specific_date):r.days.map(d=>dayNames()[d]).join(' · ');}
function changeTiming(defaultValue='tomorrow'){
 return `<label>${tx('Apply changes')}<select name="apply_from" required><option value="today" ${defaultValue==='today'?'selected':''}>${tx('Apply today')}</option><option value="tomorrow" ${defaultValue==='tomorrow'?'selected':''}>${tx('From tomorrow')}</option></select></label><p class="small muted">${tx('Applying today also changes today’s full-day target. Previously earned badges are kept.')}</p>`;
}
const taskIcons=[['tooth','🪥','Teeth'],['clothes','👕','Clothes'],['food','🍽️','Meal'],['bag','🎒','Schoolbag'],['book','📖','Reading'],['bed','🛏️','Bedtime'],['wash','🚿','Washing'],['water','💧','Water'],['shoes','👟','Shoes'],['play','🧸','Play'],['tidy','🧹','Tidying'],['quiet','🧘','Quiet time'],['medicine','💊','Medicine']];
function taskIcon(r,small=false){const icon=taskIcons.find(([id])=>id===r.icon);return icon?`<span class="task-icon ${small?'task-icon-small':''}" aria-hidden="true">${icon[1]}</span>`:'';}
function taskIconPicker(r){return `<label>${tx('Task icon (optional)')}<select name="icon"><option value="" ${!r.icon?'selected':''}>${tx('No icon')}</option>${taskIcons.map(([id,icon,label])=>`<option value="${id}" ${r.icon===id?'selected':''}>${icon} ${esc(t(label))}</option>`).join('')}</select></label>`;}
function scheduleEditor(c) {
 const r=editing || {title:'',description:'',time:'07:00',days:[0,1,2,3,4],specific_date:''};
 return `<details class="panel editor" ${editing?'open':''}><summary>${editing?t("Edit routine"):t("＋ Add a little step")}</summary><form data-form="routine">
 <input type="hidden" name="id" value="${editing?.id || ''}"><div class="form-grid">${field(t("What is the step?"),'title','text',`maxlength="100" placeholder="${tx('For example: Put your lunchbox in your bag')}" value="${esc(r.title)}"`)}${field(t("Time"),'time','time',`value="${esc(r.time)}"`)}</div>
 <p class="small muted">${tx('Use one short, concrete action, such as “Put your lunchbox in your bag” instead of “Get ready”. Doing a step with help still counts.')}</p>${taskIconPicker(r)}<label>${tx('First small action (optional)')}<input name="first_action" maxlength="160" value="${esc(r.first_action||'')}"></label><label>${tx("A little guidance (optional)")}<textarea name="description" maxlength="500" rows="2">${esc(r.description)}</textarea></label>
 <fieldset><legend>${tx("Repeat on these days")}</legend><div class="presets"><button type="button" class="text-button" data-action="preset" data-days="0,1,2,3,4">${tx("Weekdays")}</button><button type="button" class="text-button" data-action="preset" data-days="5,6">${tx("Weekend")}</button><button type="button" class="text-button" data-action="preset" data-days="0,1,2,3,4,5,6">${tx("Every day")}</button></div><div class="day-picks">${dayNames().map((d,i)=>`<label><input name="days" type="checkbox" value="${i}" ${r.days.includes(i)?'checked':''}><span>${d}</span></label>`).join('')}</div></fieldset>
 <label>${tx("Or, on one specific date (optional)")}<input type="date" name="specific_date" value="${esc(r.specific_date)}"></label><p class="small muted">${tx("A specific date takes priority over the weekday selection. Make a separate routine for a different weekend time.")}</p>
 ${changeTiming(editing?'tomorrow':'today')}<div class="actions"><button class="primary" type="submit">${editing?t("Save changes"):t("Add step")}</button>${editing?`<button type="button" data-action="cancel-edit">${tx("Cancel")}</button>`:''}</div></form></details>`;
}
function restRanges(days){
 const ranges=[];for(const day of days||[]){const last=ranges.at(-1),next=last?new Date(last.end+'T12:00:00Z'):null;if(next)next.setUTCDate(next.getUTCDate()+1);if(last&&next.toISOString().slice(0,10)===day&&(new Date(day+'T12:00:00Z')-new Date(last.start+'T12:00:00Z'))/86400000<366)last.end=day;else ranges.push({start:day,end:day});}return ranges;
}
function pauseEditor(c){return `<details class="panel pause-editor"><summary>${tx('Manage rest days')}</summary><p class="small muted">${tx('Rest days do not add to or break a series. Steps remain optional. Past rest days cannot be changed.')}</p><form data-form="rest-days"><input type="hidden" name="child" value="${c.id}"><div class="form-grid">${field(t('From'),'start','date',`min="${state.today}" value="${state.today}"`)}${field(t('Until'),'end','date',`min="${state.today}" value="${state.today}"`)}</div><button class="primary" type="submit">${tx('Plan rest days')}</button></form>${restRanges(c.rest_days).map(r=>`<div class="rest-range"><span>${esc(dateLabel(r.start))}${r.end!==r.start?' – '+esc(dateLabel(r.end)):''}</span><button data-action="remove-rest" data-start="${r.start}" data-end="${r.end}">${tx('Remove')}</button></div>`).join('')}</details>`;}
function planner(c) {
  const planned=[...(c.planned_routines||c.routines)].sort((a,b)=>a.time.localeCompare(b.time)||a.id-b.id);
  const monday=new Date(state.today+'T12:00:00Z');
  monday.setUTCDate(monday.getUTCDate()-(monday.getUTCDay()+6)%7);
  const dates=Array.from({length:7},(_,i)=>{const d=new Date(monday);d.setUTCDate(d.getUTCDate()+i);return d.toISOString().slice(0,10);});
  return `<div class="heading"><div><p class="eyebrow">${tx("MAKE ROOM FOR GOOD HABITS")}</p><h1>${tx("Weekly plan")}</h1><p>${tx("{name}’s rhythm, with room for different days.",{name:c.name})}</p></div></div>
  ${parent()?scheduleEditor(c)+pauseEditor(c):''}<section class="week-grid">${dates.map(d=>{let weekday=(new Date(d+'T12:00:00Z').getUTCDay()+6)%7;let rs=c.routines.map(r=>{const future=planned.find(p=>p.id===r.id);return future?.effective_on&&d>=future.effective_on?future:r;}).filter(r=>!r.archived&&(!r.starts_on||d>=r.starts_on)&&(r.specific_date?r.specific_date===d:r.days.includes(weekday))).sort((a,b)=>a.time.localeCompare(b.time)||a.id-b.id); return `<div class="day-column ${d===state.today?'is-today':''}"><h3>${dayNames()[weekday]} <span>${d.slice(8)}</span></h3>${c.rest_days?.includes(d)?`<p class="rest-label">${tx('Rest day')}</p>`:''}${rs.length?rs.map(r=>`<div class="week-task"><time>${esc(timeLabel(r.time))}</time><strong>${taskIcon(r,true)}${esc(r.title)}</strong></div>`).join(''):`<p class="small muted">${tx("A clear day")}</p>`}</div>`;}).join('')}</section>
  ${parent()?`<div class="section-heading"><h2>${tx("All planned steps")}</h2></div><div class="panel routine-list">${planned.length?planned.map(r=>`<article><div><h3>${esc(timeLabel(r.time))} · ${taskIcon(r,true)}${esc(r.title)}</h3><p class="small muted">${esc(scheduleLabel(r))}</p>${r.effective_on?`<p class="small pending-change">${tx(r.archived?'Archived from {date}':'Changes from {date}',{date:dateLabel(r.effective_on)})}</p>`:''}</div><div class="actions"><button data-action="edit" data-id="${r.id}">${tx("Edit")}</button><button class="text-button danger" data-action="archive" data-id="${r.id}">${tx("Archive")}</button></div></article>`).join(''):`<p>${tx("No routines yet. Add the first step above.")}</p>`}</div>`:''}`;
}
function badgeCard(b,{goal=false}={}){
 const value=Math.min(b.threshold,b.value||0);
 const requirement=b.kind==='streak'?'{count} full days in a row':b.kind==='days'?(b.threshold===1?'{count} fully completed day':'{count} fully completed days'):(b.threshold===1?'{count} completed step':'{count} completed steps');
 return `<article class="panel badge ${b.earned&&!b.revoked?'earned':'unearned'} ${goal?'next-badge':''}"><span class="badge-icon" aria-hidden="true">${b.icon}</span><h3>${esc(t(b.name))}</h3><p>${tx(requirement,{count:b.threshold})}</p>${goal?`<progress max="${b.threshold}" value="${value}" aria-label="${tx('Badge progress')}"></progress><p class="badge-count">${tx('{value} of {total}',{value,total:b.threshold})}</p>`:`<div class="badge-state">${b.earned?(b.revoked?`<span class="pill">${tx(parent()?'Removed by a parent':'Not currently awarded')}</span>`:`<details class="badge-date"><summary>${tx('Earned')}</summary><time datetime="${esc(b.earned)}">${esc(dateLabel(b.earned))}</time></details>`):`<span class="pill">${tx('Still growing')}</span>`}</div>`}${parent()&&b.earned?`<button class="text-button ${b.revoked?'':'danger'}" data-action="badge" data-id="${b.id}" data-revoked="${!b.revoked}">${b.revoked?t('Restore badge'):t('Remove badge')}</button>`:''}</article>`;
}
function rewards(c) {
 const badges=c.progress.badges.filter(b=>parent()||c.show_series!==false||b.kind!=='streak'),earned=badges.filter(b=>b.earned&&!b.revoked);
 const next=badges.find(b=>b.id===c.progress.next_badge&&!b.earned)||badges.filter(b=>!b.earned).sort((a,b)=>(b.value||0)/b.threshold-(a.value||0)/a.threshold)[0];
 const groups=[['steps','Steps'],['days','Full days'],['streak','Series']];
 return `<div class="heading"><div><p class="eyebrow">${tx('CELEBRATE THE LITTLE WINS')}</p><h1>${tx(parent()?'{name}’s badges':'My badges',{name:c.name})}</h1><p>${tx('Something to be proud of, at your own pace.')}</p></div></div>${next?`<section class="badge-goal"><h2>${tx('Your next badge')}</h2>${badgeCard(next,{goal:true})}</section>`:''}<section class="earned-badges"><h2>${tx('Earned badges')}</h2>${earned.length?`<div class="badge-grid">${earned.map(b=>badgeCard(b)).join('')}</div>`:`<p class="muted">${tx('Your first badge is waiting. One little step at a time.')}</p>`}</section><details class="badge-collection"><summary>${tx('See all badges')}</summary><p class="small muted">${tx('A full day means every planned step is done. Planned rest days pause your series. Earned badges stay yours.')}</p>${groups.filter(([kind])=>parent()||c.show_series!==false||kind!=='streak').map(([kind,label])=>`<section><h2>${esc(t(label))}</h2><div class="badge-grid">${badges.filter(b=>(b.kind||'steps')===kind).map(b=>badgeCard(b)).join('')}</div></section>`).join('')}</details>`;
}

function review(c) {
 return `<div class="heading"><div><p class="eyebrow">${tx("A HELPING HAND")}</p><h1>${tx("Review progress")}</h1><p>${tx("{name}’s latest 100 steps. Corrections update points and levels.",{name:c.name})}</p></div></div><p class="muted">${tx("Badges celebrate milestones already reached. Remove a badge separately in Badges if needed.")}</p><div class="panel history">${c.history.length?c.history.map(h=>`<article><div><h3>${esc(h.title)}</h3><p class="small muted">${esc(dateLabel(h.day))} · ${h.voided?(h.locked?t("Reopened for review"):t("Undone")):t("+10 points")}</p></div><button data-action="correct" data-id="${h.id}" data-restore="${!!h.voided}">${h.voided?t("Restore"):t("Reopen step")}</button></article>`).join(''):`<p>${tx("Completed steps will appear here.")}</p>`}</div>`;
}
function family() {
 const accounts=[...state.parents.map(p=>({...p,role:'parent'})),...state.children.map(c=>({...c,role:'child'}))];
 return `<div class="heading"><div><p class="eyebrow">${tx("YOUR LITTLE TEAM")}</p><h1>${tx("Family")}</h1><p>${tx("All parents in this garden can manage every child.")}</p></div></div><div class="family-grid"><section class="panel"><h2>${tx("Add an account")}</h2><form data-form="account"><label>${tx("Account type")}<select name="role"><option value="child">${tx("Child")}</option><option value="parent">${tx("Parent")}</option></select></label>${field(t("Name"),'name','text','maxlength="50"')}${field(t("Username"),'username','text','minlength="3" maxlength="40" autocapitalize="none" autocomplete="off"')}${field(t("Password"),'password','password','minlength="4" maxlength="128" autocomplete="new-password"')}<p class="small muted">${tx("Passwords need at least 4 characters.")}</p><button class="primary">${tx("Create account")}</button></form></section>
 <section class="panel"><h2>${tx("Your family")}</h2>${accounts.map(a=>`<div class="account"><span class="avatar" aria-hidden="true">${a.role==='parent'?'🌳':'🌱'}</span><div><strong>${esc(a.name)}</strong><p class="small muted">${esc(a.username)} · ${tx(a.role==='parent'?'Parent':'Child')}</p></div>${a.role==='child'?`<button class="text-button danger reset-child-button" data-action="reset-child" data-id="${a.id}" aria-label="${tx('Reset {name}’s account',{name:a.name})}">${tx('Reset progress')}</button>`:''}</div>`).join('')}<details><summary>${tx("Reset a password")}</summary><form data-form="password"><label>${tx("Account")}<select name="user">${accounts.map(a=>`<option value="${a.id}">${esc(a.name)} (${tx(a.role==='parent'?'Parent':'Child')})</option>`).join('')}</select></label>${field(t("New password"),'password','password','minlength="4" maxlength="128" autocomplete="new-password"')}<label>${tx("Your current parent password (for parent resets)")}<input type="password" name="current_password" autocomplete="current-password"></label><button>${tx("Reset password")}</button></form></details></section></div>
 ${childViewSettings()}${weatherSetup()}<details class="panel audit"><summary>${tx("Recent parent activity")}</summary>${state.audit.map(a=>`<p class="small"><strong>${esc(a.actor_name)}</strong> · ${esc(auditText(a.detail))}<br><span class="muted">${esc(dateTimeLabel(a.at,state.timezone))}</span></p>`).join('')}</details>`;
}
function dayCount(c){const tasks=c.routines.filter(r=>r.scheduled);return {tasks,done:tasks.filter(r=>r.done).length};}
function childLevel(c){const p=c.progress;return `<div class="child-level"><span>${tx('Level {level}',{level:p.level})}</span><progress id="child-level-progress" max="100" value="${p.level_progress}" aria-label="${tx('Progress to next level')}" aria-valuetext="${tx('Level {level}: {points} of 100 points',{level:p.level,points:p.level_progress})}"></progress><span id="point-feedback" role="status" aria-live="polite"></span></div>`;}
function showPoints(points){const feedback=document.querySelector('#point-feedback');if(feedback)feedback.innerHTML=`<span class="point-gain" aria-hidden="true">+${esc(points)}</span><span class="sr-only">${tx('{points} points earned',{points})}</span>`;}
function animateLevel(before,after){
 const bar=document.querySelector('#child-level-progress');if(!bar)return;
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){bar.value=after.level_progress;return;}
 const crossed=after.level>before.level;
 const start=performance.now(),duration=crossed?650:450;
 function frame(now){
  if(!bar.isConnected)return;
  const elapsed=Math.min(1,(now-start)/duration);
  if(crossed){bar.value=elapsed<.6?before.level_progress+(100-before.level_progress)*(elapsed/.6):after.level_progress*((elapsed-.6)/.4);}
  else bar.value=before.level_progress+(after.level_progress-before.level_progress)*(1-Math.pow(1-elapsed,3));
  if(elapsed<1)requestAnimationFrame(frame);else bar.value=after.level_progress;
 }
 bar.value=before.level_progress;requestAnimationFrame(frame);
}
function celebrateLevel(level,badge){
 const message=t('Level {level} reached!',{level})+(badge?' · '+t(badge.name):'');
 notify(message,2400);document.querySelector('#notice').classList.add('level-up');
 const levelBar=document.querySelector('.child-level');if(levelBar){levelBar.classList.add('level-celebrating');setTimeout(()=>levelBar.classList.remove('level-celebrating'),1200);}
}
function updateChildGreeting(now=new Date()){
 const heading=document.querySelector('[data-child-greeting]');
 if(heading&&current())heading.textContent=t(greetingKey(state.timezone,now),{name:current().name});
}
function updateTaskTiming(now=new Date()){
 document.querySelectorAll('[data-task-timing]').forEach(el=>{el.textContent=t(current()?.rest_day?'Optional today':taskTimingKey(el.dataset.time,state.timezone,now));});
}
function childHeading(c,title,greeting=false){const {tasks,done}=dayCount(c);return `<div class="child-heading"><p class="small muted">${esc(dateLabel(state.today))}</p><h1 ${greeting?'data-child-greeting':''}>${title}</h1>${tasks.length&&!c.rest_day?`<p class="day-tally">${tx('{done} of {total} done',{done,total:tasks.length})}</p>`:''}${childLevel(c)}</div>`;}
function childTools(){return `<div class="child-tools"><button data-action="view" data-view="daylist">${tx('See my day')}</button><button class="text-button" data-action="view" data-view="badges">${tx('My badges')}</button></div>`;}
function taskHelp(r,canDefer){return `<details class="task-help"><summary>${tx('I need help')}</summary><p>${esc(r.description||t('Ask an adult nearby to help you get started.'))}</p><div class="help-actions"><button data-action="ask-adult">${tx('Ask an adult')}</button><button data-action="defer" data-id="${r.id}" ${canDefer?'':'disabled'}>${tx('Come back later')}</button></div>${!canDefer?`<p class="small muted">${tx('There are no other steps to switch to. You can ask an adult or take a break.')}</p>`:''}<p data-help-response role="status"></p></details>`;}
function childToday(c){
 const {tasks,done}=dayCount(c),next=tasks.find(r=>!r.done&&!r.locked);
 let card;
 if(next){
  const instruction=next.first_action?`<p class="first-action">${esc(next.first_action)}</p>`:'';
  const canDefer=tasks.filter(r=>!r.done&&!r.locked).length>1;
  card=`<article class="focus-card"><p class="focus-label"><span data-task-timing data-time="${esc(next.time)}">${tx(c.rest_day?'Optional today':taskTimingKey(next.time,state.timezone))}</span> <time>${esc(timeLabel(next.time))}</time></p><div class="focus-title">${taskIcon(next)}<h2 id="next-step-title" tabindex="-1">${esc(next.title)}</h2></div>${instruction}<button class="primary focus-done" data-action="complete" data-id="${next.id}" aria-label="${tx('Done: {task}',{task:next.title})}">${tx('Done')} <span aria-hidden="true">✓</span></button><p id="step-feedback" class="step-feedback" role="status" aria-live="polite"></p>${taskHelp(next,canDefer)}</article>`;
 }else{
  const key=c.rest_day?'Rest day':!tasks.length?'Nothing planned today':done===tasks.length?'All done for today':'This step is open again. Let’s check it together.';
  card=`<section class="focus-card focus-finished"><span aria-hidden="true">${tasks.length&&done===tasks.length?'✓':'☁️'}</span><h2 id="next-step-title" tabindex="-1">${tx(key)}</h2></section>`;
 }
 return `${childHeading(c,tx(greetingKey(state.timezone),{name:c.name}),true)}${restNote(c)}${card}${undoFeedback()}${weatherSummary()}${childTools()}`;
}
function childChecklist(c){
 const {tasks}=dayCount(c);
 return `${childHeading(c,tx(greetingKey(state.timezone),{name:c.name}),true)}${restNote(c)}${undoFeedback()}<section class="child-checklist">${tasks.length?tasks.map(r=>`<article class="task ${r.done?'done':''}"><div class="task-time"><time>${esc(timeLabel(r.time))}</time>${!r.done?`<span class="task-timing" data-task-timing data-time="${esc(r.time)}">${tx(c.rest_day?'Optional today':taskTimingKey(r.time,state.timezone))}</span>`:''}</div><div class="task-content"><h2>${taskIcon(r)}${esc(r.title)}</h2>${r.first_action&&!r.done?`<p class="first-action">${esc(r.first_action)}</p>`:''}${r.defer_order&&!r.done?`<p class="small muted">${tx('For later today')}</p>`:''}${r.locked?`<p>${tx('This step is open again. Let’s check it together.')}</p>`:''}</div><button class="check" data-action="complete" data-id="${r.id}" aria-pressed="${r.done}" aria-label="${r.done?t('Undo'):t('Complete')} ${esc(r.title)}" ${r.locked?'disabled':''}>${r.done?'✓':'○'}</button></article>`).join(''):`<p>${tx('Nothing planned today')}</p>`}</section><div class="child-tools"><button data-action="view" data-view="focus">${tx('One task at a time')}</button><button class="text-button" data-action="view" data-view="plan">${tx('Weekly plan')}</button></div>`;
}
const themes=[['forest','Forest','#246b55'],['ocean','Ocean','#22658b'],['berry','Berry','#954369'],['lavender','Lavender','#6d4b91'],['sunshine','Sunshine','#825518'],['petrol','Lagoon','#146471']];
function applyTheme(value){const theme=themes.find(([id])=>id===value)||themes[0];document.documentElement.dataset.theme=theme[0];document.querySelector('meta[name="theme-color"]')?.setAttribute('content',theme[2]);}
function themePicker(){const chosen=state.user?.theme||'forest';return `<fieldset class="theme-picker"><legend>${tx('Color theme')}</legend><div class="theme-options">${themes.map(([id,label])=>`<button type="button" class="theme-option" data-action="theme" data-theme="${id}" aria-pressed="${chosen===id}"><span class="theme-swatch swatch-${id}" aria-hidden="true"></span><span>${tx(label)}</span><span class="theme-check" aria-hidden="true">${chosen===id?'✓':''}</span></button>`).join('')}</div></fieldset>`;}
async function setTheme(value){
 if(busy||!state.user||!themes.some(([id])=>id===value)||state.user.theme===value)return;
 const saved=drafts();busy=true;
 try{await api('preferences',{theme:value});state.user.theme=value;render();restoreDrafts(saved);document.querySelector(`[data-action="theme"][data-theme="${value}"]`)?.focus({preventScroll:true});}
 catch(error){notify(error.message);}finally{busy=false;}
}
function parentSettings(){return `<section class="panel personal-settings"><h1>${tx('Settings')}</h1>${themePicker()}</section>`;}
function childSettings(){return `<section class="panel child-settings"><h1>${tx('Settings')}</h1>${languagePicker()}${themePicker()}<button class="text-button" data-action="logout">${tx('Sign out')}</button></section>`;}
function childViewSettings(){return `<details class="panel child-view-settings"><summary>${tx('Child support settings')}</summary>${state.children.map(c=>`<form class="child-support-form" data-form="child-view" data-child="${c.id}"><input type="hidden" name="child" value="${c.id}"><h3>${esc(c.name)}</h3><label>${tx('Home screen')}<select name="day_view"><option value="focus" ${c.day_view!=='checklist'?'selected':''}>${tx('One task at a time')}</option><option value="checklist" ${c.day_view==='checklist'?'selected':''}>${tx('Full checklist')}</option></select></label><label class="support-toggle"><input type="checkbox" name="show_series" ${c.show_series!==false?'checked':''}><span>${tx('Show series badges')}<small>${tx('When off, series are hidden from the child’s collection and next goal. Earned badges are kept.')}</small></span></label><label class="support-toggle"><input type="checkbox" name="reduced_rewards" ${c.reduced_rewards?'checked':''}><span>${tx('Quiet rewards')}<small>${tx('Keep points and badges; use a simple acknowledgement instead of animations and celebrations.')}</small></span></label><button type="submit">${tx('Save changes')}</button></form>`).join('')}</details>`;}
function renderChild(c){
 const home=view==='today'||view==='focus';
 const content=view==='settings'?childSettings():view==='badges'?rewards(c):view==='plan'?planner(c):view==='weather'?weatherPanel():view==='daylist'||(view==='today'&&c.day_view==='checklist')?childChecklist(c):childToday(c);
 return `<header class="child-header"><div class="child-header-inner"><a class="brand" href="./"><span class="brand-icon" aria-hidden="true">🌱</span><span class="brand-name">Wusel<small>${tx('by Wild & Weich')}</small></span></a><button class="text-button child-settings-button" data-action="view" data-view="settings" aria-label="${tx('Settings')}" title="${tx('Settings')}" ${view==='settings'?'aria-current="page"':''}><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M10 2h4l.7 3L17 6.3l3-.9 2 3.4-2.3 2.2v2l2.3 2.2-2 3.4-3-.9-2.3 1.3-.7 3h-4l-.7-3L7 17.7l-3 .9-2-3.4L4.3 13v-2L2 8.8l2-3.4 3 .9L9.3 5Z"/><circle cx="12" cy="12" r="3"/></svg></button></div></header><div class="child-shell">${!home?`<button class="text-button child-back" data-action="view" data-view="today">← ${tx('My day')}</button>`:''}<main>${content}</main></div>`;
}
function compactWeatherAdvice(w){
 const hints=[['Pack a raincoat or umbrella.','Take your raincoat.'],['A warm layer could feel good today.','Take a warm layer.'],['It may get warm. Take your water bottle.','Take your water bottle.'],['A sun hat could be useful today.','Take your sun hat.'],['Ask a parent before going outside.','Ask a parent before going outside.'],['Check with a parent what to wear today.','Choose clothes with a parent.']];
 const hint=weatherAdvice(w)[0];return t(hints.find(([long])=>t(long)===hint)?.[1]||'Choose clothes with a parent.');
}
function weatherSummary(){
 const w=weatherData;
 let icon='☁️',message=t('Checking the weather…');
 if(w?.status==='ok'){
   icon=weatherIcon(w.current.condition);
   message=w.stale?t('Weather needs checking with a parent.'):temp(w.current.temperature)+' · '+compactWeatherAdvice(w);
 }else if(w)message=t('Ask a parent about today’s weather.');
 return `<div id="weather-panel" class="weather-summary"><button data-action="view" data-view="weather" aria-label="${tx('Weather for your day')}"><span aria-hidden="true">${icon}</span><span>${esc(message)}</span><span aria-hidden="true">›</span></button>${w?.demo?`<p class="preview-caption">${tx('Example weather for preview only')}</p>`:''}</div>`;
}

function render() {
 paintSyncStatus();
 document.documentElement.lang=language;
 applyTheme(state.user?.theme||'forest');
 app.classList.toggle('child-app',state.user?.role==='child');
 app.classList.toggle('quiet-rewards',state.user?.role==='child'&&!!current()?.reduced_rewards);
 if (!state.user) { app.innerHTML=auth(); return; }
 const c=current(); if(c)selected=c.id;
 if(!parent()){app.innerHTML=renderChild(c);return;}
 const tabs=[['today','☀',t('Overview')],['plan','▦',t('Weekly plan')],['badges','✧',t('Badges')],['review','✓',t('Review')]];
 const navButton=([id,icon,label])=>`<button data-action="view" data-view="${id}" class="nav-button ${view===id?'active':''}" ${view===id?'aria-current="page"':''}><span aria-hidden="true">${icon}</span> ${esc(label)}</button>`;
 app.innerHTML=`<header><div class="header-inner parent-header"><a class="brand" href="./"><span class="brand-icon">🌱</span> <span class="brand-name">Wusel<small>${tx('by Wild & Weich')}</small></span></a><details class="parent-account"><summary><span>${esc(state.user.name)}</span></summary><div class="parent-account-panel">${languagePicker(false)}<button class="text-button" data-action="logout">${tx('Sign out')}</button></div></details></div></header>
 <div class="shell"><nav class="parent-navigation" aria-label="${tx('Main')}">${c?`<label class="child-picker"><select id="child-picker" aria-label="${tx('Child')}">${state.children.map(c=>`<option value="${c.id}" ${c.id===selected?'selected':''}>${esc(c.name)}</option>`).join('')}</select></label><div class="child-tabs" role="group" aria-label="${tx('For {name}',{name:c.name})}">${tabs.map(navButton).join('')}</div>`:''}<div class="family-navigation" role="group" aria-label="${tx('Administration')}">${[['family','♧',t('Family')],['settings','⚙',t('Settings')]].map(navButton).join('')}</div></nav>
 <main>${view==='settings'?parentSettings():view==='family'?family():!c?`<section class="panel empty"><span aria-hidden="true">🌱</span><h1>${tx("Let’s plant the first seed")}</h1><p>${tx("Add a child account to start planning their day.")}</p><button class="primary" data-action="view" data-view="family">${tx("Add your family")}</button></section>`:({today,plan:planner,badges:rewards,review}[view]||today)(c)}</main><footer>${tx("A little more rhythm. A little more room to grow.")} <span>${tx("Local family garden")} · ${esc(state.timezone)}</span></footer></div>`;
}
app.addEventListener('change', async e=>{if(e.target.id==='language-picker'){await setLanguage(e.target.value);return;}if(e.target.id==='child-picker'){selected=Number(e.target.value);editing=null;render();}});
app.addEventListener('click',async e=>{
 const b=e.target.closest('[data-action]'); if(!b||busy)return;
 const action=b.dataset.action,id=Number(b.dataset.id),c=current();
 if(action==='undo-last'){
  if(!lastCompletion||lastCompletion.day!==state.today)return;
  const saved=lastCompletion;busy=true;b.disabled=true;
  try{await api('complete',{routine:saved.routine,done:false,day:saved.day});const r=current()?.routines.find(r=>r.id===saved.routine);if(r)r.done=false;clearUndo();await refresh();if(syncKind==='saved')syncStatus('idle');notify(t('Step undone.'),1600);}catch(error){notify(error.message);b.disabled=false;}finally{busy=false;}return;
 }
 if(action==='ask-adult'){b.closest('.task-help').querySelector('[data-help-response]').textContent=t('Please ask an adult to join you. You can do this step together.');return;}
 if(action==='theme'){await setTheme(b.dataset.theme);return;}
 if(action==='view'){view=b.dataset.view;editing=null;render();document.querySelector('main h1,main h2')?.focus({preventScroll:true});window.scrollTo(0,0);return;}
 if(action==='edit'){editing=(c.planned_routines||c.routines).find(r=>r.id===id);render();document.querySelector('.editor').scrollIntoView({behavior:'smooth'});return;}
 if(action==='cancel-edit'){editing=null;render();return;}
 if(action==='preset'){const ds=b.dataset.days.split(',');document.querySelectorAll('[name=days]').forEach(x=>x.checked=ds.includes(x.value));document.querySelector('[name=specific_date]').value='';return;}
 if(action==='reset-child'){
  const child=state.children.find(profile=>profile.id===id);if(!child)return;
  const dialog=document.createElement('dialog');dialog.className='archive-dialog reset-child-dialog';
  dialog.innerHTML=`<h2>${tx('Reset {name}’s account',{name:child.name})}</h2><p>${tx('This permanently deletes completions, points, levels, badges, streaks, planned rest days and personal settings. Created tasks, including archived tasks and scheduled changes, and login details are kept. The child will be signed out.')}</p><form data-form="reset-child"><input type="hidden" name="child" value="${child.id}"><p class="small">${tx('Type {username} to confirm.',{username:child.username})}</p>${field(t('Child username'),'confirmation','text','maxlength="40" autocomplete="off" autocapitalize="none" spellcheck="false"')}${field(t('Your current parent password'),'current_password','password','autocomplete="current-password"')}<div class="actions"><button class="primary" type="submit">${tx('Reset permanently')}</button><button type="button" data-action="close-dialog">${tx('Cancel')}</button></div></form>`;
  app.append(dialog);dialog.addEventListener('close',()=>dialog.remove());dialog.showModal();return;
 }
 if(action==='archive'){
  const dialog=document.createElement('dialog');dialog.className='archive-dialog';
  dialog.innerHTML=`<h2>${tx('Archive routine')}</h2><p>${tx('Archive this routine? Past progress will be kept.')}</p><form data-form="archive"><input type="hidden" name="routine" value="${id}">${changeTiming()}<div class="actions"><button class="primary" type="submit">${tx('Archive')}</button><button type="button" data-action="close-dialog">${tx('Cancel')}</button></div></form>`;
  app.append(dialog);dialog.addEventListener('close',()=>dialog.remove());dialog.showModal();return;
 }
 if(action==='close-dialog'){b.closest('dialog').close();return;}
 if(action==='badge'&&b.dataset.revoked==='true'&&!confirm(t("Remove this earned badge? You can restore it later.")))return;
 busy=true;b.disabled=true;
 const earnedBefore=new Set(c?.progress.badges.filter(b=>b.earned).map(b=>b.id)||[]);
 let childCompleted=false,earnedPoints=0;
 const progressBefore=c?{...c.progress}:null;
 try {
  if(action==='logout')await api('logout',{});
  if(action==='defer'){await api('defer',{routine:id,day:state.today});}
  if(action==='remove-rest')await api('rest-days',{child:c.id,start:b.dataset.start,end:b.dataset.end,remove:true});
  if(action==='complete'){
   const r=c.routines.find(r=>r.id===id);const result=await api('complete',{routine:id,done:!r.done,day:state.today});earnedPoints=result.earned_points||0;
   childCompleted=!parent()&&!r.done;
   if(childCompleted)rememberCompletion(r);
   r.done=!r.done;
   const feedback=document.querySelector('#step-feedback');
   if(childCompleted&&earnedPoints>0&&!c.reduced_rewards){showPoints(earnedPoints);if(feedback)feedback.textContent=t('Well done!');await new Promise(resolve=>setTimeout(resolve,750));}
   else if(!childCompleted)notify(!r.done?t('Step undone.'):t('Well done!'),1600);
  }
  if(action==='badge')await api('badge',{child:c.id,badge:b.dataset.id,revoked:b.dataset.revoked==='true'});
  if(action==='correct')await api('correct',{completion:id,restore:b.dataset.restore==='true'});
  await refresh();
  if(action==='remove-rest'){const editor=document.querySelector('.pause-editor');if(editor){editor.open=true;editor.querySelector('summary').focus({preventScroll:true});}}
  if(childCompleted){
   if(syncKind==='saved')syncStatus('idle');
   const badge=current().progress.badges.find(b=>b.earned&&!b.revoked&&!earnedBefore.has(b.id)&&(current().show_series!==false||b.kind!=='streak'));
   if(earnedPoints>0&&!current().reduced_rewards){
    animateLevel(progressBefore,current().progress);
    if(current().progress.level>progressBefore.level)celebrateLevel(current().progress.level,badge);
    else if(badge)notify(t('New badge: {badge}',{badge:t(badge.name)}),3000);
   }
   (document.querySelector('#next-step-title')||document.querySelector(`[data-action="complete"][data-id="${id}"]`))?.focus({preventScroll:true});
  }else if(action==='defer'){if(syncKind==='saved')syncStatus('idle');notify(t('Kept for later. Let’s try another step.'),2200);document.querySelector('#next-step-title')?.focus({preventScroll:true});}
  else if(['badge','correct','remove-rest'].includes(action))notify(t('Saved for {name}.',{name:c.name}));
  else if(action==='complete')document.querySelector(`[data-action="complete"][data-id="${id}"]`)?.focus();
 }catch(err){if(childCompleted)render();notify(err.message);b.disabled=false;}finally{busy=false;}
});
app.addEventListener('submit',async e=>{
 e.preventDefault();if(busy)return;const f=e.target,d=Object.fromEntries(new FormData(f)),kind=f.dataset.form,b=f.querySelector('button[type=submit],button.primary,button:not([type])');
 f.querySelector('[data-form-error]')?.remove();
 const affectedId=Number(d.child)||current()?.id;
 const affected=state.children?.find(c=>c.id===affectedId)?.name||'';
 busy=true;if(b)b.disabled=true;
 try {
  if(kind==='setup'||kind==='login')await api(kind,d);
  if(kind==='account')await api('users',d);
  if(kind==='child-view')await api('child-settings',{child:Number(d.child),day_view:d.day_view,show_series:f.elements.show_series.checked,reduced_rewards:f.elements.reduced_rewards.checked});
  if(kind==='password')await api('password',{...d,user:Number(d.user)});
  if(kind==='reset-child'){await api('reset-child',{child:Number(d.child),confirmation:d.confirmation,current_password:d.current_password});f.closest('dialog').close();}
  if(kind==='rest-days')await api('rest-days',{child:Number(d.child),start:d.start,end:d.end});
  if(kind==='archive'){await api('archive',{routine:Number(d.routine),apply_from:d.apply_from});f.closest('dialog').close();}
  if(kind==='routine') {await api('routines',{...d,id:d.id?Number(d.id):undefined,child:affectedId,days:[...f.querySelectorAll('[name=days]:checked')].map(x=>Number(x.value))});editing=null;}
  let message=t('Saved.');
  if(kind==='routine'||kind==='archive')message=t(d.apply_from==='tomorrow'?'Changes for {name} saved. Applies from tomorrow.':'Changes for {name} saved. Applies today.',{name:affected});
  else if(kind==='child-view'||kind==='rest-days')message=t('Saved for {name}.',{name:affected});
  else if(kind==='reset-child')message=t('Account for {name} reset. Created tasks were kept.',{name:affected});
  else if(kind==='account')message=t('Account created for {name}.',{name:d.name});
  else if(kind==='password'){const account=[...(state.parents||[]),...(state.children||[])].find(a=>a.id===Number(d.user));message=t('Password reset for {name}.',{name:account?.name||''});}
  if(kind!=='login')notify(message);await refresh();
  if(kind==='rest-days'){const editor=document.querySelector('.pause-editor');if(editor){editor.open=true;editor.querySelector('[name=start]').value=d.start;editor.querySelector('[name=end]').value=d.end;editor.querySelector('button[type=submit]').focus({preventScroll:true});}}
 }catch(err){const error=document.createElement('p');error.dataset.formError='';error.className='form-error';error.setAttribute('role','alert');error.textContent=err.message;f.insertBefore(error,f.querySelector('.actions')||f.firstChild);if(!f.closest('dialog'))notify(err.message);if(b)b.disabled=false;}finally{busy=false;}
});
// Weather is fetched separately, so a slow provider never delays the daily checklist.
let weatherData=null, weatherBusy=false, weatherFetched=0;
const weatherIcons={'clear-night':'🌙',cloudy:'☁️',exceptional:'⚠️',fog:'🌫️',hail:'🌨️',lightning:'⛈️','lightning-rainy':'⛈️',partlycloudy:'🌤️',pouring:'🌧️',rainy:'🌧️',snowy:'❄️','snowy-rainy':'🌨️',sunny:'☀️',windy:'🌬️','windy-variant':'🌬️',unknown:'🌡️'};
const weatherNames={'clear-night':'Clear night',cloudy:'Cloudy',exceptional:'Unusual conditions',fog:'Foggy',hail:'Hail',lightning:'Thunderstorms','lightning-rainy':'Thunderstorms and rain',partlycloudy:'Partly cloudy',pouring:'Heavy rain',rainy:'Rain',snowy:'Snow','snowy-rainy':'Snow and rain',sunny:'Sunny',windy:'Windy','windy-variant':'Windy and cloudy',unknown:'Conditions unknown'};
const weatherName=c=>t(weatherNames[c]||'Conditions unknown');
const weatherIcon=c=>weatherIcons[c]||weatherIcons.unknown;
const temp=v=>temperatureLabel(v,weatherData.unit||'');
const weatherTime=value=>new Date(value).toLocaleTimeString(locale(),{timeZone:state.timezone,hour:'numeric',minute:'2-digit'});
function weatherAdvice(w){
 const entries=[w.current,...w.hourly,...(w.daily?[w.daily]:[])],conditions=entries.map(e=>e.condition);
 if(conditions.some(c=>['exceptional','lightning','lightning-rainy','hail'].includes(c)))return [t('Ask a parent before going outside.')];
 const hints=[];
 if(conditions.some(c=>['rainy','pouring','snowy-rainy'].includes(c))||entries.some(e=>e.rain_probability>=40))hints.push(t('Pack a raincoat or umbrella.'));
 const temperatures=entries.flatMap(e=>[e.temperature,e.low,e.high]).filter(v=>typeof v==='number').map(v=>w.unit==='°F'?(v-32)*5/9:v);
 if(['°C','°F'].includes(w.unit)&&temperatures.length){
   if(Math.min(...temperatures)<=12)hints.push(t('A warm layer could feel good today.'));
   else if(Math.max(...temperatures)>=26)hints.push(t('It may get warm. Take your water bottle.'));
 }
 if(conditions.includes('sunny'))hints.push(t('A sun hat could be useful today.'));
 return (hints.length?hints:[t('Check with a parent what to wear today.')]).slice(0,2);
}
function parentWeather(open=false){
 const w=weatherData;
 const summary=!w?t('Checking the weather…'):w.status!=='ok'?t('Weather is unavailable right now.'):temp(w.current.temperature)+' · '+weatherName(w.current.condition);
 return `<details id="weather-panel" class="parent-weather" ${open?'open':''}><summary><span aria-hidden="true">${w?.status==='ok'?weatherIcon(w.current.condition):'☁️'}</span><span><strong>${tx('Weather for your day')}</strong><span class="small muted">${esc(summary)}${w?.stale?' · '+tx('Last known weather — check with a parent before heading out.'):''}</span></span></summary>${weatherPanel(true)}</details>`;
}
function weatherPanel(embedded=false){
 const w=weatherData;
 let content;
 if(!w)content=`<p class="muted">${tx('Checking the weather…')}</p>`;
 else if(w.status!=='ok')content=`<p>${tx(w.status==='not_configured'?'Ask a parent to set up the weather.':'Weather is unavailable right now.')}</p><p class="small muted">${tx(parent()?'Select a weather entity in the Home Assistant app configuration.':'Your routines are ready. Ask a parent to check the weather with you.')}</p>`;
 else {
  const slots=w.hourly.filter((_,i)=>i%3===0).slice(0,8);
  content=`${w.demo?`<p class="weather-warning">${tx('Example weather for preview only')}</p>`:''}<div class="weather-overview"><div class="weather-current"><span class="weather-symbol" aria-hidden="true">${weatherIcon(w.current.condition)}</span><div><span class="small muted">${tx('Now')}</span><h3>${esc(temp(w.current.temperature))} <span>${esc(weatherName(w.current.condition))}</span></h3><p class="small muted">${esc(w.location)}</p></div></div><p class="weather-update small muted">${tx('From Home Assistant')}<br> ${tx('Updated {time}',{time:weatherTime(w.fetched_at)})}</p></div>
  ${w.stale?`<p class="weather-warning">${tx('Last known weather — check with a parent before heading out.')}</p>`:`<div class="weather-advice"><strong>${tx('GET READY FOR YOUR DAY')}</strong>${weatherAdvice(w).map(h=>`<span>${esc(h)}</span>`).join('')}</div>`}
  ${slots.length?`<h3 class="forecast-title">${tx('Later today')}</h3><ol class="forecast-slots">${slots.map((h,i)=>`<li class="${[0,Math.floor(slots.length/2),slots.length-1].includes(i)?'mobile-summary':''}"><time datetime="${esc(h.datetime)}">${esc(weatherTime(h.datetime))}</time><span class="forecast-icon" aria-hidden="true">${weatherIcon(h.condition)}</span><strong>${esc(temp(h.temperature))}</strong><span>${esc(weatherName(h.condition))}</span><span class="rain-chance">${tx('Rain chance')}: ${h.rain_probability===null?'—':esc(h.rain_probability)+'%'}</span></li>`).join('')}</ol>`:w.daily?`<h3 class="forecast-title">${tx('Today’s forecast')}</h3><p>${esc(weatherName(w.daily.condition))} · ${tx('Low')}: ${esc(temp(w.daily.low))} · ${tx('High')}: ${esc(temp(w.daily.high))}${w.daily.rain_probability!==null?' · '+tx('Rain chance')+': '+esc(w.daily.rain_probability)+'%':''}</p><p class="small muted">${tx('Daily forecast only; hourly details are not available.')}</p>`:`<p class="small muted">${tx('The forecast is unavailable; only current conditions are shown.')}</p>`}`;
 }
 return `<section ${embedded?'':'id="weather-panel"'} class="panel weather" aria-label="${tx('Weather for your day')}"><h2>${tx('Weather for your day')}</h2>${content}</section>`;
}
function weatherSetup(){return `<section class="panel weather-setup"><h2>${tx('Weather setup')}</h2><p>${tx('Weather comes from your selected Home Assistant weather entity.')}</p><p class="small muted">${tx('Select a weather entity in the Home Assistant app configuration.')} <code>weather_entity</code></p></section>`;}
async function loadWeather(){
 if(!state?.user||weatherBusy||Date.now()-weatherFetched<60000)return;
 const uid=state.user.id;weatherBusy=true;
 try{const data=await api('weather');if(state?.user?.id!==uid)return;weatherData=data;weatherFetched=Date.now();}
 catch{if(state?.user?.id===uid)weatherData={status:'unavailable'};}
 finally{weatherBusy=false;if(state?.user?.id===uid){const panel=document.querySelector('#weather-panel');if(panel)panel.outerHTML=parent()?parentWeather(panel.open):view!=='weather'?weatherSummary():weatherPanel();}}
}

refresh().catch(err=>{app.innerHTML=`<main class="panel"><h1>${tx("Could not open your garden")}</h1><p>${tx("Reload the page to try again.")}</p></main>`;notify(err.message);});
// Refresh the date after midnight and progress when returning to the app.
setInterval(()=>{if(state?.user&&!busy&&!document.querySelector('form'))refresh(true).catch(()=>{});},60000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&state?.user&&!busy&&!document.querySelector('form'))refresh(true).catch(()=>{});});

// Localized validation messages for required fields and browser constraints.
app.addEventListener('invalid',event=>{event.target.setCustomValidity(t(event.target.validity.valueMissing?'Please complete this field.':'Please check the value in this field.'));},true);
app.addEventListener('input',event=>{if(event.target.setCustomValidity)event.target.setCustomValidity('');});

document.addEventListener('click',event=>{const menu=document.querySelector('.parent-account');if(menu&&!menu.contains(event.target))menu.open=false;});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){const menu=document.querySelector('.parent-account[open]');if(menu){menu.open=false;menu.querySelector('summary').focus();}}});

document.addEventListener('click',async event=>{
 if(event.target.closest('[data-dismiss-sync]'))syncStatus('idle');
 const button=event.target.closest('[data-reconnect]');
 if(button&&!busy){busy=true;button.disabled=true;try{await refresh(true);const target=document.querySelector('[data-dismiss-sync],.focus-done,.nav-button.active');target?.focus({preventScroll:true});}catch{document.querySelector('[data-reconnect]')?.focus({preventScroll:true});}finally{busy=false;button.disabled=false;}}
});
window.addEventListener('offline',()=>syncStatus('offline','Connection lost. Your list may be out of date.'));
window.addEventListener('online',()=>{if(!busy)refresh(true).catch(()=>{});});
