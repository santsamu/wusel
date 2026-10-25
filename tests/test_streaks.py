import json,tempfile,unittest,sys
from datetime import date,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application,ALL_BADGES

class StreakTests(unittest.TestCase):
    def setUp(self):
        scratch=Path.cwd()/'work'/'test-data';scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.app=Application(self.temp.name)
        self.day=date(2026,12,28);self.app.today=lambda:self.day
        with self.app.connect() as db:
            db.execute("INSERT INTO users(id,name,username,password,role) VALUES(1,'Alex','alex','unused','child')")
            db.execute("INSERT INTO users(id,name,username,password,role) VALUES(2,'Sam','sam','unused','child')")
            for rid in [1,2]:
                db.execute("INSERT INTO routines(id,child,title,time,days,specific_date) VALUES(?,1,'Task','07:00',?,'')",(rid,json.dumps(list(range(7)))))
    def tearDown(self):self.temp.cleanup()
    def progress(self):
        with self.app.connect() as db:return self.app.progress(db,1)
    def complete(self,rid=1):
        with self.app.connect() as db:
            db.execute("INSERT OR REPLACE INTO completions(routine,child,day,title) VALUES(?,1,?,'Task')",(rid,self.day.isoformat()))
    def full_day(self):
        self.complete(1);self.complete(2);return self.progress()
    def badge(self,progress,key):return next(b for b in progress['badges'] if b['id']==key)
    def test_partial_empty_and_missing_days_do_not_count(self):
        self.complete();self.assertEqual(self.progress()['full_days'],0)
        self.full_day();self.day+=timedelta(days=2)
        p=self.full_day();self.assertEqual(p['full_days'],2);self.assertEqual(p['best_streak'],1)
        with self.app.connect() as db:db.execute('UPDATE routines SET archived=1')
        self.day+=timedelta(days=1);p=self.progress();self.assertEqual(p['full_days'],2)
        self.day+=timedelta(days=1);self.assertEqual(self.progress()['current_streak'],0)
    def test_series_crosses_year_and_today_can_still_be_incomplete(self):
        for _ in range(7):p=self.full_day();self.day+=timedelta(days=1)
        self.assertEqual(p['best_streak'],7);self.assertTrue(self.badge(p,'streak7')['earned'])
        self.assertEqual(self.progress()['current_streak'],7)
        self.day+=timedelta(days=1);self.assertEqual(self.progress()['current_streak'],0)
    def test_correction_recalculates_series_but_preserves_badges_and_revocation(self):
        first=self.day
        for _ in range(3):self.full_day();self.day+=timedelta(days=1)
        with self.app.connect() as db:
            db.execute('UPDATE completions SET voided=1,locked=1 WHERE day=? AND routine=1',((first+timedelta(days=1)).isoformat(),))
            db.execute("UPDATE badges SET revoked=1 WHERE child=1 AND badge='streak3'")
        p=self.progress();self.assertEqual(p['best_streak'],1);self.assertEqual(p['full_days'],2)
        self.assertTrue(self.badge(p,'streak3')['earned']);self.assertTrue(self.badge(p,'streak3')['revoked'])
        with self.app.connect() as db:db.execute('UPDATE completions SET voided=0,locked=0')
        p=self.progress();self.assertEqual(p['best_streak'],3);self.assertTrue(self.badge(p,'streak3')['revoked'])
    def test_history_survives_schedule_edits_archive_and_restart(self):
        self.full_day();self.day+=timedelta(days=1)
        with self.app.connect() as db:db.execute("UPDATE routines SET archived=1,days='[]'")
        restarted=Application(self.temp.name);restarted.today=lambda:self.day;self.app=restarted
        self.assertEqual(self.progress()['full_days'],1)
        with self.app.connect() as db:self.assertEqual(self.app.progress(db,2)['full_days'],0)
    def test_new_step_badges_backfill_without_inventing_past_full_days(self):
        with self.app.connect() as db:
            for n in range(10):db.execute("INSERT INTO completions(routine,child,day,title) VALUES(1,1,?,'Task')",((self.day-timedelta(days=n+1)).isoformat(),))
        p=self.progress();self.assertTrue(self.badge(p,'ten')['earned']);self.assertEqual(p['full_days'],0)
        self.assertEqual(len(p['badges']),17);self.assertEqual(len({b[0] for b,_ in ALL_BADGES}),17)
    def test_all_full_day_and_streak_thresholds(self):
        for n in range(1,31):
            p=self.full_day()
            for key,threshold in [('day1',1),('day10',10),('day30',30),('streak3',3),('streak7',7),('streak14',14),('streak30',30)]:
                self.assertEqual(bool(self.badge(p,key)['earned']),n>=threshold,(key,n))
            self.day+=timedelta(days=1)
        self.assertEqual(p['best_streak'],30)

    def test_repeated_checks_do_not_duplicate_day_awards(self):
        self.full_day();p=self.progress();self.assertEqual(p['full_days'],1)
        with self.app.connect() as db:db.execute('UPDATE completions SET voided=1 WHERE routine=2')
        self.assertEqual(self.progress()['full_days'],0)
        with self.app.connect() as db:db.execute('UPDATE completions SET voided=0')
        self.assertEqual(self.progress()['full_days'],1)

if __name__=='__main__':unittest.main()
