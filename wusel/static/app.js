'use strict';
let state, view = 'today', selected, editing = null, busy = false;
const app = document.querySelector('#app');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const parent = () => state.user?.role === 'parent';
const current = () => state.children?.find(c => c.id === selected) || state.children?.[0];
let noticeTimer;
function notify(message,duration=6500) { document.querySelector('#notice').classList.remove('level-up'); clearTimeout(noticeTimer); document.querySelector('#notice').textContent = message; noticeTimer=setTimeout(()=>document.querySelector('#notice').textContent='',duration); }
async function api(path, body) {
  let response;try{response = await fetch('api/'+path, body === undefined ? {cache:'no-store'} : {
    method:'POST', headers:{'Content-Type':'application/json','X-Garden-Request':'1','X-CSRF-Token':state?.csrf || ''}, body:JSON.stringify(body)
  });}catch{throw new Error(t('Could not save. Please try again.'));}
  const data = await response.json();
  if (!response.ok) throw new Error(errorText(data.error || 'Could not save. Please try again.'));
  return data;
}
async function refresh(quiet=false) { const fresh=await api('state'); if(quiet && JSON.stringify(fresh)===JSON.stringify(state)){loadWeather();return;} state=fresh; if(state.user && !state.user.language){await api('preferences',{language});state.user.language=language;} if(state.user?.language) language=state.user.language; if (!state.user) {view='today'; selected=null;weatherData=null;weatherFetched=0;} render(); if(state.user)loadWeather(); }
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
  ${parentWeather()}
  <section class="today-layout"><div><div class="section-heading"><h2>${tx("Today’s little steps")}</h2><span class="muted small">${tx("10 points per step")}</span></div>
  ${tasks.length?tasks.map(r=>`<article class="task ${r.done?'done':''} ${next?.id===r.id?'next':''}"><div class="task-time">${esc(timeLabel(r.time))}${next?.id===r.id?`<span class="next-label">${tx("UP NEXT")}</span>`:''}</div><div class="task-content"><h3>${esc(r.title)}</h3>${r.description?`<p>${esc(r.description)}</p>`:''}${r.locked?`<p class="small">${tx("A parent is helping review this step.")}</p>`:''}</div><button class="check" data-action="complete" data-id="${r.id}" aria-pressed="${r.done}" aria-label="${r.done?t("Undo"):t("Complete")} ${esc(r.title)}" ${r.locked?'disabled':''}>${r.done?'✓':`<span aria-hidden="true">○</span>`}</button></article>`).join(''):`<div class="panel empty"><span aria-hidden="true">☁️</span><h3>${tx("A little breathing room")}</h3><p>${parent()?t("Add a routine in Weekly plan to get started."):t("No steps planned for today. Enjoy your day!")}</p></div>`}
  ${tasks.length&&done===tasks.length?`<div class="celebrate" role="status">${tx("🌻 All your steps are done. Look at you grow!")}</div>`:''}</div>
  <aside class="panel encouragement"><span class="sun" aria-hidden="true">☀️</span><p class="eyebrow">${tx("A LITTLE REMINDER")}</p><h2>${tx("Progress grows")}<br>${tx("one step at a time.")}</h2><p>${tx("You don’t have to do everything at once. Just start with your next little step.")}</p><div class="divider"></div><p class="small muted">${tx("Every new day is a fresh start.")}</p></aside></section>${progress(c)}`;
}
function scheduleLabel(r) {return r.specific_date?dateLabel(r.specific_date):r.days.map(d=>dayNames()[d]).join(' · ');}
function scheduleEditor(c) {
 const r=editing || {title:'',description:'',time:'07:00',days:[0,1,2,3,4],specific_date:''};
 return `<details class="panel editor" ${editing?'open':''}><summary>${editing?t("Edit routine"):t("＋ Add a little step")}</summary><form data-form="routine">
 <input type="hidden" name="id" value="${editing?.id || ''}"><div class="form-grid">${field(t("What is the step?"),'title','text',`maxlength="100" value="${esc(r.title)}"`)}${field(t("Time"),'time','time',`value="${esc(r.time)}"`)}</div>
 <label>${tx("A little guidance (optional)")}<textarea name="description" maxlength="500" rows="2">${esc(r.description)}</textarea></label>
 <fieldset><legend>${tx("Repeat on these days")}</legend><div class="presets"><button type="button" class="text-button" data-action="preset" data-days="0,1,2,3,4">${tx("Weekdays")}</button><button type="button" class="text-button" data-action="preset" data-days="5,6">${tx("Weekend")}</button><button type="button" class="text-button" data-action="preset" data-days="0,1,2,3,4,5,6">${tx("Every day")}</button></div><div class="day-picks">${dayNames().map((d,i)=>`<label><input name="days" type="checkbox" value="${i}" ${r.days.includes(i)?'checked':''}><span>${d}</span></label>`).join('')}</div></fieldset>
 <label>${tx("Or, on one specific date (optional)")}<input type="date" name="specific_date" value="${esc(r.specific_date)}"></label><p class="small muted">${tx("A specific date takes priority over the weekday selection. Make a separate routine for a different weekend time.")}</p>
 <div class="actions"><button class="primary" type="submit">${editing?t("Save changes"):t("Add step")}</button>${editing?`<button type="button" data-action="cancel-edit">${tx("Cancel")}</button>`:''}</div></form></details>`;
}
function planner(c) {
  const monday=new Date(state.today+'T12:00:00Z');
  monday.setUTCDate(monday.getUTCDate()-(monday.getUTCDay()+6)%7);
  const dates=Array.from({length:7},(_,i)=>{const d=new Date(monday);d.setUTCDate(d.getUTCDate()+i);return d.toISOString().slice(0,10);});
  return `<div class="heading"><div><p class="eyebrow">${tx("MAKE ROOM FOR GOOD HABITS")}</p><h1>${tx("Weekly plan")}</h1><p>${tx("{name}’s rhythm, with room for different days.",{name:c.name})}</p></div></div>
  ${parent()?scheduleEditor(c):''}<section class="week-grid">${dates.map(d=>{let weekday=(new Date(d+'T12:00:00Z').getUTCDay()+6)%7;let rs=c.routines.filter(r=>r.specific_date?r.specific_date===d:r.days.includes(weekday));return `<div class="day-column ${d===state.today?'is-today':''}"><h3>${dayNames()[weekday]} <span>${d.slice(8)}</span></h3>${rs.length?rs.map(r=>`<div class="week-task"><time>${esc(timeLabel(r.time))}</time><strong>${esc(r.title)}</strong></div>`).join(''):`<p class="small muted">${tx("A clear day")}</p>`}</div>`;}).join('')}</section>
  ${parent()?`<div class="section-heading"><h2>${tx("All planned steps")}</h2></div><div class="panel routine-list">${c.routines.length?c.routines.map(r=>`<article><div><h3>${esc(timeLabel(r.time))} · ${esc(r.title)}</h3><p class="small muted">${esc(scheduleLabel(r))}</p></div><div class="actions"><button data-action="edit" data-id="${r.id}">${tx("Edit")}</button><button class="text-button danger" data-action="archive" data-id="${r.id}">${tx("Archive")}</button></div></article>`).join(''):`<p>${tx("No routines yet. Add the first step above.")}</p>`}</div>`:''}`;
}
function rewards(c) {
 return `<div class="heading"><div><p class="eyebrow">${tx("CELEBRATE THE LITTLE WINS")}</p><h1>${tx(parent()?"{name}’s badges":"My badges",{name:c.name})}</h1><p>${tx("Something to be proud of, at your own pace.")}</p></div></div>${progress(c)}<div class="badge-grid">${c.progress.badges.map(b=>`<article class="panel badge ${b.earned&&!b.revoked?'earned':'unearned'}"><span class="badge-icon" aria-hidden="true">${b.icon}</span><h3>${esc(t(b.name))}</h3><p>${tx(b.threshold===1?"{count} completed step":"{count} completed steps",{count:b.threshold})}</p><span class="pill">${b.earned?(b.revoked?t("Removed by a parent"):tx("Earned {date}",{date:dateLabel(b.earned)})):t("Still growing")}</span>${parent()&&b.earned?`<button class="text-button ${b.revoked?'':'danger'}" data-action="badge" data-id="${b.id}" data-revoked="${!b.revoked}">${b.revoked?t("Restore badge"):t("Remove badge")}</button>`:''}</article>`).join('')}</div>`;
}
function review(c) {
 return `<div class="heading"><div><p class="eyebrow">${tx("A HELPING HAND")}</p><h1>${tx("Review progress")}</h1><p>${tx("{name}’s latest 100 steps. Corrections update points and levels.",{name:c.name})}</p></div></div><p class="muted">${tx("Badges celebrate milestones already reached. Remove a badge separately in Badges if needed.")}</p><div class="panel history">${c.history.length?c.history.map(h=>`<article><div><h3>${esc(h.title)}</h3><p class="small muted">${esc(dateLabel(h.day))} · ${h.voided?(h.locked?t("Corrected by parent"):t("Undone")):t("+10 points")}</p></div><button data-action="correct" data-id="${h.id}" data-restore="${!!h.voided}">${h.voided?t("Restore"):t("Reverse completion")}</button></article>`).join(''):`<p>${tx("Completed steps will appear here.")}</p>`}</div>`;
}
function family() {
 const accounts=[...state.parents.map(p=>({...p,role:'parent'})),...state.children.map(c=>({...c,role:'child'}))];
 return `<div class="heading"><div><p class="eyebrow">${tx("YOUR LITTLE TEAM")}</p><h1>${tx("Family")}</h1><p>${tx("All parents in this garden can manage every child.")}</p></div></div><div class="family-grid"><section class="panel"><h2>${tx("Add an account")}</h2><form data-form="account"><label>${tx("Account type")}<select name="role"><option value="child">${tx("Child")}</option><option value="parent">${tx("Parent")}</option></select></label>${field(t("Name"),'name','text','maxlength="50"')}${field(t("Username"),'username','text','minlength="3" maxlength="40" autocapitalize="none" autocomplete="off"')}${field(t("Password"),'password','password','minlength="4" maxlength="128" autocomplete="new-password"')}<p class="small muted">${tx("Passwords need at least 4 characters.")}</p><button class="primary">${tx("Create account")}</button></form></section>
 <section class="panel"><h2>${tx("Your family")}</h2>${accounts.map(a=>`<div class="account"><span class="avatar" aria-hidden="true">${a.role==='parent'?'🌳':'🌱'}</span><div><strong>${esc(a.name)}</strong><p class="small muted">${esc(a.username)} · ${tx(a.role==='parent'?'Parent':'Child')}</p></div></div>`).join('')}<details><summary>${tx("Reset a password")}</summary><form data-form="password"><label>${tx("Account")}<select name="user">${accounts.map(a=>`<option value="${a.id}">${esc(a.name)} (${tx(a.role==='parent'?'Parent':'Child')})</option>`).join('')}</select></label>${field(t("New password"),'password','password','minlength="4" maxlength="128" autocomplete="new-password"')}<label>${tx("Your current parent password (for parent resets)")}<input type="password" name="current_password" autocomplete="current-password"></label><button>${tx("Reset password")}</button></form></details></section></div>
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
function childHeading(c,title){const {tasks,done}=dayCount(c);return `<div class="child-heading"><p class="small muted">${esc(dateLabel(state.today))}</p><h1>${title}</h1>${tasks.length?`<p class="day-tally">${tx('{done} of {total} done',{done,total:tasks.length})}</p>`:''}${childLevel(c)}</div>`;}
function childTools(){return `<div class="child-tools"><button data-action="view" data-view="daylist">${tx('See my day')}</button><button class="text-button" data-action="view" data-view="badges">${tx('My badges')}</button></div>`;}
function childToday(c){
 const {tasks,done}=dayCount(c),next=tasks.find(r=>!r.done&&!r.locked);
 let card;
 if(next){
  const instruction=next.description?(next.description.length<=120?`<p class="focus-instruction">${esc(next.description)}</p>`:`<details class="focus-help"><summary>${tx('Help')}</summary><p class="focus-instruction">${esc(next.description)}</p></details>`):'';
  card=`<article class="focus-card"><p class="focus-label">${tx('Next step')} <time>${esc(timeLabel(next.time))}</time></p><h2 id="next-step-title" tabindex="-1">${esc(next.title)}</h2>${instruction}<button class="primary focus-done" data-action="complete" data-id="${next.id}" aria-label="${tx('Done: {task}',{task:next.title})}">${tx('Done')} <span aria-hidden="true">✓</span></button><p id="step-feedback" class="step-feedback" role="status" aria-live="polite"></p></article>`;
 }else{
  const key=!tasks.length?'Nothing planned today':done===tasks.length?'All done for today':'A parent is reviewing a step.';
  card=`<section class="focus-card focus-finished"><span aria-hidden="true">${tasks.length&&done===tasks.length?'✓':'☁️'}</span><h2 id="next-step-title" tabindex="-1">${tx(key)}</h2></section>`;
 }
 return `${childHeading(c,tx('Hi, {name}',{name:c.name}))}${card}${weatherSummary()}${childTools()}`;
}
function childChecklist(c){
 const {tasks}=dayCount(c);
 return `${childHeading(c,tx('My day'))}<section class="child-checklist">${tasks.length?tasks.map(r=>`<article class="task ${r.done?'done':''}"><time class="task-time">${esc(timeLabel(r.time))}</time><div class="task-content"><h2>${esc(r.title)}</h2>${r.locked?`<p>${tx('A parent is reviewing a step.')}</p>`:''}</div><button class="check" data-action="complete" data-id="${r.id}" aria-pressed="${r.done}" aria-label="${r.done?t('Undo'):t('Complete')} ${esc(r.title)}" ${r.locked?'disabled':''}>${r.done?'✓':'○'}</button></article>`).join(''):`<p>${tx('Nothing planned today')}</p>`}</section><div class="child-tools"><button data-action="view" data-view="focus">${tx('One task at a time')}</button><button class="text-button" data-action="view" data-view="plan">${tx('Weekly plan')}</button></div>`;
}
const themes=[['forest','Forest','#246b55'],['ocean','Ocean','#22658b'],['berry','Berry','#954369'],['lavender','Lavender','#6d4b91'],['sunshine','Sunshine','#825518']];
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
function childViewSettings(){return `<section class="panel child-view-settings"><h2>${tx('Children’s home screens')}</h2>${state.children.map(c=>`<form data-form="child-view" data-child="${c.id}"><input type="hidden" name="child" value="${c.id}"><label>${esc(c.name)}<select name="day_view"><option value="focus" ${c.day_view!=='checklist'?'selected':''}>${tx('One task at a time')}</option><option value="checklist" ${c.day_view==='checklist'?'selected':''}>${tx('Full checklist')}</option></select></label><button type="submit">${tx('Save changes')}</button></form>`).join('')}</section>`;}
function renderChild(c){
 const home=view==='today'||view==='focus';
 const content=view==='settings'?childSettings():view==='badges'?rewards(c):view==='plan'?planner(c):view==='weather'?weatherPanel():view==='daylist'||(view==='today'&&c.day_view==='checklist')?childChecklist(c):childToday(c);
 return `<header class="child-header"><div class="child-header-inner"><a class="brand" href="./"><span class="brand-icon" aria-hidden="true">🌱</span><span class="brand-name">Wusel<small>${tx('by Wild & Weich')}</small></span></a><button class="text-button" data-action="view" data-view="settings" ${view==='settings'?'aria-current="page"':''}>${tx('Settings')}</button></div></header><div class="child-shell">${!home?`<button class="text-button child-back" data-action="view" data-view="today">← ${tx('My day')}</button>`:''}<main>${content}</main></div>`;
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
 document.documentElement.lang=language;
 applyTheme(state.user?.theme||'forest');
 app.classList.toggle('child-app',state.user?.role==='child');
 if (!state.user) { app.innerHTML=auth(); return; }
 const c=current(); if(c)selected=c.id;
 if(!parent()){app.innerHTML=renderChild(c);return;}
 const tabs=[['today','☀',t("My day")],['plan','▦',t("Weekly plan")],['badges','✧',t("Badges")],...(parent()?[['review','✓',t("Review")],['family','♧',t("Family")],['settings','⚙',t("Settings")]]:[])];
 app.innerHTML=`<header><div class="header-inner"><a class="brand" href="./"><span class="brand-icon">🌱</span> <span class="brand-name">Wusel<small>${tx('by Wild & Weich')}</small></span></a><div class="user-menu">${languagePicker()}<span>${esc(state.user.name)} <span class="pill">${parent()?t("Parent"):t("My garden")}</span></span><button class="text-button" data-action="logout">${tx("Sign out")}</button></div></div></header>
 <div class="shell"><nav aria-label="${tx("Main")}">${tabs.map(([id,icon,label])=>`<button data-action="view" data-view="${id}" class="nav-button ${view===id?'active':''}" ${view===id?'aria-current="page"':''}><span aria-hidden="true">${icon}</span> ${esc(label)}</button>`).join('')}${parent()&&state.children.length?`<label class="child-picker">${tx("Garden for")}<select id="child-picker">${state.children.map(c=>`<option value="${c.id}" ${c.id===selected?'selected':''}>${esc(c.name)}</option>`).join('')}</select></label>`:''}</nav>
 <main>${view==='settings'?parentSettings():view==='family'?family():!c?`<section class="panel empty"><span aria-hidden="true">🌱</span><h1>${tx("Let’s plant the first seed")}</h1><p>${tx("Add a child account to start planning their day.")}</p><button class="primary" data-action="view" data-view="family">${tx("Add your family")}</button></section>`:({today,plan:planner,badges:rewards,review}[view]||today)(c)}</main><footer>${tx("A little more rhythm. A little more room to grow.")} <span>${tx("Local family garden")} · ${esc(state.timezone)}</span></footer></div>`;
}
app.addEventListener('change', async e=>{if(e.target.id==='language-picker'){await setLanguage(e.target.value);return;}if(e.target.id==='child-picker'){selected=Number(e.target.value);editing=null;render();}});
app.addEventListener('click',async e=>{
 const b=e.target.closest('[data-action]'); if(!b||busy)return;
 const action=b.dataset.action,id=Number(b.dataset.id),c=current();
 if(action==='theme'){await setTheme(b.dataset.theme);return;}
 if(action==='view'){view=b.dataset.view;editing=null;render();document.querySelector('main h1,main h2')?.focus({preventScroll:true});window.scrollTo(0,0);return;}
 if(action==='edit'){editing=c.routines.find(r=>r.id===id);render();document.querySelector('.editor').scrollIntoView({behavior:'smooth'});return;}
 if(action==='cancel-edit'){editing=null;render();return;}
 if(action==='preset'){const ds=b.dataset.days.split(',');document.querySelectorAll('[name=days]').forEach(x=>x.checked=ds.includes(x.value));document.querySelector('[name=specific_date]').value='';return;}
 if(action==='archive'&&!confirm(t("Archive this routine? Past progress will be kept.")))return;
 if(action==='badge'&&b.dataset.revoked==='true'&&!confirm(t("Remove this earned badge? You can restore it later.")))return;
 busy=true;b.disabled=true;
 const earnedBefore=new Set(c?.progress.badges.filter(b=>b.earned).map(b=>b.id)||[]);
 let childCompleted=false,earnedPoints=0;
 const progressBefore=c?{...c.progress}:null;
 try {
  if(action==='logout')await api('logout',{});
  if(action==='complete'){
   const r=c.routines.find(r=>r.id===id);const result=await api('complete',{routine:id,done:!r.done});earnedPoints=result.earned_points||0;
   childCompleted=!parent()&&!r.done;
   const feedback=document.querySelector('#step-feedback');
   if(childCompleted&&earnedPoints>0){showPoints(earnedPoints);if(feedback)feedback.textContent=t('Well done!');await new Promise(resolve=>setTimeout(resolve,750));}
   else if(!childCompleted)notify(r.done?t('Step undone.'):t('Well done!'),1600);
  }
  if(action==='archive')await api('archive',{routine:id});
  if(action==='badge')await api('badge',{child:c.id,badge:b.dataset.id,revoked:b.dataset.revoked==='true'});
  if(action==='correct')await api('correct',{completion:id,restore:b.dataset.restore==='true'});
  await refresh();
  if(childCompleted){
   const badge=current().progress.badges.find(b=>b.earned&&!b.revoked&&!earnedBefore.has(b.id));
   if(earnedPoints>0){
    animateLevel(progressBefore,current().progress);
    if(current().progress.level>progressBefore.level)celebrateLevel(current().progress.level,badge);
    else if(badge)notify(t('New badge: {badge}',{badge:t(badge.name)}),3000);
   }
   (document.querySelector('#next-step-title')||document.querySelector(`[data-action="complete"][data-id="${id}"]`))?.focus({preventScroll:true});
  }else if(action==='complete')document.querySelector(`[data-action="complete"][data-id="${id}"]`)?.focus();
 }catch(err){notify(err.message);b.disabled=false;}finally{busy=false;}
});
app.addEventListener('submit',async e=>{
 e.preventDefault();if(busy)return;const f=e.target,d=Object.fromEntries(new FormData(f)),kind=f.dataset.form,b=f.querySelector('button[type=submit],button.primary,button:not([type])');
 busy=true;if(b)b.disabled=true;
 try {
  if(kind==='setup'||kind==='login')await api(kind,d);
  if(kind==='account')await api('users',d);
  if(kind==='child-view')await api('child-settings',{child:Number(d.child),day_view:d.day_view});
  if(kind==='password')await api('password',{...d,user:Number(d.user)});
  if(kind==='routine') {await api('routines',{...d,id:d.id?Number(d.id):undefined,child:current().id,days:[...f.querySelectorAll('[name=days]:checked')].map(x=>Number(x.value))});editing=null;}
  if(kind!=='login')notify(kind==='login'?t("Welcome back."):kind==='password'?t("Password reset. Existing sessions for that account were signed out."):t("Saved. Your garden is up to date."));await refresh();
 }catch(err){notify(err.message);if(b)b.disabled=false;}finally{busy=false;}
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
