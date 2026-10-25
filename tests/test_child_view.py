import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application
from test_app import Client

class ChildViewTests(unittest.TestCase):
    def setUp(self):
        folder=Path.cwd()/'work'/'test-data';folder.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=folder)
        self.app=Application(self.temp.name)
        self.parent=Client(self.app)
        self.parent.call('setup',{'name':'Parent','username':'parent','password':'parent-password','code':self.app.setup_code});self.parent.call('state')
        for name in ('alex','sam'):
            self.parent.call('users',{'name':name,'username':name,'password':'child-pass','role':'child'})
        self.child=Client(self.app);self.child.call('login',{'username':'alex','password':'child-pass'});self.child.call('state')
    def tearDown(self):self.temp.cleanup()
    def test_default_and_parent_choice_persist(self):
        self.assertEqual(self.child.call('state')[1]['children'][0]['day_view'],'focus')
        self.assertEqual(self.parent.call('child-settings',{'child':2,'day_view':'checklist'})[0],200)
        self.assertEqual(self.child.call('state')[1]['children'][0]['day_view'],'checklist')
        with self.app.connect() as db:self.assertEqual(db.execute('SELECT day_view FROM users WHERE id=3').fetchone()[0],'focus')
        app=Application(self.temp.name);client=Client(app);client.cookie=self.child.cookie
        self.assertEqual(client.call('state')[1]['children'][0]['day_view'],'checklist')
    def test_children_cannot_change_defaults(self):
        self.assertEqual(self.child.call('child-settings',{'child':2,'day_view':'checklist'})[0],403)
        self.assertEqual(self.child.call('child-settings',{'child':3,'day_view':'checklist'})[0],403)
        self.assertEqual(Client(self.app).call('child-settings',{'child':2,'day_view':'checklist'})[0],401)
    def test_validation_and_csrf(self):
        self.assertEqual(self.parent.call('child-settings',{'child':2,'day_view':'other'})[0],400)
        self.assertEqual(self.parent.call('child-settings',{'child':1,'day_view':'focus'})[0],404)
        self.assertEqual(self.parent.call('child-settings',{'child':2,'day_view':'focus'},{'HTTP_X_CSRF_TOKEN':''})[0],403)
    def test_previous_database_migrates_with_progress_untouched(self):
        with self.app.connect() as db:
            db.execute('ALTER TABLE users DROP COLUMN day_view')
        app=Application(self.temp.name)
        with app.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT day_view FROM users WHERE id=2').fetchone()[0],'focus')

if __name__=='__main__':unittest.main()
