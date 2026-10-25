import sys,tempfile,unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application
from test_app import Client

class RewardEventTests(unittest.TestCase):
    def setUp(self):
        scratch=Path.cwd()/'work'/'test-data';scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.app=Application(self.temp.name);self.app.today=lambda:date(2026,10,26)
        self.parent=Client(self.app);self.parent.call('setup',{'name':'Parent','username':'parent','password':'parent-password','code':self.app.setup_code});self.parent.call('state')
        self.parent.call('users',{'name':'Alex','username':'alex','password':'child-pass','role':'child'})
        self.parent.call('routines',{'child':2,'title':'Task','description':'','time':'07:00','days':[0]})
        self.child=Client(self.app);self.child.call('login',{'username':'alex','password':'child-pass'});self.child.call('state')
    def tearDown(self):self.temp.cleanup()
    def test_new_reward_only_on_first_completion(self):
        for done,expected in [(True,10),(True,0),(False,0),(True,0)]:
            code,data=self.child.call('complete',{'routine':1,'done':done})
            self.assertEqual(code,200);self.assertEqual(data['earned_points'],expected)
        self.assertEqual(self.child.call('state')[1]['children'][0]['progress']['xp'],10)
    def test_only_one_concurrent_request_receives_reward(self):
        def complete(_):
            client=Client(self.app);client.cookie=self.child.cookie;client.csrf=self.child.csrf
            code,data=client.call('complete',{'routine':1,'done':True});self.assertEqual(code,200)
            return data['earned_points']
        with ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(complete,range(8)))
        self.assertEqual(sum(values),10);self.assertEqual(values.count(10),1)

if __name__=='__main__':unittest.main()
