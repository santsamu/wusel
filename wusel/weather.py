"""Fixed, server-side Home Assistant weather adapter. No tokens reach the browser."""
import json
import math
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

CONDITIONS = {'clear-night','cloudy','exceptional','fog','hail','lightning','lightning-rainy',
              'partlycloudy','pouring','rainy','snowy','snowy-rainy','sunny','windy','windy-variant'}

def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        return None
    return round(value,1)

def stamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return parsed if parsed.tzinfo is not None else None
    except (ValueError,TypeError):
        return None

def condition(value):
    return value if value in CONDITIONS else 'unknown'

class Weather:
    def __init__(self, entity='', token=None):
        if entity and not re.fullmatch(r'weather\.[a-z0-9_]+',entity):
            raise ValueError('weather_entity must be a weather entity ID, e.g. weather.forecast_home')
        self.entity = entity
        self.token = token if token is not None else os.environ.get('SUPERVISOR_TOKEN','')
        self.lock = threading.Lock()
        self.cached = None
        self.cached_at = 0
        self.retry_at = 0
    def request(self,path,body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request('http://supervisor/core/api/'+path,data=data,
                      headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'})
        with urlopen(req,timeout=4) as response:
            raw = response.read(2_000_001)
        if len(raw)>2_000_000:
            raise ValueError('Weather response is too large')
        return json.loads(raw)
    def forecasts(self,kind):
        result = self.request('services/weather/get_forecasts?return_response',
                              {'entity_id':self.entity,'type':kind})
        rows = result.get('service_response',{}).get(self.entity,{}).get('forecast',[])
        if not isinstance(rows,list):
            raise ValueError('Invalid forecast')
        return rows
    def fetch(self,zone,now):
        state = self.request('states/'+self.entity)
        if state.get('state') in ('unavailable','unknown',None):
            raise ValueError('Weather is unavailable')
        attrs = state.get('attributes',{})
        unit = attrs.get('temperature_unit')
        unit = unit if unit in ('°C','°F') else ''
        current = {'condition':condition(state.get('state')),'temperature':number(attrs.get('temperature')),
                   'apparent_temperature':number(attrs.get('apparent_temperature'))}
        hourly = []
        try:
            for row in self.forecasts('hourly'):
                at = stamp(row.get('datetime')) if isinstance(row,dict) else None
                if at and at.astimezone(zone).date()==now.astimezone(zone).date() and at>=now-timedelta(minutes=30):
                    chance = number(row.get('precipitation_probability'))
                    hourly.append({'datetime':at.isoformat(),'condition':condition(row.get('condition')),
                                   'temperature':number(row.get('temperature')),
                                   'rain_probability':chance if chance is not None and 0<=chance<=100 else None})
        except Exception:
            pass
        hourly.sort(key=lambda r:r['datetime'])
        # Sort instants, including offsets across the autumn DST transition.
        hourly.sort(key=lambda r:stamp(r['datetime']).timestamp())
        daily = None
        if not hourly:
            try:
                for row in self.forecasts('daily'):
                    at = stamp(row.get('datetime')) if isinstance(row,dict) else None
                    if at and at.astimezone(zone).date()==now.astimezone(zone).date():
                        chance = number(row.get('precipitation_probability'))
                        daily = {'condition':condition(row.get('condition')),'high':number(row.get('temperature')),
                                 'low':number(row.get('templow')),
                                 'rain_probability':chance if chance is not None and 0<=chance<=100 else None}
                        break
            except Exception:
                pass
        observed = stamp(state.get('last_reported') or state.get('last_updated'))
        old = bool(observed and now-observed>timedelta(hours=3))
        return {'status':'ok','entity':self.entity,'location':str(attrs.get('friendly_name') or self.entity)[:100],
                'unit':unit,'current':current,'hourly':hourly[:24],'daily':daily,
                'forecast_status':'hourly' if hourly else ('daily' if daily else 'unavailable'),
                'fetched_at':now.isoformat(),'observed_at':observed.isoformat() if observed else None,
                'stale':old}
    def get(self,zone,now=None):
        now = now or datetime.now(timezone.utc)
        if not self.entity:
            return {'status':'not_configured'}
        if not self.token:
            return {'status':'unavailable'}
        clock = time.monotonic()
        cache_today = self.cached and stamp(self.cached['fetched_at']).astimezone(zone).date()==now.astimezone(zone).date()
        if cache_today and clock-self.cached_at<600 and clock>=self.retry_at:
            return self.cached
        def fallback():
            if cache_today and clock-self.cached_at<3600:
                return {**self.cached,'stale':True}
            return {'status':'unavailable'}
        if clock<self.retry_at:
            return fallback()
        # Keep other workers free for check-offs while one refresh is in progress.
        if not self.lock.acquire(blocking=False):
            return fallback()
        try:
            self.cached = self.fetch(zone,now)
            self.cached_at = clock
            self.retry_at = 0
            return self.cached
        except Exception:
            self.retry_at = clock+60
            return fallback()
        finally:
            self.lock.release()
