import unittest
from unittest.mock import patch
from datetime import timedelta
import test_app as base
from app import Application

class LiveUpdateTests(unittest.TestCase):
    setUp=base.WuselTests.setUp
    tearDown=base.WuselTests.tearDown
    create=base.WuselTests.create
    profile=base.WuselTests.profile
    def marker(self,client=None):
        status,data=(client or self.child).call('updates')
        self.assertEqual(status,200)
        return data

    def test_markers_are_authenticated_and_child_scoped(self):
        self.assertEqual(base.Client(self.app).call('updates')[0],401)
        before=self.marker();family=self.marker(self.parent)
        self.create(child=3)
        self.assertEqual(self.marker(),before)
        self.assertGreater(self.marker(self.parent)['revision'],family['revision'])
        self.create(child=2)
        self.assertGreater(self.marker()['revision'],before['revision'])
        self.assertEqual(set(self.marker()),{'revision','day','timezone'})
        self.assertEqual(self.child.call('updates',extra={'QUERY_STRING':'child=3'})[1],self.marker())

    def test_polling_is_a_read_only_fast_path(self):
        before=self.marker()
        with patch.object(self.app,'activate_pending',side_effect=AssertionError('pending work')), \
             patch.object(self.app,'state',side_effect=AssertionError('state work')), \
             patch.object(self.app.weather,'get',side_effect=AssertionError('weather work')):
            for _ in range(3):self.assertEqual(self.marker(),before)

    def test_committed_corrections_and_children_update_parent_and_child_markers(self):
        rid=self.create();self.child.call('state');before=self.marker();family=self.marker(self.parent)
        self.child.call('complete',{'routine':rid,'done':True})
        self.assertGreater(self.marker()['revision'],before['revision'])
        self.assertGreater(self.marker(self.parent)['revision'],family['revision'])
        for done in [False,True]:
            before=self.marker()
            self.assertEqual(self.parent.call('complete',{'routine':rid,'done':done})[0],200)
            self.assertGreater(self.marker()['revision'],before['revision'])
        snapshot=self.child.call('state')[1]
        self.assertEqual(snapshot['revision'],self.marker()['revision'])

    def test_failed_writes_and_rollback_do_not_publish_changes(self):
        rid=self.create();before=self.marker();family=self.marker(self.parent)
        self.assertEqual(self.parent.call('routines',{'child':2,'title':''})[0],400)
        with self.assertRaises(RuntimeError):
            with self.app.connect() as db:
                db.execute('UPDATE routines SET title=? WHERE id=?',('Discarded',rid))
                raise RuntimeError('rollback')
        self.assertEqual(self.marker(),before);self.assertEqual(self.marker(self.parent),family)

    def test_day_change_is_detected_without_activating_pending_edits_in_poll(self):
        rid=self.create();self.parent.call('routines',{'id':rid,'child':2,'title':'Tomorrow','description':'','time':'07:00','days':[0,1,2,3,4],'apply_from':'tomorrow'})
        before=self.marker();day=self.app.today()+timedelta(days=1);self.app.today=lambda:day
        changed=self.marker();self.assertNotEqual(changed['day'],before['day'])
        with self.app.connect() as db:self.assertEqual(db.execute('SELECT title FROM routines WHERE id=?',(rid,)).fetchone()[0],'Brush teeth')
        snapshot=self.child.call('state')[1]
        self.assertEqual(snapshot['children'][0]['routines'][0]['title'],'Tomorrow')
        self.assertEqual(snapshot['revision'],self.marker()['revision'])
        self.assertGreater(snapshot['revision'],changed['revision'])

    def test_preferences_rest_badges_and_reset_notify_then_expire_child_session(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        actions=[('child-settings',{'child':2,'plain_icons':True}),('rest-days',{'child':2,'start':self.app.today().isoformat(),'end':self.app.today().isoformat()}),('badge',{'child':2,'badge':'first','revoked':True})]
        for endpoint,body in actions:
            before=self.marker();self.assertEqual(self.parent.call(endpoint,body)[0],200)
            self.assertGreater(self.marker()['revision'],before['revision'])
        before=self.marker(self.parent)
        self.assertEqual(self.parent.call('reset-child',{'child':2,'confirmation':'alex','current_password':'parent-password'})[0],200)
        self.assertGreater(self.marker(self.parent)['revision'],before['revision'])
        self.assertEqual(self.child.call('updates')[0],401)

    def test_restart_retains_revisions_and_full_state_does_not_churn(self):
        self.create();self.child.call('state');before=self.marker()
        for _ in range(3):self.child.call('state');self.assertEqual(self.marker(),before)
        restarted=Application(self.temp.name);restarted.today=self.app.today
        client=base.Client(restarted);client.cookie=self.child.cookie
        self.assertEqual(client.call('updates')[1],before)

    def test_existing_installation_migrates_without_losing_progress(self):
        rid=self.create();self.child.call('complete',{'routine':rid,'done':True})
        self.child.call('state')
        with self.app.connect() as db:
            names=[row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'live_%'")]
            for name in names:db.execute('DROP TRIGGER "'+name+'"')
            db.execute('DROP TABLE live_revisions')
        restarted=Application(self.temp.name);restarted.today=self.app.today
        client=base.Client(restarted);client.cookie=self.child.cookie;client.call('state')
        snapshot=client.call('state')[1]
        self.assertEqual(snapshot['children'][0]['progress']['xp'],10)
        self.assertTrue(snapshot['children'][0]['routines'][0]['done'])
        self.assertEqual(snapshot['revision'],client.call('updates')[1]['revision'])

    def test_no_revision_churn_when_all_badges_are_earned(self):
        from app import ALL_BADGES
        with self.app.connect() as db:
            for badge,_ in ALL_BADGES:db.execute('INSERT INTO badges(child,badge,earned) VALUES(2,?,?)',(badge[0],self.app.today().isoformat()))
        self.child.call('state');before=self.marker()
        for _ in range(3):self.child.call('state');self.assertEqual(self.marker(),before)

if __name__=='__main__':unittest.main()
