import io
import json
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application

class Client:
    def __init__(self,app): self.app,self.cookie,self.csrf=app,'',''
    def call(self,path,body=None,extra=None):
        raw=json.dumps(body).encode() if body is not None else b''
        env={'REQUEST_METHOD':'POST' if body is not None else 'GET','PATH_INFO':'/api/'+path,
             'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw),
             'REMOTE_ADDR':'127.0.0.1','HTTP_COOKIE':self.cookie,'HTTP_X_WUSEL_REQUEST':'1','HTTP_X_CSRF_TOKEN':self.csrf}
        env.update(extra or {})
        captured={}
        def start(status,headers): captured.update(status=int(status.split()[0]),headers=dict(headers))
        data=json.loads(b''.join(self.app(env,start)))
        if 'Set-Cookie' in captured['headers']: self.cookie=captured['headers']['Set-Cookie'].split(';')[0]
        if path=='state' and 'csrf' in data:self.csrf=data['csrf']
        return captured['status'],data

class WuselTests(unittest.TestCase):
    def setUp(self):
        scratch=Path.cwd()/'work'/'test-data'
        scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch)
        self.app=Application(self.temp.name)
        self.app.today=lambda:date(2026,10,26)  # Monday.
        self.parent=Client(self.app)
        self.assertEqual(self.parent.call('setup',{'code':self.app.setup_code,'name':'Parent','username':'parent','password':'parent-password'})[0],200)
        self.parent.call('state')
        for name in ['alex','sam']:
            self.assertEqual(self.parent.call('users',{'role':'child','name':name.title(),'username':name,'password':'child-pass'})[0],200)
        self.child=Client(self.app)
        self.child.call('login',{'username':'alex','password':'child-pass'})
        self.child.call('state')
    def tearDown(self): self.temp.cleanup()
    def create(self,**extra):
        body={'child':2,'title':'Brush teeth','description':'Two little minutes','time':'07:00','days':[0,1,2,3,4],'specific_date':''}
        body.update(extra)
        self.assertEqual(self.parent.call('routines',body)[0],200)
        with self.app.connect() as db: return db.execute('SELECT MAX(id) FROM routines').fetchone()[0]
    def profile(self,client=None): return (client or self.child).call('state')[1]['children'][0]
    def test_weekday_weekend_and_date(self):
        self.create();self.create(title='Weekend breakfast',days=[5,6]);self.create(title='Dentist',days=[],specific_date='2026-10-27')
        self.assertEqual([r['scheduled'] for r in self.profile()['routines']],[True,False,False])
        self.app.today=lambda:date(2026,10,31)
        self.assertEqual([r['scheduled'] for r in self.profile()['routines']],[False,True,False])
        self.app.today=lambda:date(2026,10,27)
        self.assertEqual([r['scheduled'] for r in self.profile()['routines']],[True,False,True])
    def test_repeated_checks_and_undo_do_not_farm_points(self):
        rid=self.create()
        for done in [True,True,False,True,True]:self.assertEqual(self.child.call('complete',{'routine':rid,'done':done})[0],200)
        self.assertEqual(self.profile()['progress']['xp'],10)
        self.assertEqual(self.profile()['progress']['count'],1)
        self.assertIsNotNone(self.profile()['progress']['badges'][0]['earned'])
    def test_children_are_isolated_and_cannot_manage(self):
        rid=self.create(child=3)
        self.assertEqual(len(self.child.call('state')[1]['children']),1)
        self.assertEqual(self.profile()['routines'],[])
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],404)
        for route in ['users','routines','badge','correct','password','archive']:
            self.assertEqual(self.child.call(route,{})[0],403)
    def test_parent_correction_locks_and_restore_unlocks(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        cid=self.profile(self.parent)['history'][0]['id']
        self.assertEqual(self.parent.call('correct',{'completion':cid})[0],200)
        self.assertEqual(self.profile()['progress']['xp'],0)
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],403)
        self.parent.call('correct',{'completion':cid,'restore':True})
        self.assertEqual(self.profile()['progress']['xp'],10)
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],200)
    def test_overview_and_review_share_parent_correction_lifecycle(self):
        rid=self.create()
        self.child.call('complete',{'routine':rid,'done':True})
        cid=self.profile(self.parent)['history'][0]['id']
        for reopen,restore in [
            (('complete',{'routine':rid,'done':False}),('correct',{'completion':cid,'restore':True})),
            (('correct',{'completion':cid}),('complete',{'routine':rid,'done':True}))]:
            self.assertEqual(self.parent.call(*reopen)[0],200)
            step=self.profile()['routines'][0]
            self.assertFalse(step['done']);self.assertTrue(step['locked'])
            self.assertEqual(self.profile()['progress']['xp'],0)
            self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],403)
            self.assertEqual(self.parent.call(*restore)[0],200)
            step=self.profile()['routines'][0]
            self.assertTrue(step['done']);self.assertFalse(step['locked'])
            self.assertEqual(self.profile()['progress']['xp'],10)
        with self.app.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM audit WHERE action='correction'").fetchone()[0],4)
    def test_revoked_badge_stays_revoked(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        self.assertEqual(self.parent.call('badge',{'child':2,'badge':'first','revoked':True})[0],200)
        r2=self.create(title='Get dressed');self.child.call('complete',{'routine':r2,'done':True})
        self.assertTrue(self.profile()['progress']['badges'][0]['revoked'])
        self.parent.call('badge',{'child':2,'badge':'first','revoked':False})
        self.assertFalse(self.profile()['progress']['badges'][0]['revoked'])
    def test_midnight_and_persistence(self):
        self.assertEqual(self.app.db_path, Path(self.temp.name)/'wusel.sqlite3')
        self.assertTrue(self.child.cookie.startswith('wusel_session='))
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        self.app.today=lambda:date(2026,10,27)
        self.assertFalse(self.profile()['routines'][0]['done'])
        self.child.call('complete',{'routine':rid,'done':True})
        self.assertEqual(self.profile()['progress']['xp'],20)
        restarted=Application(self.temp.name)
        restarted.today=self.app.today
        c=Client(restarted);c.cookie=self.child.cookie
        self.assertEqual(c.call('state')[1]['children'][0]['progress']['xp'],20)
    def test_validation_csrf_setup_and_missing_login(self):
        self.assertEqual(Client(self.app).call('complete',{'routine':1,'done':True})[0],401)
        self.assertEqual(self.parent.call('users',{}, {'HTTP_X_CSRF_TOKEN':'bad'})[0],403)
        self.assertEqual(self.parent.call('login',{}, {'HTTP_X_WUSEL_REQUEST':''})[0],403)
        self.assertEqual(self.parent.call('setup',{})[0],409)
        for extra in [{'days':[]},{'days':[7]},{'time':'29:00'},{'specific_date':'bad'},{'specific_date':1}]:
            body={'child':2,'title':'Task','description':'','time':'07:00','days':[0],**extra}
            self.assertEqual(self.parent.call('routines',body)[0],400)
    def test_edit_archive_keeps_history(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        self.create(id=rid,title='New title',time='08:00')
        self.assertEqual(self.profile(self.parent)['history'][0]['title'],'Brush teeth')
        self.parent.call('archive',{'routine':rid})
        self.assertEqual(self.profile()['routines'],[])
        self.assertEqual(self.profile()['progress']['xp'],10)
    def test_password_reset_revokes_sessions(self):
        self.assertEqual(self.parent.call('password',{'user':2,'password':'new-child-pass'})[0],200)
        self.assertIsNone(self.child.call('state')[1]['user'])
        self.assertEqual(self.child.call('login',{'username':'alex','password':'child-pass'})[0],401)
        self.assertEqual(self.child.call('login',{'username':'alex','password':'new-child-pass'})[0],200)
        self.assertEqual(self.parent.call('password',{'user':1,'password':'new-parent-pass'})[0],403)
    def test_four_character_passwords_for_both_roles(self):
        for role in ['parent', 'child']:
            with self.subTest(role=role):
                body={'role':role,'name':'Test','username':'short-'+role,'password':'123'}
                self.assertEqual(self.parent.call('users',body)[0],400)
                body['password']='1234'
                self.assertEqual(self.parent.call('users',body)[0],200)
                client=Client(self.app)
                self.assertEqual(client.call('login',{'username':body['username'],'password':'1234'})[0],200)
        for user in [1,2]:
            body={'user':user,'password':'123','current_password':'parent-password'}
            self.assertEqual(self.parent.call('password',body)[0],400)
        self.assertEqual(self.parent.call('password',{'user':2,'password':'abcd'})[0],200)
        self.assertEqual(Client(self.app).call('login',{'username':'alex','password':'abcd'})[0],200)
        self.assertEqual(self.parent.call('password',{'user':1,'password':'abcd','current_password':'parent-password'})[0],200)
        self.assertEqual(Client(self.app).call('login',{'username':'parent','password':'abcd'})[0],200)

    def test_first_parent_accepts_four_character_password(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()/'work'/'test-data') as folder:
            app=Application(folder)
            client=Client(app)
            body={'code':app.setup_code,'name':'Parent','username':'parent','password':'123'}
            self.assertEqual(client.call('setup',body)[0],400)
            body['password']='1234'
            self.assertEqual(client.call('setup',body)[0],200)

    def test_rate_limit(self):
        client=Client(self.app)
        for _ in range(10):self.assertEqual(client.call('login',{'username':'missing','password':'bad'},{'REMOTE_ADDR':'10.0.0.2'})[0],401)
        self.assertEqual(client.call('login',{'username':'missing','password':'bad'},{'REMOTE_ADDR':'10.0.0.2'})[0],429)
    def test_concurrent_completion_is_unique(self):
        rid=self.create()
        def tap(_):
            client=Client(self.app);client.cookie=self.child.cookie;client.csrf=self.child.csrf
            return client.call('complete',{'routine':rid,'done':True})[0]
        with ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(list(pool.map(tap,range(8))),[200]*8)
        self.assertEqual(self.profile()['progress']['xp'],10)
    def test_levels(self):
        for i in range(10):self.child.call('complete',{'routine':self.create(title=f'Step {i}'),'done':True})
        self.assertEqual(self.profile()['progress']['level'],2)
        self.assertEqual(self.profile()['progress']['level_progress'],0)

if __name__=='__main__':unittest.main()
