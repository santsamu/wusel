"""Regression checks for CI metadata, packaging and the container smoke runner."""
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from wsgiref.simple_server import WSGIRequestHandler, make_server

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'wusel')]
from app import Application, create_app
from tools.package import build
from tools.smoke import smoke
from tools.validate import load_yaml, validate, validate_archive, validate_webui

class CIValidationTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'work'/'test-data';scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.path=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def archive(self,extra=None,omit=None):
        with contextlib.redirect_stdout(io.StringIO()):source=build(self.path/'source.zip')
        target=self.path/'test.zip'
        with ZipFile(source) as original,ZipFile(target,'w') as output:
            for name in original.namelist():
                if name!=omit:output.writestr(name,original.read(name))
            if extra:
                for name,data in extra.items():output.writestr(name,data)
        return target
    def test_source_and_complete_archive_validate(self):
        version=validate();validate_archive(self.archive(),version)
    def test_environment_creates_fresh_wusel_installation(self):
        settings={'WUSEL_DATA':str(self.path),'WUSEL_TIMEZONE':'Europe/Berlin',
                  'WUSEL_SECURE_COOKIE':'1','WUSEL_WEATHER_ENTITY':''}
        with patch.dict(os.environ,settings),contextlib.redirect_stdout(io.StringIO()):
            application=create_app()
        self.assertEqual(application.zone.key,'Europe/Berlin')
        self.assertTrue(application.secure_cookie)
        self.assertEqual(application.db_path,self.path/'wusel.sqlite3')
        self.assertTrue(application.db_path.is_file())
        with application.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0],0)
    def test_webui_requires_supervisor_placeholders_and_listener_port(self):
        validate_webui('http://[HOST]:[PORT:8099]/')
        for value in ['http://[HOST]:8099/','http://[HOST]:[PORT:8080]/',
                      'http://localhost:[PORT:8099]/',None]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                validate_webui(value)
    def test_duplicate_yaml_keys_are_rejected(self):
        with self.assertRaises(ValueError):load_yaml('version: 1\nversion: 2\n')
    def test_private_runtime_and_traversal_members_are_rejected(self):
        version=validate()
        for name in ['wusel/data/wusel.sqlite3','wusel/work/accounts.json','wusel/.env','wusel/setup-code','../outside','/absolute']:
            with self.subTest(name=name),self.assertRaises(ValueError):validate_archive(self.archive({name:b'test'}),version)
    def test_missing_runtime_file_and_wrong_version_are_rejected(self):
        for name in ['wusel/wusel/server.py','wusel/wusel/static/icons.js','wusel/wusel/static/manifest.webmanifest']:
            with self.subTest(name=name),self.assertRaises(ValueError):validate_archive(self.archive(omit=name),validate())
        with self.assertRaises(ValueError):validate_archive(self.archive(),'0.0.0')

class QuietHandler(WSGIRequestHandler):
    def log_message(self,*args):pass

class SmokeRunnerTests(unittest.TestCase):
    def test_smoke_checks_real_fresh_application(self):
        scratch=ROOT/'work'/'test-data';scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            app=Application(folder)
            server=make_server('127.0.0.1',0,app,handler_class=QuietHandler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                output=io.StringIO()
                with contextlib.redirect_stdout(output):smoke(f'http://127.0.0.1:{server.server_port}',timeout=5)
                self.assertIn('Container smoke passed',output.getvalue())
                with app.connect() as db:db.execute("INSERT INTO users(name,username,password,role) VALUES('Demo','demo','unused','parent')")
                with self.assertRaises(RuntimeError):smoke(f'http://127.0.0.1:{server.server_port}',timeout=5)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main()
