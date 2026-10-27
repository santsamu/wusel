"""Bounded HTTP smoke check for a freshly started Wusel container."""
import argparse
import json
import time
from urllib.error import URLError
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
    with http.open(base+'/api/state',timeout=5) as response:
        state=json.load(response)
        if state.get('needs_setup') is not True or state.get('user') is not None:
            raise RuntimeError('Fresh disposable container must start at first-run setup')
    print('Container smoke passed: health, frontend assets and first-run API')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base',nargs='?',default='http://127.0.0.1:8099')
    parser.add_argument('--timeout',type=int,default=45)
    args=parser.parse_args()
    smoke(args.base,args.timeout)
