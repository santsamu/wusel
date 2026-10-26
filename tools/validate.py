"""Validate Wusel source metadata and distributable packages (CI/development only)."""
import argparse
import ast
import json
import os
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile
from zoneinfo import ZoneInfo
import yaml

ROOT = Path(__file__).resolve().parents[1]

class UniqueLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def load_yaml(text):
    return yaml.load(text, Loader=UniqueLoader)

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate_webui(value):
    # Supervisor requires port placeholders even when host networking is enabled.
    require(isinstance(value,str) and re.fullmatch(r'(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*',value),
            'Web URL must use the Home Assistant host and port placeholders')
    require(value=='http://[HOST]:[PORT:8099]/','Web URL must match the listener port')

def validate(root=ROOT):
    app = root/'wusel'
    config = load_yaml((app/'config.yaml').read_text(encoding='utf-8-sig'))
    version = config.get('version')
    require(isinstance(version,str) and re.fullmatch(r'\d+\.\d+\.\d+',version),'App version must be semantic x.y.z')
    require(config.get('slug')=='wusel','Home Assistant app identity must be wusel')
    require(set(config.get('arch',[]))=={'aarch64','amd64'},'Manifest and build matrix must cover both architectures')
    require(config.get('host_network') is True,'Host networking is required for the current listener')
    validate_webui(config.get('webui'))
    require(config.get('backup')=='cold','SQLite backups must stop the app')
    require(set(config['options'])==set(config['schema']),'Options must match the Home Assistant schema')
    ZoneInfo(config['options']['timezone'])
    docker = (app/'Dockerfile').read_text(encoding='utf-8')
    require(f'ARG BUILD_VERSION={version}' in docker,'Dockerfile version differs from manifest')
    require('FROM python:3.12-slim' in docker and 'EXPOSE 8099' in docker,'Container runtime or port differs from CI')
    require(f'## {version}\n' in (app/'CHANGELOG.md').read_text(encoding='utf-8'),'Missing changelog entry')
    for name in ('README.md','README.de.md','wusel/README.md','wusel/README.de.md','wusel/DOCS.md','wusel/DOCS.de.md'):
        require(f'Version {version}**' in (root/name).read_text(encoding='utf-8'),f'Stale version in {name}')
    for path in app.rglob('*.yaml'):
        load_yaml(path.read_text(encoding='utf-8-sig'))
    for path in app.rglob('*.json'):
        require(isinstance(json.loads(path.read_text(encoding='utf-8')),dict),f'JSON object required: {path}')
    for folder in ('wusel','tools','tests'):
        for path in (root/folder).rglob('*.py'):
            ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
    flow = load_yaml((root/'.github/workflows/ci.yml').read_text(encoding='utf-8-sig'))
    require(set(flow.get('on',{}))=={'push','pull_request','workflow_dispatch'},'CI triggers missing')
    require(flow.get('permissions')=={'contents':'read'},'CI must use read-only repository permissions')
    jobs = flow['jobs']
    require(jobs['container']['needs']=='quality','Container builds must depend on source checks')
    require({x['arch']:x['platform'] for x in jobs['container']['strategy']['matrix']['include']}=={'amd64':'linux/amd64','aarch64':'linux/arm64'},'Build matrix differs from supported platforms')
    for job in jobs.values():
        require(job.get('timeout-minutes',0)>0,'Every CI job needs a bounded timeout')
        for step in job['steps']:
            if 'uses' in step:
                require(re.fullmatch(r'[\w-]+/[\w-]+@[0-9a-f]{40}',step['uses']),f'Action must be commit-pinned: {step["uses"]}')
    return version

def validate_archive(path, version):
    with ZipFile(path) as archive:
        require(archive.testzip() is None,'Archive checksum failure')
        names = archive.namelist()
        require(len(names)==len(set(names)),'Duplicate archive members')
        for name in names:
            entry = PurePosixPath(name)
            require(bool(entry.parts) and not entry.is_absolute() and '..' not in entry.parts and entry.parts[0]=='wusel','Unsafe archive member')
            require(not any(part in {'work','data','.git','__pycache__','.venv','node_modules'} for part in entry.parts),'Runtime data/cache in source archive')
            require(not any(part=='.env' or part.startswith('.env.') or part=='setup-code' for part in entry.parts),'Private configuration in archive')
            require(entry.suffix.lower() not in {'.sqlite3','.db','.pyc'},'Database or bytecode in archive')
        required=('wusel/wusel/config.yaml','wusel/wusel/Dockerfile','wusel/wusel/static/app.js','wusel/wusel/static/i18n.js','wusel/wusel/static/index.html','wusel/wusel/static/style.css','wusel/wusel/static/themes.css','wusel/wusel/weather.py','wusel/wusel/server.py','wusel/wusel/requirements.txt','wusel/tools/validate.py','wusel/requirements-dev.txt')
        require(all(name in names for name in required),'Required source file missing from archive')
        require(load_yaml(archive.read('wusel/wusel/config.yaml'))['version']==version,'Packaged version differs from source')
        require(f'ARG BUILD_VERSION={version}' in archive.read('wusel/wusel/Dockerfile').decode('utf-8'),'Packaged Docker version differs')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--github-output',action='store_true')
    args=parser.parse_args()
    version=validate()
    if args.archive:
        validate_archive(args.archive,version)
    if args.github_output:
        with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf-8') as output:
            output.write(f'version={version}\n')
    print(f'Wusel {version}: metadata, versions, Python syntax, JSON and CI validation passed'+('; archive passed' if args.archive else ''))
