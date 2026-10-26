import unittest,json
from datetime import date
import test_app as app_tests
from test_app import Client
from app import Application

class RoutineTimingTests(unittest.TestCase):
    setUp=app_tests.WuselTests.setUp
    tearDown=app_tests.WuselTests.tearDown
    def create(self,**extra):
        body={'child':2,'title':'Original','description':'Help','time':'07:00','days':list(range(7)),'specific_date':'','apply_from':'today',**extra}
        self.assertEqual(self.parent.call('routines',body)[0],200)
        with self.app.connect() as db:return db.execute('SELECT MAX(id) FROM routines').fetchone()[0]
    def edit(self,rid,**extra):
        return self.parent.call('routines',{'id':rid,'child':2,'title':'Changed','description':'New help','time':'09:00','days':list(range(7)),'specific_date':'','apply_from':'tomorrow',**extra})
    def profile(self,client=None):return (client or self.parent).call('state')[1]['children'][0]
    def plan(self):
        with self.app.connect() as db:return json.loads(db.execute('SELECT routines FROM daily_plans WHERE child=2 AND day=?',(self.app.today().isoformat(),)).fetchone()[0])
    def test_tomorrow_edit_preserves_today_and_survives_restart(self):
        rid=self.create();self.assertEqual(self.edit(rid)[0],200)
        p=self.profile();self.assertEqual(p['routines'][0]['title'],'Original');self.assertEqual(p['planned_routines'][0]['title'],'Changed')
        restarted=Application(self.temp.name);restarted.today=lambda:date(2026,10,27)
        client=Client(restarted);client.cookie=self.parent.cookie
        p=self.profile(client);self.assertEqual(p['routines'][0]['title'],'Changed');self.assertEqual(p['routines'][0]['time'],'09:00')
        self.assertNotIn('effective_on',p['planned_routines'][0])
    def test_tomorrow_archive_preserves_unfinished_today(self):
        first=self.create();second=self.create(title='Second')
        self.child.call('complete',{'routine':first,'done':True})
        self.assertEqual(self.parent.call('archive',{'routine':second,'apply_from':'tomorrow'})[0],200)
        self.assertEqual(self.plan(),[first,second]);self.assertEqual(self.profile()['progress']['full_days'],0)
        self.assertEqual(self.child.call('complete',{'routine':second,'done':True})[0],200)
        self.assertEqual(self.profile()['progress']['full_days'],1)
        self.app.today=lambda:date(2026,10,27)
        p=self.profile();self.assertEqual([r['id'] for r in p['routines']],[first]);self.assertEqual(p['progress']['full_days'],1)
    def test_apply_today_intentionally_changes_target_and_retains_earned_badges(self):
        first=self.create();second=self.create(title='Second')
        self.child.call('complete',{'routine':first,'done':True})
        self.assertEqual(self.parent.call('archive',{'routine':second,'apply_from':'today'})[0],200)
        self.assertEqual(self.plan(),[first]);self.assertEqual(self.profile()['progress']['full_days'],1)
        third=self.create(title='Third')
        p=self.profile()['progress'];self.assertEqual(p['full_days'],0)
        self.assertTrue(next(b for b in p['badges'] if b['id']=='day1')['earned'])
        self.assertEqual(set(self.plan()),{first,third})
    def test_new_tomorrow_routine_cannot_be_completed_today(self):
        rid=self.create(apply_from='tomorrow')
        self.assertFalse(self.profile()['routines'][0]['scheduled']);self.assertEqual(self.plan(),[])
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],400)
        self.app.today=lambda:date(2026,10,27)
        self.assertTrue(self.profile()['routines'][0]['scheduled'])
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],200)
    def test_immediate_edit_replaces_pending_and_updates_today(self):
        rid=self.create();self.edit(rid)
        self.assertEqual(self.edit(rid,title='Immediate',apply_from='today')[0],200)
        self.assertEqual(self.profile()['routines'][0]['title'],'Immediate')
        self.app.today=lambda:date(2026,10,27)
        self.assertEqual(self.profile()['routines'][0]['title'],'Immediate')
    def test_invalid_timing_and_child_writes_are_rejected(self):
        rid=self.create()
        self.assertEqual(self.edit(rid,apply_from='invalid')[0],400)
        self.assertEqual(self.parent.call('archive',{'routine':rid,'apply_from':'invalid'})[0],400)
        self.assertEqual(self.child.call('archive',{'routine':rid,'apply_from':'tomorrow'})[0],403)
        self.assertEqual(self.profile()['routines'][0]['title'],'Original')
    def test_upgrade_retains_legacy_routines_progress_and_sessions(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        with self.app.connect() as db:
            db.execute('DROP TABLE pending_routines')
            db.execute('ALTER TABLE routines DROP COLUMN starts_on')
        restarted=Application(self.temp.name);restarted.today=self.app.today
        self.parent.app=restarted;self.child.app=restarted;self.app=restarted
        p=self.profile();self.assertEqual(p['routines'][0]['id'],rid)
        self.assertEqual(p['progress']['xp'],10);self.assertEqual(p['progress']['full_days'],1)
        self.assertEqual(self.edit(rid)[0],200)
        self.assertEqual(self.profile()['routines'][0]['title'],'Original')

    def test_badge_progress_has_the_right_unit(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        p=self.profile()['progress'];badges={b['id']:b for b in p['badges']}
        self.assertEqual(badges['ten']['value'],1);self.assertEqual(badges['day10']['value'],1);self.assertEqual(badges['streak3']['value'],1)
        self.app.today=lambda:date(2026,10,29)
        self.assertEqual(next(b for b in self.profile()['progress']['badges'] if b['id']=='streak3')['value'],0)

if __name__=='__main__':unittest.main()
