"""Home Screen launch metadata and public asset integration."""
import io
import json
from html.parser import HTMLParser
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from urllib.parse import urljoin, urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wusel'))
from app import Application

class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.meta={}
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='link':self.links.append(attrs)
        if tag=='meta':self.meta[attrs.get('name')]=attrs.get('content')

class HomeScreenTests(unittest.TestCase):
    def test_anonymous_http_launch_resolves_manifest_scope_and_icons(self):
        scratch=ROOT/'work/test-data';scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            app=Application(folder)
            def get(url):
                captured={}
                def start(status,headers):captured.update(status=status,headers=dict(headers))
                body=b''.join(app({'REQUEST_METHOD':'GET','PATH_INFO':urlsplit(url).path,
                                  'wsgi.url_scheme':'http','wsgi.input':io.BytesIO()},start))
                self.assertEqual(captured['status'],'200 OK')
                self.assertNotIn('Set-Cookie',captured['headers'])
                return captured['headers'],body
            base='http://homeassistant.local:8099/'
            _,html=get(base)
            head=HeadParser();head.feed(html.decode())
            manifests=[link for link in head.links if link.get('rel')=='manifest']
            self.assertEqual(len(manifests),1)
            url=urljoin(base,manifests[0]['href'])
            headers,body=get(url)
            self.assertEqual(headers['Content-Type'],'application/manifest+json; charset=utf-8')
            manifest=json.loads(body)
            self.assertEqual(manifest['short_name'],'Wusel')
            for key in ['id','start_url','scope']:
                self.assertEqual(urljoin(url,manifest[key]),base)
            self.assertEqual(manifest['display'],'fullscreen')
            self.assertEqual({icon['sizes'] for icon in manifest['icons']},{'192x192','512x512'})
            for icon in manifest['icons']:
                headers,data=get(urljoin(url,icon['src']))
                self.assertEqual(headers['Content-Type'],icon['type'])
                width,height=struct.unpack('>II',data[16:24])
                self.assertEqual(icon['sizes'],f'{width}x{height}')
            self.assertEqual(head.meta['apple-mobile-web-app-capable'],'yes')
            self.assertEqual(head.meta['apple-mobile-web-app-title'],'Wusel')
            touch=next(link for link in head.links if link.get('rel')=='apple-touch-icon')
            self.assertEqual(get(urljoin(base,touch['href']))[0]['Content-Type'],'image/png')

if __name__=='__main__':unittest.main()
