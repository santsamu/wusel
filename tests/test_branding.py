import io
from pathlib import Path
import struct
import tempfile
import unittest
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wusel'))
from app import Application

class BrandingTests(unittest.TestCase):
    def request(self,app,path):
        captured={}
        def start(status,headers):captured.update(status=int(status.split()[0]),headers=dict(headers))
        body=b''.join(app({'REQUEST_METHOD':'GET','PATH_INFO':path,'wsgi.input':io.BytesIO()},start))
        return captured,body

    def test_public_brand_assets_have_correct_mime_and_safe_paths(self):
        scratch=ROOT/'work/test-data';scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            app=Application(folder)
            for name in ['wusel-logo.png','wusel-mark.png','favicon-16.png','favicon-32.png','favicon-192.png','favicon-512.png','apple-touch-icon.png']:
                with self.subTest(name=name):
                    result,body=self.request(app,'/static/'+name)
                    self.assertEqual(result['status'],200)
                    self.assertEqual(result['headers']['Content-Type'],'image/png')
                    self.assertTrue(body.startswith(b'\x89PNG\r\n\x1a\n'))
            root,body=self.request(app,'/favicon.ico')
            nested,other=self.request(app,'/static/favicon.ico')
            self.assertEqual(root['status'],200);self.assertEqual(nested['status'],200)
            self.assertEqual(root['headers']['Content-Type'],'image/x-icon');self.assertEqual(body,other)
            for path in ['/static/../app.py','/static/../../data/wusel.sqlite3','/static/not-an-asset.png']:
                self.assertEqual(self.request(app,path)[0]['status'],404)

    def test_favicon_frames_touch_icon_and_home_assistant_dimensions(self):
        static=ROOT/'wusel/static'
        for path,size in [(static/'favicon-16.png',16),(static/'favicon-32.png',32),(static/'favicon-192.png',192),(static/'favicon-512.png',512),(static/'apple-touch-icon.png',180),(ROOT/'wusel/icon.png',128)]:
            self.assertEqual(struct.unpack('>II',path.read_bytes()[16:24]),(size,size))
        data=(static/'favicon.ico').read_bytes()
        self.assertEqual(struct.unpack('<HHH',data[:6]),(0,1,6))
        sizes=[]
        for index in range(6):
            width,height,_,_,planes,bits,length,offset=struct.unpack_from('<BBBBHHII',data,6+index*16)
            width=width or 256;height=height or 256;sizes.append(width)
            self.assertEqual((planes,bits),(1,32))
            frame=data[offset:offset+length];self.assertTrue(frame.startswith(b'\x89PNG'))
            self.assertEqual(struct.unpack('>II',frame[16:24]),(width,height))
        self.assertEqual(sizes,[16,32,48,64,128,256])

if __name__=='__main__':unittest.main()
