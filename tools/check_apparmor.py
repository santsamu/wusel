"""Real Linux AppArmor integration checks; uses only disposable container/data.

Run as root on an AppArmor-enabled Docker host after building the Wusel image.
No fallback to an unconfined/complain profile is permitted. This does not deploy
to Home Assistant or prove compatibility with every Home Assistant OS kernel.
"""
import argparse
from datetime import datetime, timedelta, timezone
from http.cookiejar import CookieJar
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TOKEN = 'disposable-apparmor-weather-fixture'


def run(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True, timeout=60)


def profile_denials(log, profile, since):
    """Use kernel boot timestamps, independent of wall-clock/journal setup."""
    result = []
    for line in log.splitlines():
        if 'apparmor="DENIED"' not in line or f'profile="{profile}"' not in line:
            continue
        stamp = re.search(r'\[\s*(\d+(?:\.\d+)?)\]', line)
        if not stamp:
            raise ValueError('AppArmor audit entry lacks a kernel timestamp')
        if float(stamp.group(1)) >= since:
            result.append(line)
    return result


class WeatherFixture(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        self.reply()

    def do_POST(self):
        self.reply()

    def reply(self):
        assert self.headers.get('Authorization') == 'Bearer ' + TOKEN
        now = datetime.now(timezone.utc)
        if self.path == '/core/api/states/weather.demo':
            data = {'state': 'cloudy', 'last_reported': now.isoformat(),
                    'attributes': {'temperature': 12, 'temperature_unit': '\u00b0C'}}
        elif self.path == '/core/api/services/weather/get_forecasts?return_response':
            request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            assert request == {'entity_id': 'weather.demo', 'type': 'hourly'}
            local = now.astimezone(ZoneInfo('Europe/Zurich'))
            rows = [{'datetime': now.isoformat(), 'temperature': 12, 'condition': 'cloudy'}]
            for hour in (7, 17):
                at = (local + timedelta(days=1)).replace(hour=hour, minute=0, second=0)
                rows.append({'datetime': at.isoformat(), 'temperature': 10, 'condition': 'rainy'})
            data = {'service_response': {'weather.demo': {'forecast': rows}}}
        else:
            raise AssertionError('Unexpected weather destination')
        payload = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class Client:
    def __init__(self):
        self.http = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))
        self.csrf = ''

    def call(self, path, body=None, expected=200):
        payload = json.dumps(body).encode() if body is not None else None
        request = Request('http://127.0.0.1:8099/api/' + path, data=payload,
                          headers={'Content-Type': 'application/json', 'X-Wusel-Request': '1',
                                   'X-CSRF-Token': self.csrf})
        try:
            response = self.http.open(request, timeout=20)
        except HTTPError as error:
            response = error
        with response:
            assert response.status == expected, (path, response.status)
            data = json.load(response)
        if path == 'state' and 'csrf' in data:
            self.csrf = data['csrf']
        return data


def check(image):
    # Check both Docker's configured label and the kernel's effective label below.
    assert any('apparmor' in value for value in json.loads(
        run('docker', 'info', '--format', '{{json .SecurityOptions}}').stdout)), 'AppArmor required'
    assert run('aa-enabled').returncode == 0
    name = 'wusel-apparmor-check'
    profile_name = 'local_wusel'
    assert run('docker', 'inspect', name, check=False).returncode != 0, 'Test container name already in use'
    labels = Path('/sys/kernel/security/apparmor/profiles').read_text().splitlines()
    assert not any(line.startswith(profile_name + ' ') for line in labels), 'Refusing to replace an existing profile'
    fixture = ThreadingHTTPServer(('127.0.0.2', 80), WeatherFixture)
    thread = threading.Thread(target=fixture.serve_forever, daemon=True)
    thread.start()
    loaded = False
    with tempfile.TemporaryDirectory(prefix='wusel-apparmor-') as folder:
        temp = Path(folder)
        data = temp / 'data'
        data.mkdir()
        canary = temp / 'canary'
        canary.write_text('This readable file must be blocked by AppArmor.')
        profile = temp / 'profile'
        raw = (ROOT / 'wusel/apparmor.txt').read_text()
        assert len(re.findall(r'^profile ', raw, re.M)) == 1
        # Supervisor performs this same name substitution before loading.
        profile.write_text(raw.replace('profile wusel ', 'profile ' + profile_name + ' ', 1))
        try:
            run('apparmor_parser', '-Q', '-T', str(ROOT / 'wusel/apparmor.txt'))
            run('apparmor_parser', '-r', '-T', str(profile))
            loaded = True
            since = float(Path('/proc/uptime').read_text().split()[0])
            run('docker', 'run', '--detach', '--name', name, '--init', '--network', 'host',
                '--security-opt', 'apparmor=' + profile_name, '--add-host', 'supervisor:127.0.0.2',
                '--mount', f'type=bind,src={data},dst=/data',
                '--mount', f'type=bind,src={canary},dst=/share/canary,readonly',
                '--env', 'SUPERVISOR_TOKEN=' + TOKEN, '--env', 'WUSEL_WEATHER_ENTITY=weather.demo', image)
            from tools.smoke import smoke
            smoke('http://127.0.0.1:8099')
            assert run('docker', 'inspect', '--format', '{{.AppArmorProfile}}', name).stdout.strip() == profile_name
            label = run('docker', 'exec', name, 'python', '-c',
                        "print(open('/proc/self/attr/current').read().strip())").stdout.strip()
            assert label == profile_name + ' (enforce)', label
            http = build_opener(ProxyHandler({}))
            with http.open('http://[::1]:8099/health', timeout=5) as reply:
                assert json.load(reply) == {'ok': True}

            parent, child = Client(), Client()
            code = (data / 'setup-code').read_text().strip()
            parent.call('setup', {'code': code, 'name': 'Demo parent', 'username': 'parent', 'password': 'demo-password'})
            parent.call('state')
            parent.call('users', {'name': 'Demo child', 'username': 'child', 'password': 'demo-password', 'role': 'child'})
            parent.call('routines', {'child': 2, 'title': 'Demo task', 'description': 'Demo help',
                                    'first_action': 'Get started', 'icon': 'snack-box', 'time': '07:00', 'days': list(range(7))})
            parent.call('preferences', {'language': 'de', 'theme': 'lavender'})
            child.call('login', {'username': 'child', 'password': 'demo-password'})
            today = child.call('state')['today']
            child.call('complete', {'routine': 1, 'done': True, 'day': today})
            assert child.call('state')['children'][0]['progress']['xp'] == 10
            child.call('complete', {'routine': 1, 'done': False, 'day': today})
            child.call('complete', {'routine': 1, 'done': True, 'day': today})
            completion = parent.call('state')['children'][0]['history'][0]['id']
            parent.call('correct', {'completion': completion})
            child.call('complete', {'routine': 1, 'done': True, 'day': today}, expected=403)
            parent.call('correct', {'completion': completion, 'restore': True})
            parent.call('updates')
            weather = child.call('weather')
            assert weather['status'] == 'ok' and weather['tomorrow']['forecast_status'] == 'hourly'
            assert (data / 'wusel.sqlite3').is_file()
            # SQLite/WAL locks, runtime imports, DNS config and UDP socket access.
            run('docker', 'exec', name, 'python', '-c',
                "import sqlite3,socket,fcntl; from pathlib import Path; "
                "db=sqlite3.connect('/data/wusel.sqlite3'); assert db.execute('select count(*) from users').fetchone()[0]==2; "
                "f=open('/data/lock-check','w'); fcntl.flock(f,fcntl.LOCK_EX); "
                "socket.getaddrinfo('supervisor',80); socket.socket(socket.AF_INET,socket.SOCK_DGRAM).close(); "
                "Path('/etc/resolv.conf').read_text()")
            run('docker', 'stop', '--time', '10', name)
            assert int(run('docker', 'inspect', '--format', '{{.State.ExitCode}}', name).stdout) in (0, 143)
            run('docker', 'start', name)
            deadline = time.monotonic() + 30
            while True:
                try:
                    assert parent.call('state')['children'][0]['progress']['xp'] == 10
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(1)
            parent.call('reset-child', {'child': 2, 'confirmation': 'child', 'current_password': 'demo-password'})
            assert parent.call('state')['children'][0]['progress']['xp'] == 0
            # --raw retains boot timestamps on Ubuntu 24.04's util-linux too;
            # --time-format raw only exists in newer util-linux releases.
            audit = run('dmesg', '--raw', check=False)
            assert audit.returncode == 0, 'Cannot read kernel audit log: ' + audit.stderr
            denials = profile_denials(audit.stdout, profile_name, since)
            assert not denials, '\n'.join(denials)
            print('Enforced positive flows passed, with no AppArmor audit denials.')

            # These paths exist and are DAC-accessible to container root; denial
            # must be EACCES rather than a missing path or a read-only mount.
            probe = r'''
import os, pathlib, socket, subprocess
assert pathlib.Path('/share/canary').is_file()
for path, mode in [('/etc/shadow','r'),('/share/canary','r'),('/app/app.py','a'),('/etc/hostname','a')]:
    try:
        with open(path,mode): pass
    except PermissionError: pass
    else: raise AssertionError('Unexpected file access: '+path)
script=pathlib.Path('/data/exec-check')
script.write_text('#!/usr/local/bin/python3.12\nprint(1)\n');script.chmod(0o755)
for argv in [['/bin/sh','-c','true'],[str(script)]]:
    try: subprocess.run(argv,check=True)
    except PermissionError: pass
    else: raise AssertionError('Unexpected execution: '+argv[0])
try: socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
except PermissionError: pass
else: raise AssertionError('Unexpected raw socket access')
print('Forbidden reads, writes, shell/data execution and raw sockets denied.')
'''
            print(run('docker', 'exec', name, 'python', '-c', probe).stdout.strip())
        except Exception:
            logs = run('docker', 'logs', name, check=False)
            print(re.sub(r'(Wusel first-run setup code:).*', r'\1 [redacted]', logs.stdout + logs.stderr))
            raise
        finally:
            run('docker', 'rm', '--force', name, check=False)
            if loaded:
                run('apparmor_parser', '-R', str(profile))
            fixture.shutdown()
            fixture.server_close()
            thread.join(timeout=5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    args = parser.parse_args()
    check(args.image)
