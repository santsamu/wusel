import unittest
from pathlib import Path
import test_app as base
from app import Application

class ChildUndoTests(unittest.TestCase):
    setUp=base.WuselTests.setUp
    tearDown=base.WuselTests.tearDown
    create=base.WuselTests.create
    profile=base.WuselTests.profile

    def start(self):
        self.clock=self.app.now()
        self.app.now=lambda:self.clock
        rid=self.create()
        status,payload=self.child.call('complete',{'routine':rid,'done':True})
        self.assertEqual(status,200);self.assertEqual(payload['undo_seconds'],15)
        return rid

    def test_undo_before_deadline_and_recheck_without_extra_points(self):
        rid=self.start();self.clock+=14.999
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':False})[0],200)
        self.assertEqual(self.profile()['progress']['xp'],0)
        status,data=self.child.call('complete',{'routine':rid,'done':True})
        self.assertEqual(status,200);self.assertEqual(data['earned_points'],0)
        self.assertEqual(data['undo_seconds'],15)
        self.assertEqual(self.profile()['progress']['xp'],10)

    def test_deadline_is_enforced_at_15_seconds(self):
        rid=self.start();self.clock+=15
        self.assertEqual(self.profile()['routines'][0]['undo_seconds'],0)
        status,data=self.child.call('complete',{'routine':rid,'done':False})
        self.assertEqual(status,403);self.assertIn('Ask a parent',data['error'])
        self.assertTrue(self.profile()['routines'][0]['done'])
        self.assertEqual(self.profile()['progress']['xp'],10)

    def test_duplicate_checks_do_not_extend_deadline(self):
        rid=self.start();self.clock+=10
        status,data=self.child.call('complete',{'routine':rid,'done':True})
        self.assertEqual(status,200);self.assertEqual(data['undo_seconds'],5)
        self.clock+=5
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':False})[0],403)

    def test_restart_and_another_session_keep_original_deadline(self):
        rid=self.start();self.clock+=7
        restarted=Application(self.temp.name);restarted.today=self.app.today;restarted.now=lambda:self.clock
        client=base.Client(restarted);client.cookie=self.child.cookie;client.call('state')
        self.assertEqual(client.call('state')[1]['children'][0]['routines'][0]['undo_seconds'],8)
        self.clock+=8
        self.assertEqual(client.call('complete',{'routine':rid,'done':False})[0],403)

    def test_parent_can_reopen_expired_completion_and_restore(self):
        rid=self.start();self.clock+=60
        self.assertEqual(self.parent.call('complete',{'routine':rid,'done':False})[0],200)
        self.assertTrue(self.profile()['routines'][0]['locked'])
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':True})[0],403)
        cid=self.profile(self.parent)['history'][0]['id']
        self.assertEqual(self.parent.call('correct',{'completion':cid,'restore':True})[0],200)
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':False})[0],403)
        self.assertEqual(self.profile()['progress']['xp'],10)

    def test_parent_marked_completion_has_no_child_undo_window(self):
        rid=self.create()
        self.assertEqual(self.parent.call('complete',{'routine':rid,'done':True})[0],200)
        self.assertEqual(self.profile()['routines'][0]['undo_seconds'],0)
        self.assertEqual(self.child.call('complete',{'routine':rid,'done':False})[0],403)

    def test_old_completions_migrate_without_reopening_or_losing_progress(self):
        rid=self.start()
        with self.app.connect() as db:db.execute('ALTER TABLE completions DROP COLUMN undo_until')
        restarted=Application(self.temp.name);restarted.today=self.app.today
        client=base.Client(restarted);client.cookie=self.child.cookie;client.call('state')
        profile=client.call('state')[1]['children'][0]
        self.assertEqual(profile['progress']['xp'],10)
        self.assertEqual(profile['routines'][0]['undo_seconds'],0)
        self.assertEqual(client.call('complete',{'routine':rid,'done':False})[0],403)

if __name__=='__main__':unittest.main()
