"""Bounded HTTP smoke check for a freshly started Wusel container."""
import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener


def smoke(base, timeout=45):
    http=build_opener(ProxyHandler({}))
    base=base.rstrip('/')
    deadline=time.monotonic()+timeout
    while True:
        try:
            with http.open(base+'/health',timeout=2) as response:
                if response.status==200 and json.load(response)=={'ok':True}:
                    break
        except (URLError,OSError,ValueError):
            pass
        if time.monotonic()>=deadline:
            raise RuntimeError('Wusel did not become healthy within the startup timeout')
        time.sleep(1)
    for path, marker in [('/','Wusel'),('/static/app.js','function render'),('/static/icons.js','WUSEL_ICONS'),('/static/i18n.js','CATALOG'),('/static/style.css',':root'),('/static/themes.css','data-theme')]:
        with http.open(base+path,timeout=5) as response:
            if response.status!=200 or marker not in response.read().decode('utf-8'):
                raise RuntimeError('Frontend smoke check failed: '+path)
    for path,signature in [('/static/wusel-mark.png',b'\x89PNG\r\n\x1a\n'),('/favicon.ico',b'\x00\x00\x01\x00')]:
        with http.open(base+path,timeout=5) as response:
            if response.read(len(signature))!=signature:
                raise RuntimeError('Branding asset smoke check failed: '+path)
    with http.open(base+'/api/state',timeout=5) as response:
        state=json.load(response)
        if state.get('needs_setup') is not True or state.get('user') is not None:
            raise RuntimeError('Fresh disposable container must start at first-run setup')
    try:
        with http.open(base+'/api/updates',timeout=5):
            raise RuntimeError('Live updates exposed an unauthenticated marker')
    except HTTPError as error:
        code=error.code
        error.close()
        if code!=401:
            raise RuntimeError('Live updates must require authentication') from error
    print('Container smoke passed: health, frontend assets, first-run API and private update marker')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base',nargs='?',default='http://127.0.0.1:8099')
    parser.add_argument('--timeout',type=int,default=45)
    args=parser.parse_args()
    smoke(args.base,args.timeout)
