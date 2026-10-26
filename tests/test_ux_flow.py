import unittest
from datetime import date,timedelta
import test_streaks as streak_tests
import test_app as app_tests
from app import Application

class RestSeriesTests(unittest.TestCase):
    setUp=streak_tests.StreakTests.setUp
    tearDown=streak_tests.StreakTests.tearDown
    progress=streak_tests.StreakTests.progress
    full_day=streak_tests.StreakTests.full_day
    complete=streak_tests.StreakTests.complete
    badge=streak_tests.StreakTests.badge
    def pause(self,day):
        with self.app.connect() as db:db.execute('INSERT OR IGNORE INTO rest_days VALUES(1,?)',(day.isoformat(),))
    def test_rest_days_bridge_without_counting_as_full_days(self):
        self.full_day();self.day+=timedelta(days=1);self.pause(self.day)
        p=self.full_day();self.assertEqual(p['full_days'],1);self.assertEqual(p['best_streak'],1)
        self.day+=timedelta(days=1);p=self.full_day();self.assertEqual(p['full_days'],2);self.assertEqual(p['best_streak'],2)
        self.day+=timedelta(days=2);p=self.full_day();self.assertEqual(p['best_streak'],2);self.assertEqual(p['current_streak'],1)
    def test_long_break_preserves_current_series_only_if_every_day_is_planned(self):
        self.full_day()
        for _ in range(4):self.day+=timedelta(days=1);self.pause(self.day)
        self.assertEqual(self.progress()['current_streak'],1)
        self.day+=timedelta(days=1);self.assertEqual(self.progress()['current_streak'],1)
        self.day+=timedelta(days=1);self.assertEqual(self.progress()['current_streak'],0)
    def test_goal_is_stable_when_progress_changes_and_across_restart(self):
        with self.app.connect() as db:db.execute("UPDATE users SET badge_goal='streak3' WHERE id=1")
        self.full_day();self.day+=timedelta(days=3)
        p=self.progress();self.assertEqual(p['next_badge'],'streak3');self.assertEqual(self.badge(p,'streak3')['value'],0)
        restarted=Application(self.temp.name);restarted.today=lambda:self.day;self.app=restarted
        self.assertEqual(self.progress()['next_badge'],'streak3')
    def test_upgrade_keeps_progress_while_adding_rest_days_and_goal(self):
        self.full_day()
        with self.app.connect() as db:
            db.execute('DROP TABLE rest_days')
            db.execute('ALTER TABLE users DROP COLUMN badge_goal')
        restarted=Application(self.temp.name);restarted.today=lambda:self.day;self.app=restarted
        p=self.progress();self.assertEqual(p['xp'],20);self.assertEqual(p['full_days'],1)
        self.assertTrue(self.badge(p,'first')['earned']);self.assertTrue(p['next_badge'])

    def test_earned_goal_advances_and_revoked_badges_are_not_goals(self):
        p=self.progress();self.assertEqual(p['next_badge'],'first')
        self.complete();p=self.progress();self.assertNotEqual(p['next_badge'],'first')
        with self.app.connect() as db:db.execute("UPDATE badges SET revoked=1 WHERE badge='first'")
        self.assertNotEqual(self.progress()['next_badge'],'first')

class RestApiTests(unittest.TestCase):
    setUp=app_tests.WuselTests.setUp
    tearDown=app_tests.WuselTests.tearDown
    def body(self,**extra):return {'child':2,'start':'2026-10-26','end':'2026-10-28',**extra}
    def test_rest_range_add_remove_isolation_and_permissions(self):
        self.assertEqual(self.child.call('rest-days',self.body())[0],403)
        self.assertEqual(self.parent.call('rest-days',self.body(),{'HTTP_X_CSRF_TOKEN':'bad'})[0],403)
        self.assertEqual(self.parent.call('rest-days',self.body())[0],200)
        p=self.parent.call('state')[1]['children'];self.assertTrue(p[0]['rest_day']);self.assertEqual(len(p[0]['rest_days']),3);self.assertFalse(p[1]['rest_day'])
        self.assertEqual(self.parent.call('rest-days',self.body(remove=True))[0],200)
        self.assertFalse(self.child.call('state')[1]['children'][0]['rest_day'])
    def test_invalid_and_past_ranges_do_not_change_history(self):
        for extra in [{'start':'2026-10-25'},{'end':'2026-10-24'},{'end':'2028-01-01'},{'start':None},{'remove':'yes'}]:
            self.assertEqual(self.parent.call('rest-days',self.body(**extra))[0],400)
        self.assertEqual(self.child.call('state')[1]['children'][0]['rest_days'],[])
    def test_reset_clears_pauses_and_goal(self):
        self.parent.call('rest-days',self.body())
        self.assertEqual(self.parent.call('reset-child',{'child':2,'confirmation':'alex','current_password':'parent-password'})[0],200)
        with self.app.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM rest_days WHERE child=2').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT badge_goal FROM users WHERE id=2').fetchone()[0],'')
    def test_completion_from_stale_day_is_rejected(self):
        self.parent.call('routines',{'child':2,'title':'Task','description':'','time':'07:00','days':[0]})
        self.assertEqual(self.child.call('complete',{'routine':1,'done':True,'day':'2026-10-25'})[0],409)
        self.assertEqual(self.child.call('state')[1]['children'][0]['progress']['xp'],0)
        self.assertEqual(self.child.call('complete',{'routine':1,'done':True,'day':'2026-10-26'})[0],200)

if __name__=='__main__':unittest.main()
