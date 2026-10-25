"""Exercise the actual production HTTP server over IPv4 and IPv6."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.request import ProxyHandler, Request, build_opener

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wusel'))
from app import Application
HAS_WAITRESS=importlib.util.find_spec('waitress') is not None

@unittest.skipUnless(HAS_WAITRESS,'Install wusel/requirements.txt to run production HTTP checks')
class ProductionServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from server import create_http_server
        scratch=Path.cwd()/'work'/'http-test-data';scratch.mkdir(parents=True,exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(dir=scratch)
        cls.app=Application(cls.temp.name)
        cls.server=create_http_server(cls.app,port=0)
        cls.addresses=getattr(cls.server,'effective_listen',[(getattr(cls.server,'effective_host',''),getattr(cls.server,'effective_port',0))])
        cls.thread=threading.Thread(target=cls.server.run,daemon=True,name='wusel-http-test')
        cls.thread.start()
        cls.http=build_opener(ProxyHandler({}))
    @classmethod
    def tearDownClass(cls):
        cls.server.close();cls.thread.join(timeout=4);cls.temp.cleanup()
    def url(self,ipv6,path):
        match=next(((host,port) for host,port in self.addresses if (':' in host)==ipv6),None)
        if not match:self.skipTest('This OS has no '+('IPv6' if ipv6 else 'IPv4')+' listener')
        return ('http://[::1]:' if ipv6 else 'http://127.0.0.1:')+str(match[1])+path
    def test_ipv4_health(self):
        with self.http.open(self.url(False,'/health'),timeout=5) as response:
            self.assertEqual(response.status,200);self.assertEqual(json.load(response),{'ok':True})
    def test_ipv6_health(self):
        with self.http.open(self.url(True,'/health'),timeout=5) as response:
            self.assertEqual(response.status,200);self.assertEqual(json.load(response),{'ok':True})
    def test_ipv4_and_ipv6_deliver_app_and_styles(self):
        for ipv6 in (False,True):
            with self.http.open(self.url(ipv6,'/'),timeout=5) as response:
                self.assertIn('Wusel',response.read().decode())
            with self.http.open(self.url(ipv6,'/static/themes.css'),timeout=5) as response:
                self.assertEqual(response.status,200);self.assertEqual(response.headers.get_content_type(),'text/css')
    def test_real_http_state_endpoint(self):
        for ipv6 in (False,True):
            with self.http.open(self.url(ipv6,'/api/state'),timeout=5) as response:
                state=json.load(response);self.assertTrue(state['needs_setup']);self.assertIsNone(state['user'])

class HostNetworkConfigurationTests(unittest.TestCase):
    def test_host_network_has_literal_web_port(self):
        folder=Path(__file__).resolve().parents[1]/'wusel'
        config=(folder/'config.yaml').read_text(encoding='utf-8')
        self.assertIn('host_network: true',config)
        self.assertIn('init: true',config)
        self.assertIn('http://[HOST]:8099/',config)
        self.assertNotIn('[PORT:',config)
        self.assertNotIn('\nports:',config)
        self.assertIn('server.py',(folder/'Dockerfile').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
