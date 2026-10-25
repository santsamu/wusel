import unittest
from pathlib import Path
import test_app as app_tests
from test_app import Client
from app import Application

class ChildResetTests(unittest.TestCase):
    setUp=app_tests.GardenTests.setUp
    tearDown=app_tests.GardenTests.tearDown
    def seed(self):
        for name in ['First','Archived']:
            self.parent.call('routines',{'child':2,'title':name,'description':'Keep me','time':'07:00','days':[0,1,2,3,4,5,6]})
        self.child.call('complete',{'routine':1,'done':True});self.child.call('complete',{'routine':2,'done':True})
        self.parent.call('archive',{'routine':2,'apply_from':'today'})
        self.parent.call('routines',{'id':1,'child':2,'title':'Tomorrow','description':'Future guidance','time':'08:00','days':[0,1,2,3,4,5,6],'apply_from':'tomorrow'})
        self.child.call('preferences',{'language':'de','theme':'petrol'})
        self.parent.call('child-settings',{'child':2,'day_view':'checklist'})
        self.parent.call('preferences',{'language':'en','theme':'berry'})
        self.parent.call('routines',{'child':3,'title':'Other child','description':'','time':'07:00','days':[0]})
        self.parent.call('complete',{'routine':3,'done':True})
    def reset(self,**extra):return self.parent.call('reset-child',{'child':2,'confirmation':'alex','current_password':'parent-password',**extra})
    def test_reset_preserves_all_tasks_and_credentials_and_isolates_accounts(self):
        self.seed()
        with self.app.connect() as db:
            routines=[tuple(r) for r in db.execute('SELECT * FROM routines ORDER BY id')]
            pending=[tuple(r) for r in db.execute('SELECT * FROM pending_routines')]
            identity=tuple(db.execute('SELECT id,name,username,password,role FROM users WHERE id=2').fetchone())
            other=[tuple(r) for r in db.execute('SELECT * FROM completions WHERE child=3')]
        self.assertEqual(self.reset()[0],200)
        with self.app.connect() as db:
            for table in ['completions','badges','daily_plans']:self.assertEqual(db.execute('SELECT COUNT(*) FROM '+table+' WHERE child=2').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sessions WHERE user=2').fetchone()[0],0)
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM routines ORDER BY id')],routines)
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM pending_routines')],pending)
            self.assertEqual(tuple(db.execute('SELECT id,name,username,password,role FROM users WHERE id=2').fetchone()),identity)
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM completions WHERE child=3')],other)
            self.assertEqual(tuple(db.execute('SELECT language,theme,day_view FROM users WHERE id=2').fetchone()),('','forest','focus'))
            self.assertTrue(db.execute("SELECT 1 FROM audit WHERE action='reset'").fetchone())
        self.assertIsNone(self.child.call('state')[1]['user'])
        self.assertEqual(self.child.call('complete',{'routine':1,'done':True})[0],401)
        self.assertEqual(self.child.call('login',{'username':'alex','password':'child-pass'})[0],200)
        p=self.child.call('state')[1]['children'][0]['progress']
        self.assertEqual((p['xp'],p['level'],p['full_days'],p['best_streak']),(0,1,0,0))
        self.assertFalse(any(b['earned'] for b in p['badges']))
        self.assertEqual(self.parent.call('state')[1]['user']['theme'],'berry')
        self.assertEqual(self.child.call('complete',{'routine':1,'done':True})[1]['earned_points'],10)
    def test_bad_confirmation_and_password_do_not_delete_anything(self):
        self.seed()
        for extra,status in [({'confirmation':'sam'},400),({'confirmation':''},400),({'current_password':'wrong'},403)]:
            self.assertEqual(self.reset(**extra)[0],status)
            with self.app.connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM completions WHERE child=2').fetchone()[0],2)
        self.assertIsNotNone(self.child.call('state')[1]['user'])
    def test_only_parents_with_csrf_can_reset_children(self):
        body={'child':2,'confirmation':'alex','current_password':'parent-password'}
        self.assertEqual(Client(self.app).call('reset-child',body)[0],401)
        self.assertEqual(self.child.call('reset-child',body)[0],403)
        self.assertEqual(self.parent.call('reset-child',body,{'HTTP_X_CSRF_TOKEN':'bad'})[0],403)
        self.assertEqual(self.reset(child=1,confirmation='parent')[0],404)
        self.assertEqual(self.reset(child=999)[0],404)
    def test_reset_is_idempotent_and_survives_restart(self):
        self.seed();self.assertEqual(self.reset()[0],200);self.assertEqual(self.reset()[0],200)
        restarted=Application(self.temp.name);restarted.today=self.app.today
        client=Client(restarted);client.call('login',{'username':'alex','password':'child-pass'})
        p=client.call('state')[1]['children'][0]['progress'];self.assertEqual(p['count'],0);self.assertEqual(p['current_streak'],0)
        self.assertFalse(any(b['earned'] for b in p['badges']))

if __name__=='__main__':unittest.main()
