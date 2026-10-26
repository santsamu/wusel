import unittest,json
from pathlib import Path
from datetime import date
import test_app as app_tests
from app import Application,TASK_ICONS
from test_app import Client

class TaskIconTests(unittest.TestCase):
    setUp=app_tests.GardenTests.setUp
    tearDown=app_tests.GardenTests.tearDown
    def body(self,**extra):return {'child':2,'title':'Task','description':'','time':'07:00','days':list(range(7)),**extra}
    def test_frontend_and_backend_icon_choices_match(self):
        import ast
        source=(Path(__file__).resolve().parents[1]/'wusel'/'static'/'app.js').read_text(encoding='utf-8')
        choices=ast.literal_eval(source.split('const taskIcons=',1)[1].split(';',1)[0])
        self.assertEqual([choice[0] for choice in choices],list(TASK_ICONS[1:]))

    def test_default_and_every_allowed_icon_including_medicine(self):
        self.assertEqual(self.parent.call('routines',self.body())[0],200)
        self.assertEqual(self.child.call('state')[1]['children'][0]['routines'][0]['icon'],'')
        for icon in TASK_ICONS:
            self.assertEqual(self.parent.call('routines',self.body(id=1,icon=icon))[0],200)
            self.assertEqual(self.child.call('state')[1]['children'][0]['routines'][0]['icon'],icon)
        self.assertIn('medicine',TASK_ICONS)
    def test_invalid_values_are_atomic_and_child_cannot_edit(self):
        self.parent.call('routines',self.body(icon='tooth'))
        for value in ['<img src=x>','💊','unknown',None,[],{}]:
            self.assertEqual(self.parent.call('routines',self.body(id=1,icon=value))[0],400)
        self.assertEqual(self.child.call('routines',self.body(id=1,icon='medicine'))[0],403)
        self.assertEqual(self.child.call('state')[1]['children'][0]['routines'][0]['icon'],'tooth')
    def test_edit_tomorrow_keeps_today_and_persists_on_activation(self):
        self.parent.call('routines',self.body(icon='tooth'))
        self.parent.call('routines',self.body(id=1,icon='medicine',apply_from='tomorrow'))
        c=self.child.call('state')[1]['children'][0]
        self.assertEqual(c['routines'][0]['icon'],'tooth');self.assertEqual(c['planned_routines'][0]['icon'],'medicine')
        app=Application(self.temp.name);app.today=lambda:date(2026,10,27)
        client=Client(app);client.cookie=self.child.cookie
        self.assertEqual(client.call('state')[1]['children'][0]['routines'][0]['icon'],'medicine')
    def test_old_client_edit_does_not_erase_icon_and_reset_keeps_it(self):
        self.parent.call('routines',self.body(icon='medicine'))
        self.parent.call('routines',self.body(id=1,title='New title'))
        self.assertEqual(self.parent.call('state')[1]['children'][0]['routines'][0]['icon'],'medicine')
        self.parent.call('reset-child',{'child':2,'confirmation':'alex','current_password':'parent-password'})
        self.assertEqual(self.parent.call('state')[1]['children'][0]['routines'][0]['icon'],'medicine')
        self.assertEqual(self.parent.call('routines',self.body(id=1,icon=''))[0],200)
        self.assertEqual(self.parent.call('state')[1]['children'][0]['routines'][0]['icon'],'')
    def test_legacy_upgrade_keeps_tasks_points_and_old_pending_edits(self):
        self.parent.call('routines',self.body())
        self.child.call('complete',{'routine':1,'done':True})
        self.parent.call('routines',self.body(id=1,title='Future',apply_from='tomorrow'))
        with self.app.connect() as db:
            data=json.loads(db.execute('SELECT payload FROM pending_routines').fetchone()[0]);data.pop('icon')
            db.execute('UPDATE pending_routines SET payload=?',(json.dumps(data),))
            db.execute('ALTER TABLE routines DROP COLUMN icon')
        app=Application(self.temp.name);app.today=self.app.today
        client=Client(app);client.cookie=self.parent.cookie
        c=client.call('state')[1]['children'][0]
        self.assertEqual(c['routines'][0]['icon'],'');self.assertEqual(c['progress']['xp'],10)
        app.today=lambda:date(2026,10,27)
        c=client.call('state')[1]['children'][0]
        self.assertEqual(c['routines'][0]['title'],'Future');self.assertEqual(c['routines'][0]['icon'],'')

if __name__=='__main__':unittest.main()
