import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application
from test_app import Client

class ThemeTests(unittest.TestCase):
    def setUp(self):
        folder=Path.cwd()/'work'/'test-data';folder.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=folder);self.app=Application(self.temp.name)
        self.parent=Client(self.app);self.parent.call('setup',{'name':'Parent','username':'parent','password':'parent-password','code':self.app.setup_code});self.parent.call('state')
        self.parent.call('users',{'name':'Alex','username':'alex','password':'child-pass','role':'child'})
        self.child=Client(self.app);self.child.call('login',{'username':'alex','password':'child-pass'});self.child.call('state')
    def tearDown(self):self.temp.cleanup()
    def test_default_and_all_allowed_themes(self):
        self.assertEqual(self.child.call('state')[1]['user']['theme'],'forest')
        for theme in ('forest','ocean','berry','lavender','sunshine','petrol'):
            self.assertEqual(self.child.call('preferences',{'theme':theme})[0],200)
            self.assertEqual(self.child.call('state')[1]['user']['theme'],theme)
    def test_theme_persists_across_login_and_restart(self):
        self.child.call('preferences',{'theme':'petrol'})
        app=Application(self.temp.name);client=Client(app)
        self.assertEqual(client.call('login',{'username':'alex','password':'child-pass'})[0],200)
        self.assertEqual(client.call('state')[1]['user']['theme'],'petrol')
    def test_accounts_cannot_change_each_others_theme(self):
        self.child.call('preferences',{'theme':'berry','user':1})
        self.assertEqual(self.parent.call('state')[1]['user']['theme'],'forest')
        self.parent.call('preferences',{'theme':'sunshine','user':2})
        self.assertEqual(self.child.call('state')[1]['user']['theme'],'berry')
    def test_partial_preferences_preserve_other_settings(self):
        self.child.call('preferences',{'theme':'lavender','language':'de'})
        self.child.call('preferences',{'language':'en'})
        self.assertEqual(self.child.call('state')[1]['user']['theme'],'lavender')
        self.child.call('preferences',{'theme':'berry'})
        self.assertEqual(self.child.call('state')[1]['user']['language'],'en')
    def test_invalid_combination_is_atomic(self):
        for body in ({'theme':'bad','language':'de'},{'theme':'ocean','language':'fr'},{'theme':'<script>'},{'theme':None},{}):
            self.assertEqual(self.child.call('preferences',body)[0],400)
        user=self.child.call('state')[1]['user']
        self.assertEqual(user['theme'],'forest');self.assertEqual(user['language'],'')
    def test_authentication_and_csrf(self):
        self.assertEqual(Client(self.app).call('preferences',{'theme':'berry'})[0],401)
        self.assertEqual(self.child.call('preferences',{'theme':'berry'},{'HTTP_X_CSRF_TOKEN':''})[0],403)
    def test_previous_database_gains_theme_without_data_loss(self):
        self.parent.call('child-settings',{'child':2,'day_view':'checklist'})
        self.child.call('preferences',{'language':'de'})
        with self.app.connect() as db:db.execute('ALTER TABLE users DROP COLUMN theme')
        app=Application(self.temp.name)
        with app.connect() as db:
            row=db.execute('SELECT username,theme,language,day_view FROM users WHERE id=2').fetchone()
            self.assertEqual(tuple(row),('alex','forest','de','checklist'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0],2)

if __name__=='__main__':unittest.main()
