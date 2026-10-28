import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application
from weather import Weather
from test_app import Client

NOW=datetime(2026,10,25,7,0,tzinfo=timezone.utc)
ZONE=ZoneInfo('Europe/Zurich')
ENTITY='weather.home'

def state():
    return {'state':'partlycloudy','last_reported':NOW.isoformat(),
            'attributes':{'temperature':9.5,'temperature_unit':'°C','friendly_name':'Home'}}
def forecast(rows):
    return {'changed_states':[],'service_response':{ENTITY:{'forecast':rows}}}

def fixtures(path,body=None):
    if path=='states/'+ENTITY:return state()
    if body['type']=='hourly':return forecast([
        {'datetime':'2026-10-25T05:00:00+00:00','temperature':6,'condition':'cloudy'},
        {'datetime':'2026-10-25T07:00:00+00:00','temperature':9,'condition':'partlycloudy'},
        {'datetime':'2026-10-25T10:00:00+00:00','temperature':13,'condition':'rainy','precipitation_probability':75},
        {'datetime':'2026-10-25T23:00:00+00:00','temperature':4,'condition':'clear-night'},
        {'datetime':'not-a-date','temperature':99}])
    return forecast([{'datetime':'2026-10-25T00:00:00Z','temperature':15,'templow':7,'condition':'cloudy'}])

class WeatherTests(unittest.TestCase):
    def setUp(self):self.weather=Weather(ENTITY,token='server-secret')
    def test_hourly_and_local_day_filtering(self):
        with patch.object(self.weather,'request',side_effect=fixtures) as call:
            result=self.weather.get(ZONE,NOW)
        self.assertEqual(result['forecast_status'],'hourly')
        self.assertEqual(len(result['hourly']),2)
        self.assertEqual(result['hourly'][1]['rain_probability'],75)
        self.assertIsNone(result['hourly'][0]['rain_probability'])
        self.assertEqual(call.call_args_list[1].args,('services/weather/get_forecasts?return_response',{'entity_id':ENTITY,'type':'hourly'}))
        self.assertNotIn('server-secret',json.dumps(result))
    def test_tomorrow_hourly_uses_local_date_and_preserves_daytime(self):
        rows=[{'datetime':'2026-10-25T10:00:00Z','temperature':13,'condition':'cloudy'},
              {'datetime':'2026-10-25T23:00:00Z','temperature':-2,'condition':'clear-night'},
              {'datetime':'2026-10-26T05:00:00Z','temperature':8,'condition':'cloudy'},
              {'datetime':'2026-10-26T15:00:00Z','temperature':14,'condition':'rainy'},
              {'datetime':'2026-10-26T23:00:00Z','temperature':99,'condition':'sunny'}]
        with patch.object(self.weather,'request',side_effect=lambda path,body=None:state() if body is None else forecast(rows)) as req:
            result=self.weather.get(ZONE,NOW)
        self.assertEqual(result['date'],'2026-10-25')
        self.assertEqual(len(result['hourly']),1)
        self.assertEqual(result['tomorrow']['date'],'2026-10-26')
        self.assertEqual([r['temperature'] for r in result['tomorrow']['hourly']],[-2,8,14])
        self.assertEqual(result['tomorrow']['forecast_status'],'hourly')
        self.assertEqual(req.call_count,2)

    def test_tomorrow_daily_fallback_is_separate_from_today(self):
        def provider(path,body=None):
            if body is None:return state()
            if body['type']=='hourly':return fixtures(path,body)
            return forecast([{'datetime':'2026-10-26T00:00:00Z','temperature':18,'templow':4,'condition':'rainy','precipitation_probability':65}])
        with patch.object(self.weather,'request',side_effect=provider):result=self.weather.get(ZONE,NOW)
        self.assertEqual(result['forecast_status'],'hourly')
        self.assertIsNone(result['daily'])
        self.assertEqual(result['tomorrow']['forecast_status'],'daily')
        self.assertEqual(result['tomorrow']['daily']['high'],18)
        self.assertEqual(result['tomorrow']['daily']['rain_probability'],65)

    def test_tomorrow_dst_repeated_hours_are_sorted_as_instants(self):
        now=datetime(2026,10,24,16,tzinfo=timezone.utc)
        rows=[{'datetime':at,'temperature':12,'condition':'cloudy'} for at in
              ['2026-10-25T02:30:00+01:00','2026-10-25T02:30:00+02:00','2026-10-25T07:00:00+01:00','2026-10-25T17:00:00+01:00']]
        with patch.object(self.weather,'request',side_effect=lambda path,body=None:state() if body is None else forecast(rows)):
            result=self.weather.get(ZONE,now)
        tomorrow=result['tomorrow'];self.assertEqual(tomorrow['date'],'2026-10-25')
        self.assertEqual(tomorrow['hourly'][0]['datetime'],'2026-10-25T02:30:00+02:00')
        self.assertEqual(tomorrow['hourly'][1]['datetime'],'2026-10-25T02:30:00+01:00')

    def test_missing_tomorrow_is_explicit_without_reusing_current_conditions(self):
        with patch.object(self.weather,'request',side_effect=fixtures):result=self.weather.get(ZONE,NOW)
        self.assertEqual(result['tomorrow']['forecast_status'],'unavailable')
        self.assertIsNone(result['tomorrow']['daily'])
        self.assertNotIn('current',result['tomorrow'])

    def test_current_weather_survives_missing_forecast(self):
        def provider(path,body=None):
            if path.startswith('states/'):return state()
            raise OSError('not supported')
        with patch.object(self.weather,'request',side_effect=provider):r=self.weather.get(ZONE,NOW)
        self.assertEqual(r['status'],'ok');self.assertEqual(r['forecast_status'],'unavailable')
        self.assertEqual(r['current']['temperature'],9.5)
    def test_daily_fallback_has_no_invented_hours(self):
        def provider(path,body=None):
            if body and body['type']=='hourly':raise OSError('hourly unsupported')
            return fixtures(path,body)
        with patch.object(self.weather,'request',side_effect=provider):r=self.weather.get(ZONE,NOW)
        self.assertEqual(r['forecast_status'],'daily');self.assertEqual(r['hourly'],[])
        self.assertEqual(r['daily']['high'],15)
    def test_cache_is_shared_and_expired_errors_are_marked_stale(self):
        with patch('weather.time.monotonic',return_value=1000),patch.object(self.weather,'request',side_effect=fixtures) as req:
            first=self.weather.get(ZONE,NOW)
            second=self.weather.get(ZONE,NOW)
            self.assertEqual(req.call_count,3);self.assertEqual(first,second)
        with patch('weather.time.monotonic',return_value=1700),patch.object(self.weather,'request',side_effect=OSError('offline')):
            stale=self.weather.get(ZONE,NOW)
        self.assertTrue(stale['stale']);self.assertEqual(stale['fetched_at'],first['fetched_at'])
        with patch('weather.time.monotonic',return_value=5000),patch.object(self.weather,'request',side_effect=OSError('offline')):
            self.assertEqual(self.weather.get(ZONE,NOW),{'status':'unavailable'})
    def test_yesterday_cache_is_not_used_today(self):
        with patch.object(self.weather,'request',side_effect=fixtures):self.weather.get(ZONE,NOW)
        with patch.object(self.weather,'request',side_effect=OSError('offline')):
            self.assertEqual(self.weather.get(ZONE,datetime(2026,10,26,7,tzinfo=timezone.utc)),{'status':'unavailable'})
    def test_no_configuration_and_missing_token(self):
        self.assertEqual(Weather('',token='').get(ZONE,NOW)['status'],'not_configured')
        self.assertEqual(Weather(ENTITY,token='').get(ZONE,NOW)['status'],'unavailable')
        with self.assertRaises(ValueError):Weather('http://example.org',token='x')
    def test_old_observations_are_marked_stale(self):
        old=state();old['last_reported']='2026-10-24T07:00:00Z'
        with patch.object(self.weather,'request',side_effect=lambda path,body=None:old if body is None else fixtures(path,body)):
            self.assertTrue(self.weather.get(ZONE,NOW)['stale'])
    def test_missing_and_invalid_numbers_are_not_zero(self):
        bad=state();bad['attributes'].update(temperature=True,temperature_unit='invalid')
        with patch.object(self.weather,'request',side_effect=lambda path,body=None:bad if body is None else forecast([])):
            r=self.weather.get(ZONE,NOW)
        self.assertIsNone(r['current']['temperature']);self.assertEqual(r['unit'],'')
    def test_outage_does_not_expose_internals(self):
        with patch.object(self.weather,'request',side_effect=RuntimeError('server-secret')):
            self.assertEqual(self.weather.get(ZONE,NOW),{'status':'unavailable'})
    def test_request_uses_supervisor_auth_and_timeouts(self):
        class Reply:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,limit):return b'{"state":"sunny"}'
        with patch('weather.urlopen',return_value=Reply()) as open_url:
            self.weather.request('states/'+ENTITY)
        request=open_url.call_args.args[0]
        self.assertEqual(request.full_url,'http://supervisor/core/api/states/weather.home')
        self.assertEqual(request.get_header('Authorization'),'Bearer server-secret')
        self.assertEqual(open_url.call_args.kwargs['timeout'],4)

class PreferenceTests(unittest.TestCase):
    def setUp(self):
        scratch=Path.cwd()/'work'/'test-data';scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch)
        self.app=Application(self.temp.name)
        self.client=Client(self.app)
        self.client.call('setup',{'name':'Parent','username':'parent','password':'parent-password','code':self.app.setup_code})
        self.client.call('state')
    def tearDown(self):self.temp.cleanup()
    def test_language_is_saved_and_validated(self):
        self.assertEqual(self.client.call('preferences',{'language':'de'})[0],200)
        self.assertEqual(self.client.call('state')[1]['user']['language'],'de')
        self.assertEqual(self.client.call('preferences',{'language':'fr'})[0],400)
        other=Client(self.app);other.call('login',{'username':'parent','password':'parent-password'})
        self.assertEqual(other.call('state')[1]['user']['language'],'de')
    def test_child_can_save_only_own_language(self):
        self.client.call('users',{'name':'Alex','username':'alex','password':'child-pass','role':'child'})
        child=Client(self.app);child.call('login',{'username':'alex','password':'child-pass'});child.call('state')
        self.assertEqual(child.call('preferences',{'language':'de','user':1})[0],200)
        self.assertEqual(child.call('state')[1]['user']['language'],'de')
        self.assertEqual(self.client.call('state')[1]['user']['language'],'')
    def test_weather_requires_login_and_never_blocks_state(self):
        self.assertEqual(Client(self.app).call('weather')[0],401)
        self.assertEqual(self.client.call('weather')[1],{'status':'not_configured'})
        with patch.object(self.app.weather,'get',side_effect=OSError('offline')):
            self.assertEqual(self.client.call('state')[0],200)
    def test_preferences_require_csrf(self):
        self.assertEqual(self.client.call('preferences',{'language':'de'},{'HTTP_X_CSRF_TOKEN':''})[0],403)
    def test_old_database_migrates_without_losing_users(self):
        with self.app.connect() as db:
            db.execute('ALTER TABLE users DROP COLUMN language')
        migrated=Application(self.temp.name)
        with migrated.connect() as db:
            self.assertEqual(db.execute('SELECT username,language FROM users').fetchone()['username'],'parent')
            self.assertEqual(db.execute('SELECT language FROM users').fetchone()[0],'')

if __name__=='__main__':unittest.main()
