"""Local family routines; Python 3.12+, SQLite, WSGI."""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import date, datetime, timezone, timedelta
from http.cookies import SimpleCookie
from pathlib import Path
from zoneinfo import ZoneInfo
from weather import Weather

TASK_ICONS = ('','tooth','clothes','food','bag','book','bed','wash','water','shoes','play','tidy','quiet','medicine')

BADGES = [('first', 'First step', 1, '🌱'), ('five', 'Growing strong', 5, '🌿'),
          ('twenty', 'Routine explorer', 20, '🌻'), ('fifty', 'Shining star', 50, '⭐'),
          ('hundred', 'Routine champion', 100, '🏆'),
          ('ten', 'Little adventurer', 10, '🧭'), ('onefifty', 'Soaring high', 150, '🪁'),
          ('twofifty', 'Bright comet', 250, '☄️'), ('fivehundred', 'Super explorer', 500, '🚀'),
          ('thousand', 'A thousand little wins', 1000, '🌌')]
DAY_BADGES = [('day1', 'A whole day', 1, '☀️'), ('day10', 'Ten bright days', 10, '🌈'),
              ('day30', 'Thirty bright days', 30, '💎')]
STREAK_BADGES = [('streak3', 'Finding a rhythm', 3, '🎵'), ('streak7', 'A week of little wins', 7, '🔥'),
                 ('streak14', 'Two weeks of rhythm', 14, '🎶'), ('streak30', 'A month of little wins', 30, '👑')]
ALL_BADGES = [(b,kind) for kind,items in [('steps',BADGES),('days',DAY_BADGES),('streak',STREAK_BADGES)] for b in sorted(items,key=lambda b:b[2])]
SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,
 name TEXT NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('parent','child')));
CREATE TABLE IF NOT EXISTS routines(id INTEGER PRIMARY KEY,child INTEGER REFERENCES users(id),
 title TEXT,description TEXT,time TEXT,days TEXT,specific_date TEXT DEFAULT '',archived INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS completions(id INTEGER PRIMARY KEY,routine INTEGER REFERENCES routines(id),
 child INTEGER REFERENCES users(id),day TEXT,title TEXT,points INTEGER DEFAULT 10,
 voided INTEGER DEFAULT 0,locked INTEGER DEFAULT 0,UNIQUE(routine,day));
CREATE TABLE IF NOT EXISTS badges(child INTEGER REFERENCES users(id),badge TEXT,earned TEXT,
 revoked INTEGER DEFAULT 0,PRIMARY KEY(child,badge));
CREATE TABLE IF NOT EXISTS daily_plans(child INTEGER REFERENCES users(id),day TEXT,routines TEXT NOT NULL,PRIMARY KEY(child,day));
CREATE TABLE IF NOT EXISTS pending_routines(routine INTEGER PRIMARY KEY REFERENCES routines(id),effective_on TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rest_days(child INTEGER REFERENCES users(id),day TEXT,PRIMARY KEY(child,day));
CREATE TABLE IF NOT EXISTS deferred_steps(routine INTEGER REFERENCES routines(id),child INTEGER REFERENCES users(id),day TEXT,position INTEGER NOT NULL,PRIMARY KEY(routine,day));
CREATE INDEX IF NOT EXISTS deferred_child_day ON deferred_steps(child,day);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user INTEGER REFERENCES users(id),csrf TEXT,expires REAL);
CREATE TABLE IF NOT EXISTS attempts(key TEXT,at REAL);
CREATE INDEX IF NOT EXISTS attempts_key ON attempts(key,at);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at TEXT,actor INTEGER,action TEXT,detail TEXT);
'''

class Problem(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status

def password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
    return f'{salt}${digest}'

def password_matches(password, stored):
    salt, expected = stored.split('$')
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
    return hmac.compare_digest(actual, expected)

class ScopedConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

class Application:
    def __init__(self, data_dir, tz='Europe/Zurich', secure_cookie=False, weather_entity=''):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'wusel.sqlite3'
        self.zone = ZoneInfo(tz)
        self.secure_cookie = secure_cookie
        self.weather = Weather(weather_entity)
        self.static = Path(__file__).parent / 'static'
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript(SCHEMA)
            if 'undo_until' not in {row[1] for row in db.execute('PRAGMA table_info(completions)')}:
                db.execute('ALTER TABLE completions ADD COLUMN undo_until REAL NOT NULL DEFAULT 0')
            for column,definition in [('show_series','INTEGER NOT NULL DEFAULT 1'),('reduced_rewards','INTEGER NOT NULL DEFAULT 0')]:
                if column not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                    db.execute('ALTER TABLE users ADD COLUMN '+column+' '+definition)
            if 'first_action' not in {row[1] for row in db.execute('PRAGMA table_info(routines)')}:
                db.execute("ALTER TABLE routines ADD COLUMN first_action TEXT NOT NULL DEFAULT ''")
            if 'icon' not in {row[1] for row in db.execute('PRAGMA table_info(routines)')}:
                db.execute("ALTER TABLE routines ADD COLUMN icon TEXT NOT NULL DEFAULT ''")
            if 'badge_goal' not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                db.execute("ALTER TABLE users ADD COLUMN badge_goal TEXT NOT NULL DEFAULT ''")
            if 'starts_on' not in {row[1] for row in db.execute('PRAGMA table_info(routines)')}:
                db.execute("ALTER TABLE routines ADD COLUMN starts_on TEXT NOT NULL DEFAULT ''")
            if 'language' not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                db.execute("ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT ''")
            if 'day_view' not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                db.execute("ALTER TABLE users ADD COLUMN day_view TEXT NOT NULL DEFAULT 'focus'")
            if 'theme' not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                db.execute("ALTER TABLE users ADD COLUMN theme TEXT NOT NULL DEFAULT 'forest'")
            if 'plain_icons' not in {row[1] for row in db.execute('PRAGMA table_info(users)')}:
                db.execute("ALTER TABLE users ADD COLUMN plain_icons INTEGER NOT NULL DEFAULT 0")
        code = self.data_dir / 'setup-code'
        if not code.exists():
            code.write_text(secrets.token_urlsafe(18), encoding='utf-8')
        self.setup_code = code.read_text(encoding='utf-8').strip()
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=15, factory=ScopedConnection)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db
    def today(self):
        return datetime.now(self.zone).date()
    def now(self):
        return datetime.now(timezone.utc).timestamp()
    def audit(self, db, actor, action, detail):
        db.execute('INSERT INTO audit(at,actor,action,detail) VALUES(?,?,?,?)',
                   (datetime.now(timezone.utc).isoformat(), actor, action, detail))
    def text(self, body, key, minimum=1, maximum=120):
        value = body.get(key)
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
            raise Problem(f'{key.replace("_", " ").capitalize()} must be {minimum}–{maximum} characters.')
        return value.strip()
    def integer(self, body, key):
        value = body.get(key)
        if type(value) is not int or value < 1:
            raise Problem(f'Choose a valid {key}.')
        return value
    def credentials(self, body, role):
        name = self.text(body, 'name', maximum=50)
        username = self.text(body, 'username', 3, 40).lower()
        if not re.fullmatch(r'[a-z0-9_.-]+', username):
            raise Problem('Username can contain letters, numbers, dots, underscores and hyphens.')
        password = body.get('password', '')
        length = 4
        if not isinstance(password, str) or not length <= len(password) <= 128:
            raise Problem(f'Password must be {length}–128 characters.')
        return name, username, password_hash(password)
    def throttle(self, db, key):
        db.execute('DELETE FROM attempts WHERE at < ?', (self.now()-900,))
        if db.execute('SELECT COUNT(*) FROM attempts WHERE key=?', (key,)).fetchone()[0] >= 10:
            raise Problem('Too many attempts. Try again in 15 minutes.', 429)
        db.execute('INSERT INTO attempts VALUES(?,?)', (key, self.now()))
        db.commit()  # Persist failed attempts too.
    def session(self, db, environ):
        cookie = SimpleCookie()
        try:
            cookie.load(environ.get('HTTP_COOKIE', ''))
            token = cookie['wusel_session'].value if 'wusel_session' in cookie else ''
        except Exception:
            token = ''
        return db.execute('''SELECT users.*,sessions.csrf FROM sessions JOIN users ON users.id=sessions.user
                             WHERE token=? AND expires>?''',
                          (hashlib.sha256(token.encode()).hexdigest(), self.now())).fetchone()
    def new_session(self, db, uid):
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE expires<=?', (self.now(),))
        db.execute('INSERT INTO sessions VALUES(?,?,?,?)',
                   (hashlib.sha256(token.encode()).hexdigest(), uid, csrf, self.now()+43200))
        return f'wusel_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=43200' + ('; Secure' if self.secure_cookie else '')
    def correct_completion(self, db, user, completion, restore):
        db.execute('UPDATE completions SET voided=?,locked=?,undo_until=0 WHERE id=?',
                   (int(not restore),int(not restore),completion['id']))
        if restore:
            self.award(db,completion['child'])
        self.audit(db,user['id'],'correction',f'{"Restored" if restore else "Reversed"} completion {completion["id"]}: {completion["title"]} ({completion["day"]})')
    def undo_seconds(self, completion):
        return max(0,completion['undo_until']-self.now()) if completion and not completion['voided'] and not completion['locked'] else 0
    def child(self, db, uid):
        row = db.execute("SELECT id FROM users WHERE id=? AND role='child'", (uid,)).fetchone()
        if not row:
            raise Problem('Child profile not found.', 404)
    def scheduled(self, r, day):
        if r['starts_on'] and day.isoformat() < r['starts_on']:
            return False
        return r['specific_date'] == day.isoformat() if r['specific_date'] else day.weekday() in json.loads(r['days'])
    def activate_pending(self, db):
        today = self.today().isoformat()
        if not db.execute('SELECT 1 FROM pending_routines WHERE effective_on<=? LIMIT 1',(today,)).fetchone():
            return
        db.execute('BEGIN IMMEDIATE')
        for change in db.execute('SELECT * FROM pending_routines WHERE effective_on<=?',(today,)).fetchall():
            data = json.loads(change['payload'])
            columns = ','.join(k+'=?' for k in data)
            db.execute('UPDATE routines SET '+columns+' WHERE id=?',(*data.values(),change['routine']))
            db.execute('DELETE FROM pending_routines WHERE routine=?',(change['routine'],))
        db.commit()
    def change_date(self, body):
        choice = body.get('apply_from','today')
        if choice not in ('today','tomorrow'):
            raise Problem('Choose when to apply this change.')
        return self.today() + timedelta(days=choice=='tomorrow')
    def record_plan(self, db, child, replace=False):
        today = self.today()
        planned = [r['id'] for r in db.execute('SELECT * FROM routines WHERE child=? AND archived=0',(child,)) if self.scheduled(r,today)]
        verb = 'REPLACE' if replace else 'IGNORE'
        db.execute('INSERT OR '+verb+' INTO daily_plans(child,day,routines) VALUES(?,?,?)',(child,today.isoformat(),json.dumps(planned)))
    def day_stats(self, db, child):
        # Keep past plans immutable so later routine edits cannot rewrite a child's history.
        today = self.today()
        self.record_plan(db,child)
        done = {(r['day'],r['routine']) for r in db.execute('SELECT day,routine FROM completions WHERE child=? AND voided=0 AND day<=?',(child,today.isoformat()))}
        pauses = {date.fromisoformat(r['day']) for r in db.execute('SELECT day FROM rest_days WHERE child=? AND day<=?',(child,today.isoformat()))}
        full = []
        for plan in db.execute('SELECT day,routines FROM daily_plans WHERE child=? AND day<=? ORDER BY day',(child,today.isoformat())):
            ids = json.loads(plan['routines'])
            if date.fromisoformat(plan['day']) not in pauses and ids and all((plan['day'],rid) in done for rid in ids):
                full.append(date.fromisoformat(plan['day']))
        best = run = 0
        previous = None
        for day in full:
            gap = (day-previous).days-1 if previous else 0
            neutral = sum(previous < pause < day for pause in pauses) if previous else 0
            run = run+1 if previous and gap == neutral else 1
            best = max(best,run)
            previous = day
        # Today's unfinished plan does not end yesterday's series before the day is over.
        gap = max(0,(today-previous).days-1) if previous else 0
        neutral = sum(previous < pause < today for pause in pauses) if previous else 0
        current = run if previous and gap == neutral else 0
        return {'full_days':len(full),'best_streak':best,'current_streak':current}
    def award(self, db, child):
        count = db.execute('SELECT COUNT(*) FROM completions WHERE child=? AND voided=0', (child,)).fetchone()[0]
        stats = self.day_stats(db,child)
        for (key, _, threshold, _),kind in ALL_BADGES:
            value = {'steps':count,'days':stats['full_days'],'streak':stats['best_streak']}[kind]
            if value >= threshold:
                db.execute('INSERT OR IGNORE INTO badges(child,badge,earned) VALUES(?,?,?)', (child,key,self.today().isoformat()))
        return stats
    def progress(self, db, child):
        stats = self.award(db,child)
        count, xp = db.execute('SELECT COUNT(*),COALESCE(SUM(points),0) FROM completions WHERE child=? AND voided=0', (child,)).fetchone()
        records = {r['badge']: dict(r) for r in db.execute('SELECT * FROM badges WHERE child=?', (child,))}
        badges = [{'id':k,'name':n,'threshold':threshold,'icon':icon,'kind':kind,
                   'earned':records.get(k,{}).get('earned'),'revoked':bool(records.get(k,{}).get('revoked',0)),
                   'value':{'steps':count,'days':stats['full_days'],'streak':stats['current_streak']}[kind]}
                  for (k,n,threshold,icon),kind in ALL_BADGES]
        show_series = db.execute('SELECT show_series FROM users WHERE id=?',(child,)).fetchone()['show_series']
        eligible = [badge for badge in badges if not badge['earned'] and (show_series or badge['kind']!='streak')]
        goal = db.execute('SELECT badge_goal FROM users WHERE id=?',(child,)).fetchone()['badge_goal']
        if goal not in {badge['id'] for badge in eligible}:
            goal = max(eligible,key=lambda badge:badge['value']/badge['threshold'])['id'] if eligible else ''
            db.execute('UPDATE users SET badge_goal=? WHERE id=?',(goal,child))
        return {'count':count,'xp':xp,'level':xp//100+1,'level_progress':xp%100,**stats,'next_badge':goal,'badges':badges}
    def state(self, db, user):
        today = self.today()
        result = {'needs_setup':not db.execute('SELECT 1 FROM users LIMIT 1').fetchone(),
                  'today':today.isoformat(),'timezone':str(self.zone),'user':None}
        if user is None:
            return result
        result.update(user={k:user[k] for k in ('id','name','username','role','language','theme')},csrf=user['csrf'])
        children = db.execute("SELECT id,name,username,day_view,show_series,reduced_rewards,plain_icons FROM users WHERE role='child' ORDER BY name").fetchall() if user['role']=='parent' else [user]
        profiles = []
        for c in children:
            child = {k:c[k] for k in ('id','name','username','day_view')}
            child.update(show_series=bool(c['show_series']),reduced_rewards=bool(c['reduced_rewards']),plain_icons=bool(c['plain_icons']))
            deferred = {row['routine']:row['position'] for row in db.execute('SELECT routine,position FROM deferred_steps WHERE child=? AND day=?',(c['id'],today.isoformat()))}
            routines = []
            for r in db.execute('SELECT * FROM routines WHERE child=? AND archived=0 ORDER BY time,id', (c['id'],)):
                item = dict(r)
                item['days'] = json.loads(item['days'])
                item['scheduled'] = self.scheduled(r,today)
                done = db.execute('SELECT voided,locked,undo_until FROM completions WHERE routine=? AND day=?', (r['id'],today.isoformat())).fetchone()
                item.update(done=bool(done and not done['voided']),locked=bool(done and done['locked']),defer_order=deferred.get(r['id'],0),undo_seconds=self.undo_seconds(done) if user['role']=='child' else 0)
                routines.append(item)
            routines.sort(key=lambda r:(r['defer_order']>0,r['defer_order'],r['time'],r['id']))
            child.update(routines=routines,progress=self.progress(db,c['id']))
            child['rest_days'] = [r['day'] for r in db.execute('SELECT day FROM rest_days WHERE child=? AND day>=? ORDER BY day',(c['id'],today.isoformat()))]
            child['rest_day'] = today.isoformat() in child['rest_days']
            projected = []
            for item in routines:
                change = db.execute('SELECT * FROM pending_routines WHERE routine=?',(item['id'],)).fetchone()
                planned = dict(item)
                if change:
                    update = json.loads(change['payload'])
                    if 'days' in update: update['days'] = json.loads(update['days'])
                    planned.update(update)
                    planned['effective_on'] = change['effective_on']
                elif item['starts_on'] > today.isoformat():
                    planned['effective_on'] = item['starts_on']
                projected.append(planned)
            child['planned_routines'] = projected
            if user['role']=='parent':
                child['history'] = [dict(r) for r in db.execute('SELECT * FROM completions WHERE child=? ORDER BY day DESC,id DESC LIMIT 100', (c['id'],))]
            profiles.append(child)
        result['children'] = profiles
        if user['role']=='parent':
            result['parents'] = [dict(r) for r in db.execute("SELECT id,name,username,day_view FROM users WHERE role='parent' ORDER BY name")]
            result['audit'] = [dict(r) for r in db.execute('SELECT audit.*,users.name AS actor_name FROM audit JOIN users ON users.id=audit.actor ORDER BY audit.id DESC LIMIT 30')]
        return result
    def dispatch(self, db, path, method, body, user, env):
        if method=='GET' and path=='/api/state':
            return self.state(db,user), None
        if method=='GET' and path=='/api/weather':
            if user is None:
                raise Problem('Please sign in.',401)
            return self.weather.get(self.zone),None
        if method!='POST':
            raise Problem('Page not found.',404)
        if env.get('HTTP_X_WUSEL_REQUEST')!='1':
            raise Problem('Request could not be verified. Reload the page.',403)
        if path=='/api/setup':
            self.throttle(db,'setup:'+env.get('REMOTE_ADDR',''))
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM users LIMIT 1').fetchone():
                raise Problem('Setup is already complete.',409)
            if not hmac.compare_digest(str(body.get('code','')).encode(),self.setup_code.encode()):
                raise Problem('Setup code is incorrect. Find it in the app logs.',403)
            n,u,p = self.credentials(body,'parent')
            uid = db.execute("INSERT INTO users(name,username,password,role) VALUES(?,?,?,'parent')",(n,u,p)).lastrowid
            self.audit(db,uid,'setup','Created the first parent account')
            return {'ok':True},self.new_session(db,uid)
        if path=='/api/login':
            username = self.text(body,'username',maximum=40).lower()
            self.throttle(db,'login:'+env.get('REMOTE_ADDR',''))
            account = db.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
            password = body.get('password','')
            if not isinstance(password,str) or len(password)>128:
                raise Problem('Username or password is incorrect.',401)
            stored = account['password'] if account else '0'*32+'$'+'0'*64
            valid = password_matches(password,stored)
            if not account or not valid:
                raise Problem('Username or password is incorrect.',401)
            return {'ok':True},self.new_session(db,account['id'])
        if user is None:
            raise Problem('Please sign in.',401)
        if not hmac.compare_digest(env.get('HTTP_X_CSRF_TOKEN','').encode(),user['csrf'].encode()):
            raise Problem('Your session changed. Reload the page.',403)
        if path=='/api/preferences':
            changes = {}
            if 'language' in body:
                if body['language'] not in ('en','de'):
                    raise Problem('Choose English or German.')
                changes['language'] = body['language']
            if 'theme' in body:
                if body['theme'] not in ('forest','ocean','berry','lavender','sunshine','petrol'):
                    raise Problem('Choose a valid color theme.')
                changes['theme'] = body['theme']
            if not changes:
                raise Problem('Choose a preference to change.')
            columns = ','.join(key+'=?' for key in changes)
            db.execute('UPDATE users SET '+columns+' WHERE id=?',(*changes.values(),user['id']))
            return {'ok':True},None
        if path=='/api/logout':
            raw = SimpleCookie(env.get('HTTP_COOKIE',''))['wusel_session'].value
            db.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(raw.encode()).hexdigest(),))
            return {'ok':True},'wusel_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'
        if path=='/api/complete':
            rid = self.integer(body,'routine')
            db.execute('BEGIN IMMEDIATE')
            r = db.execute('SELECT * FROM routines WHERE id=? AND archived=0',(rid,)).fetchone()
            if not r or (user['role']!='parent' and r['child']!=user['id']):
                raise Problem('Routine not found.',404)
            today = self.today()
            if body.get('day',today.isoformat()) != today.isoformat():
                raise Problem('The day has changed. Refresh your day before checking this step.',409)
            if not self.scheduled(r,today):
                raise Problem('This routine is not scheduled for today.')
            done = body.get('done')
            if type(done) is not bool:
                raise Problem('Choose completed or not completed.')
            old = db.execute('SELECT * FROM completions WHERE routine=? AND day=?',(rid,today.isoformat())).fetchone()
            if old and user['role']=='parent':
                self.correct_completion(db,user,old,done)
                return {'ok':True,'earned_points':0,'undo_seconds':0},None
            if old and old['locked']:
                raise Problem('This step is open again. Let’s check it together.',403)
            if old:
                if not done and not old['voided'] and self.undo_seconds(old)<=0:
                    raise Problem('Undo time has ended. Ask a parent to reopen this step.',403)
                deadline = self.now()+15 if done and old['voided'] else old['undo_until'] if done else 0
                db.execute('UPDATE completions SET voided=?,undo_until=? WHERE id=?',(int(not done),deadline,old['id']))
            elif done:
                db.execute('INSERT INTO completions(routine,child,day,title,undo_until) VALUES(?,?,?,?,?)',(rid,r['child'],today.isoformat(),r['title'],self.now()+15 if user['role']=='child' else 0))
            self.award(db,r['child'])
            saved = db.execute('SELECT voided,locked,undo_until FROM completions WHERE routine=? AND day=?',(rid,today.isoformat())).fetchone()
            return {'ok':True,'earned_points':10 if done and old is None else 0,'undo_seconds':self.undo_seconds(saved) if user['role']=='child' else 0},None
        if path=='/api/defer':
            rid = self.integer(body,'routine')
            db.execute('BEGIN IMMEDIATE')
            r = db.execute('SELECT * FROM routines WHERE id=? AND archived=0',(rid,)).fetchone()
            if not r or (user['role']!='parent' and r['child']!=user['id']):
                raise Problem('Routine not found.',404)
            today = self.today()
            if body.get('day') != today.isoformat():
                raise Problem('The day has changed. Refresh your day before checking this step.',409)
            if not self.scheduled(r,today):
                raise Problem('This routine is not scheduled for today.')
            completion = db.execute('SELECT voided,locked FROM completions WHERE routine=? AND day=?',(rid,today.isoformat())).fetchone()
            if completion and completion['locked']:
                raise Problem('This step is open again. Let’s check it together.',403)
            if completion and not completion['voided']:
                raise Problem('This step is already completed.',409)
            others = db.execute('SELECT r.* FROM routines r WHERE r.child=? AND r.archived=0 AND r.id!=? AND NOT EXISTS(SELECT 1 FROM completions c WHERE c.routine=r.id AND c.day=? AND (c.voided=0 OR c.locked=1))',(r['child'],rid,today.isoformat())).fetchall()
            if not any(self.scheduled(other,today) for other in others):
                raise Problem('There are no other steps to switch to.',409)
            position = db.execute('SELECT COALESCE(MAX(position),0)+1 FROM deferred_steps WHERE child=? AND day=?',(r['child'],today.isoformat())).fetchone()[0]
            db.execute('INSERT OR REPLACE INTO deferred_steps VALUES(?,?,?,?)',(rid,r['child'],today.isoformat(),position))
            return {'ok':True},None
        if user['role']!='parent':
            raise Problem('Only a parent can do this.',403)
        if path=='/api/reset-child':
            child = self.integer(body,'child')
            db.execute('BEGIN IMMEDIATE')
            self.child(db,child)
            account = db.execute('SELECT username FROM users WHERE id=?',(child,)).fetchone()
            if body.get('confirmation') != account['username']:
                raise Problem('Enter the child’s username to confirm the reset.')
            if not password_matches(str(body.get('current_password','')),user['password']):
                raise Problem('Enter your current parent password.',403)
            db.execute('DELETE FROM completions WHERE child=?',(child,))
            db.execute('DELETE FROM badges WHERE child=?',(child,))
            db.execute('DELETE FROM daily_plans WHERE child=?',(child,))
            db.execute('DELETE FROM rest_days WHERE child=?',(child,))
            db.execute('DELETE FROM deferred_steps WHERE child=?',(child,))
            db.execute('DELETE FROM sessions WHERE user=?',(child,))
            db.execute("UPDATE users SET language='',theme='forest',day_view='focus',badge_goal='',show_series=1,reduced_rewards=0,plain_icons=0 WHERE id=?",(child,))
            self.audit(db,user['id'],'reset',f'Reset child account: {account["username"]}')
            return {'ok':True},None
        if path=='/api/rest-days':
            child = self.integer(body,'child')
            self.child(db,child)
            try:
                start = date.fromisoformat(body.get('start',''))
                end = date.fromisoformat(body.get('end',''))
            except (ValueError,TypeError):
                raise Problem('Choose a valid rest-day range.')
            if end < start:
                raise Problem('The end date must be on or after the start date.')
            if start < self.today() or (end-start).days > 365 or type(body.get('remove',False)) is not bool:
                raise Problem('Choose today or future dates, up to 366 days at a time.')
            db.execute('BEGIN IMMEDIATE')
            if body.get('remove',False):
                db.execute('DELETE FROM rest_days WHERE child=? AND day BETWEEN ? AND ?',(child,start.isoformat(),end.isoformat()))
            else:
                db.executemany('INSERT OR IGNORE INTO rest_days(child,day) VALUES(?,?)',[(child,(start+timedelta(days=i)).isoformat()) for i in range((end-start).days+1)])
            self.audit(db,user['id'],'rest-days',f'Changed rest days for child {child}')
            return {'ok':True},None
        if path=='/api/child-settings':
            child = self.integer(body,'child')
            self.child(db,child)
            changes = {}
            if 'day_view' in body:
                if body['day_view'] not in ('focus','checklist'):
                    raise Problem('Choose a valid day view.')
                changes['day_view'] = body['day_view']
            for key in ('show_series','reduced_rewards','plain_icons'):
                if key in body:
                    if type(body[key]) is not bool:
                        raise Problem('Choose a valid support setting.')
                    changes[key] = int(body[key])
            if not changes:
                raise Problem('Choose a setting to change.')
            db.execute('UPDATE users SET '+','.join(key+'=?' for key in changes)+' WHERE id=?',(*changes.values(),child))
            self.audit(db,user['id'],'support',f'Changed support settings for child {child}')
        elif path=='/api/users':
            role = body.get('role')
            if role not in ('parent','child'):
                raise Problem('Choose parent or child.')
            n,u,p = self.credentials(body,role)
            db.execute('INSERT INTO users(name,username,password,role) VALUES(?,?,?,?)',(n,u,p,role))
            self.audit(db,user['id'],'account',f'Created {role} account: {u}')
        elif path=='/api/password':
            uid = self.integer(body,'user')
            account = db.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
            if not account:
                raise Problem('Account not found.',404)
            _,_,hashed = self.credentials({'name':account['name'],'username':account['username'],'password':body.get('password')},account['role'])
            if account['role']=='parent' and not password_matches(str(body.get('current_password','')),user['password']):
                raise Problem('Enter your current parent password.',403)
            db.execute('UPDATE users SET password=? WHERE id=?',(hashed,uid))
            db.execute('DELETE FROM sessions WHERE user=?',(uid,))
            self.audit(db,user['id'],'password',f'Reset password: {account["username"]}')
        elif path=='/api/routines':
            child = self.integer(body,'child')
            self.child(db,child)
            title = self.text(body,'title',maximum=100)
            description = self.text(body,'description',0,500)
            at = self.text(body,'time',5,5)
            try:
                datetime.strptime(at,'%H:%M')
            except ValueError:
                raise Problem('Choose a valid time.')
            days,special = body.get('days',[]),body.get('specific_date','')
            if not isinstance(days,list) or any(type(d) is not int or d not in range(7) for d in days):
                raise Problem('Choose valid weekdays.')
            if not isinstance(special,str):
                raise Problem('Choose a valid date.')
            if special:
                try:
                    date.fromisoformat(special)
                except ValueError:
                    raise Problem('Choose a valid date.')
            elif not days:
                raise Problem('Choose at least one weekday or a specific date.')
            first_action = self.text(body,'first_action',0,160) if 'first_action' in body else ''
            icon = body.get('icon','')
            if icon not in TASK_ICONS:
                raise Problem('Choose a valid task icon.')
            effective = self.change_date(body)
            db.execute('BEGIN IMMEDIATE')
            self.record_plan(db,child)
            data = dict(title=title,description=description,time=at,days=json.dumps(sorted(set(days))),specific_date=special,archived=0,icon=icon,first_action=first_action)
            if body.get('id'):
                rid = self.integer(body,'id')
                old = db.execute('SELECT icon,first_action FROM routines WHERE child=? AND id=? AND archived=0',(child,rid)).fetchone()
                if not old:
                    raise Problem('Routine not found.',404)
                if 'icon' not in body:
                    data['icon'] = old['icon']
                if 'first_action' not in body:
                    data['first_action'] = old['first_action']
                if effective > self.today():
                    db.execute('INSERT OR REPLACE INTO pending_routines VALUES(?,?,?)',(rid,effective.isoformat(),json.dumps(data)))
                else:
                    db.execute('UPDATE routines SET title=?,description=?,time=?,days=?,specific_date=?,archived=?,icon=?,first_action=?,starts_on=? WHERE id=?',(*data.values(),'',rid))
                    db.execute('DELETE FROM pending_routines WHERE routine=?',(rid,))
            else:
                db.execute('INSERT INTO routines(title,description,time,days,specific_date,archived,icon,first_action,child,starts_on) VALUES(?,?,?,?,?,?,?,?,?,?)',(*data.values(),child,effective.isoformat()))
            if effective == self.today():
                self.record_plan(db,child,replace=True)
            self.audit(db,user['id'],'routine',f'Saved routine for child {child}: {title}')
        elif path=='/api/archive':
            rid = self.integer(body,'routine')
            effective = self.change_date(body)
            db.execute('BEGIN IMMEDIATE')
            routine = db.execute('SELECT * FROM routines WHERE id=? AND archived=0',(rid,)).fetchone()
            if not routine:
                raise Problem('Routine not found.',404)
            self.record_plan(db,routine['child'])
            if effective > self.today():
                db.execute('INSERT OR REPLACE INTO pending_routines VALUES(?,?,?)',(rid,effective.isoformat(),json.dumps({'archived':1})))
            else:
                db.execute('UPDATE routines SET archived=1 WHERE id=?',(rid,))
                db.execute('DELETE FROM pending_routines WHERE routine=?',(rid,))
                self.record_plan(db,routine['child'],replace=True)
            self.audit(db,user['id'],'archive',f'Archived routine {rid}')
        elif path=='/api/correct':
            cid = self.integer(body,'completion')
            db.execute('BEGIN IMMEDIATE')
            c = db.execute('SELECT * FROM completions WHERE id=?',(cid,)).fetchone()
            if not c:
                raise Problem('Completion not found.',404)
            restore = body.get('restore',False)
            if type(restore) is not bool:
                raise Problem('Choose a valid correction.')
            self.correct_completion(db,user,c,restore)
        elif path=='/api/badge':
            child = self.integer(body,'child')
            self.child(db,child)
            badge = body.get('badge')
            if badge not in [b[0] for b,_ in ALL_BADGES] or type(body.get('revoked')) is not bool:
                raise Problem('Choose a valid badge action.')
            if not db.execute('UPDATE badges SET revoked=? WHERE child=? AND badge=?',(int(body['revoked']),child,badge)).rowcount:
                raise Problem('This badge has not been earned yet.')
            self.audit(db,user['id'],'badge',f'{"Revoked" if body["revoked"] else "Restored"} badge {badge} for child {child}')
        else:
            raise Problem('Page not found.',404)
        return {'ok':True},None
    def __call__(self, env, start_response):
        headers = [('X-Content-Type-Options','nosniff'),('Referrer-Policy','same-origin'),
                   ('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'none'; form-action 'self'"),('Cache-Control','no-store')]
        status,ctype = 200,'application/json; charset=utf-8'
        path,method = env.get('PATH_INFO','/'),env.get('REQUEST_METHOD','GET')
        try:
            if path=='/health' and method=='GET':
                payload = b'{"ok":true}'
            elif path in ('/','/static/app.js','/static/i18n.js','/static/style.css','/static/themes.css') and method=='GET':
                name = 'index.html' if path=='/' else path.rsplit('/',1)[1]
                ctype = {'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','i18n.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8','themes.css':'text/css; charset=utf-8'}[name]
                payload = (self.static/name).read_bytes()
            elif path.startswith('/api/'):
                body = {}
                if method=='POST':
                    if env.get('CONTENT_TYPE','').split(';')[0]!='application/json':
                        raise Problem('Send a JSON request.',415)
                    try:
                        length = int(env.get('CONTENT_LENGTH','0') or 0)
                    except ValueError:
                        raise Problem('Invalid request length.')
                    if not 0<length<=16384:
                        raise Problem('Request is empty or too large.',413)
                    try:
                        body = json.loads(env['wsgi.input'].read(length))
                    except (ValueError,UnicodeError):
                        raise Problem('Invalid JSON.')
                    if not isinstance(body,dict):
                        raise Problem('Expected an object.')
                db = self.connect()
                try:
                    self.activate_pending(db)
                    with db:
                        result,cookie = self.dispatch(db,path,method,body,self.session(db,env),env)
                finally:
                    db.close()
                if cookie:
                    headers.append(('Set-Cookie',cookie))
                payload = json.dumps(result).encode()
            else:
                raise Problem('Page not found.',404)
        except Problem as e:
            status,payload = e.status,json.dumps({'error':e.message}).encode()
        except sqlite3.IntegrityError:
            status,payload = 409,b'{"error":"That username is already in use, or the record has changed."}'
        except Exception:
            import traceback
            traceback.print_exc()
            status,payload = 500,b'{"error":"Something went wrong. Please try again."}'
        headers += [('Content-Type',ctype),('Content-Length',str(len(payload)))]
        reasons = {200:'OK',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',409:'Conflict',413:'Content Too Large',415:'Unsupported Media Type',429:'Too Many Requests',500:'Internal Server Error'}
        start_response(f'{status} {reasons[status]}',headers)
        return [payload]

def create_app():
    data = Path(os.environ.get('WUSEL_DATA','/data'))
    options = data/'options.json'
    config = json.loads(options.read_text()) if options.exists() else {}
    app = Application(data,config.get('timezone',os.environ.get('WUSEL_TIMEZONE','Europe/Zurich')),
                      config.get('secure_cookie',False) or os.environ.get('WUSEL_SECURE_COOKIE')=='1',
                      config.get('weather_entity',os.environ.get('WUSEL_WEATHER_ENTITY','')))
    with app.connect() as db:
        if not db.execute('SELECT 1 FROM users LIMIT 1').fetchone():
            print(f'Wusel first-run setup code: {app.setup_code}',flush=True)
    return app

if __name__=='__main__':
    app = create_app()
    if os.environ.get('WUSEL_DEV')=='1':
        from wsgiref.simple_server import make_server
        print('Local preview: http://127.0.0.1:8099',flush=True)
        make_server('127.0.0.1',8099,app).serve_forever()
    else:
        from server import serve_production
        serve_production(app)
