import unittest,json
from datetime import date
import test_app as app_tests
from app import Application
from test_app import Client

class ChildSupportTests(unittest.TestCase):
    setUp=app_tests.WuselTests.setUp
    tearDown=app_tests.WuselTests.tearDown
    def task(self,**extra):
        body={'child':2,'title':'Task','description':'Ask together','first_action':'Pick up your toothbrush','time':'07:00','days':list(range(7)),**extra}
        self.assertEqual(self.parent.call('routines',body)[0],200)
        with self.app.connect() as db:return db.execute('SELECT MAX(id) FROM routines').fetchone()[0]
    def profile(self,client=None):return (client or self.child).call('state')[1]['children'][0]
    def settings(self,**extra):return self.parent.call('child-settings',{'child':2,**extra})
    def defer(self,rid,**extra):return self.child.call('defer',{'routine':rid,'day':'2026-10-26',**extra})
    def test_first_action_timing_validation_and_legacy_edit(self):
        rid=self.task()
        self.task(id=rid,first_action='Get your cup',apply_from='tomorrow')
        p=self.profile();self.assertEqual(p['routines'][0]['first_action'],'Pick up your toothbrush');self.assertEqual(p['planned_routines'][0]['first_action'],'Get your cup')
        self.assertEqual(self.parent.call('routines',{'id':rid,'child':2,'title':'Updated','description':'','time':'07:00','days':[0]})[0],200)
        self.assertEqual(self.profile()['routines'][0]['first_action'],'Pick up your toothbrush')
        body={'id':rid,'child':2,'title':'Updated','description':'','time':'07:00','days':[0],'first_action':'x'*161}
        self.assertEqual(self.parent.call('routines',body)[0],400)
    def test_first_action_scheduled_change_survives_restart(self):
        rid=self.task();self.task(id=rid,first_action='Get your cup',apply_from='tomorrow')
        restarted=Application(self.temp.name);restarted.today=lambda:date(2026,10,27)
        client=Client(restarted);client.cookie=self.child.cookie
        self.assertEqual(self.profile(client)['routines'][0]['first_action'],'Get your cup')

    def test_deferral_is_unfinished_persistent_order_for_today_only(self):
        for i in range(3):self.task(time=f'0{7+i}:00')
        self.assertEqual(self.defer(1)[0],200)
        self.assertEqual([r['id'] for r in self.profile()['routines']],[2,3,1])
        self.assertEqual(self.defer(2)[0],200)
        self.assertEqual([r['id'] for r in self.profile()['routines']],[3,1,2])
        self.assertEqual(self.profile()['progress']['xp'],0);self.assertFalse(any(r['done'] for r in self.profile()['routines']))
        restarted=Application(self.temp.name);restarted.today=self.app.today;client=Client(restarted);client.cookie=self.child.cookie
        self.assertEqual([r['id'] for r in self.profile(client)['routines']],[3,1,2])
        restarted.today=lambda:date(2026,10,27)
        self.assertEqual([r['id'] for r in self.profile(client)['routines']],[1,2,3])
    def test_deferral_permissions_completed_locked_stale_and_last_step(self):
        first=self.task();second=self.task();other=self.task(child=3)
        self.assertEqual(self.defer(other)[0],404)
        self.assertEqual(self.defer(first,day='2026-10-25')[0],409)
        self.assertEqual(self.child.call('defer',{'routine':first,'day':'2026-10-26'},{'HTTP_X_CSRF_TOKEN':'bad'})[0],403)
        self.child.call('complete',{'routine':first,'done':True})
        self.assertEqual(self.defer(first)[0],409)
        self.assertEqual(self.defer(second)[0],409)
        parent_profile=self.parent.call('state')[1]['children'][0]
        cid=parent_profile['history'][0]['id'];self.parent.call('correct',{'completion':cid})
        code,data=self.defer(first);self.assertEqual(code,403);self.assertEqual(data['error'],'This step is open again. Let’s check it together.')
    def test_support_preferences_are_atomic_parent_only_and_isolated(self):
        self.assertEqual(self.settings(show_series=False,reduced_rewards=True)[0],200)
        p=self.profile();self.assertFalse(p['show_series']);self.assertTrue(p['reduced_rewards'])
        self.assertEqual(self.settings(day_view='checklist')[0],200)
        self.assertFalse(self.profile()['show_series']);self.assertTrue(self.profile()['reduced_rewards'])
        self.assertEqual(self.settings(show_series=True,reduced_rewards='yes')[0],400)
        self.assertFalse(self.profile()['show_series'])
        self.assertEqual(self.child.call('child-settings',{'child':2,'show_series':True})[0],403)
        self.assertEqual(self.parent.call('child-settings',{'child':2,'show_series':True},{'HTTP_X_CSRF_TOKEN':'bad'})[0],403)
        self.assertEqual(self.settings()[0],400)
        with self.app.connect() as db:self.assertEqual(tuple(db.execute('SELECT show_series,reduced_rewards FROM users WHERE id=3').fetchone()),(1,0))
    def test_hidden_series_retains_earned_badges_and_chooses_nonseries_goal(self):
        with self.app.connect() as db:
            db.execute("INSERT INTO badges VALUES(2,'streak3','2026-10-26',0)")
            db.execute("UPDATE users SET badge_goal='streak7' WHERE id=2")
        self.settings(show_series=False)
        p=self.profile();self.assertFalse(p['show_series'])
        goal=next(b for b in p['progress']['badges'] if b['id']==p['progress']['next_badge']);self.assertNotEqual(goal['kind'],'streak')
        self.assertTrue(next(b for b in p['progress']['badges'] if b['id']=='streak3')['earned'])
        self.settings(show_series=True);self.assertTrue(self.profile()['show_series'])
        self.assertTrue(next(b for b in self.profile()['progress']['badges'] if b['id']=='streak3')['earned'])
    def test_settings_persist_and_reset_clears_deferral_but_keeps_guidance(self):
        self.task();self.task();self.defer(1);self.settings(show_series=False,reduced_rewards=True)
        restarted=Application(self.temp.name);restarted.today=self.app.today;client=Client(restarted);client.cookie=self.child.cookie
        p=self.profile(client);self.assertFalse(p['show_series']);self.assertTrue(p['reduced_rewards'])
        self.parent.call('reset-child',{'child':2,'confirmation':'alex','current_password':'parent-password'})
        p=self.parent.call('state')[1]['children'][0];self.assertTrue(p['show_series']);self.assertFalse(p['reduced_rewards'])
        self.assertEqual(p['routines'][0]['first_action'],'Pick up your toothbrush')
        with self.app.connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM deferred_steps WHERE child=2').fetchone()[0],0)
    def test_legacy_upgrade_preserves_tasks_and_progress(self):
        rid=self.task();self.child.call('complete',{'routine':rid,'done':True})
        with self.app.connect() as db:
            db.execute('DROP TABLE deferred_steps');db.execute('ALTER TABLE routines DROP COLUMN first_action')
            db.execute('ALTER TABLE users DROP COLUMN show_series');db.execute('ALTER TABLE users DROP COLUMN reduced_rewards')
        restarted=Application(self.temp.name);restarted.today=self.app.today;client=Client(restarted);client.cookie=self.child.cookie
        p=self.profile(client);self.assertEqual(p['progress']['xp'],10);self.assertEqual(p['routines'][0]['first_action'],'')
        self.assertTrue(p['show_series']);self.assertFalse(p['reduced_rewards'])

if __name__=='__main__':unittest.main()
