import io
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wusel'))
from app import Application, TASK_ICONS, ALL_BADGES

class SVGIconTests(unittest.TestCase):
    def registry(self):
        source=(ROOT/'wusel/static/icons.js').read_text(encoding='utf-8')
        return json.loads(source.split('Object.freeze(',1)[1].split(');',1)[0])

    def test_artwork_covers_tasks_badges_and_safe_svg_geometry(self):
        icons=self.registry()
        self.assertTrue(set(TASK_ICONS[1:]).issubset(icons))
        self.assertTrue({'badge-'+badge[0] for badge,_ in ALL_BADGES}.issubset(icons))
        for name,body in icons.items():
            with self.subTest(name=name):
                root=ET.fromstring('<svg>'+body+'</svg>')
                for node in root.iter():
                    self.assertIn(node.tag,{'svg','g','path','rect','circle'})
                    for attr,value in node.attrib.items():
                        self.assertIn(attr,{'d','fill','x','y','width','height','rx','cx','cy','r','transform'})
                        self.assertNotIn('url(',value.lower())
                        self.assertNotIn('javascript:',value.lower())
        self.assertEqual(len({icons['badge-'+badge[0]] for badge,_ in ALL_BADGES}),17)

    def test_icons_asset_is_served_as_local_javascript_and_loaded_before_app(self):
        scratch=ROOT/'work/test-data';scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            application=Application(folder);captured={}
            def start(status,headers):captured.update(status=status,headers=dict(headers))
            payload=b''.join(application({'REQUEST_METHOD':'GET','PATH_INFO':'/static/icons.js','wsgi.input':io.BytesIO()},start))
            self.assertTrue(captured['status'].startswith('200'))
            self.assertIn('text/javascript',captured['headers']['Content-Type'])
            self.assertIn(b'WUSEL_ICONS',payload)
        html=(ROOT/'wusel/static/index.html').read_text()
        self.assertLess(html.index('static/icons.js'),html.index('static/app.js'))

if __name__=='__main__':unittest.main()
