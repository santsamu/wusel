"""Build the Wusel source distribution without runtime data or cache files."""
import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT / 'wusel'
SKIP = {'__pycache__', '.venv', 'node_modules', '.git', 'work'}
LEGACY_NAMES = ('routine' + '-garden', 'routine' + '_garden')

def files():
    for name in ('wusel', 'tests', 'tools'):
        for path in (PROJECT / name).rglob('*'):
            if path.is_file() and not any(part in SKIP for part in path.relative_to(PROJECT).parts) and path.suffix not in {'.pyc','.sqlite3','.db'}:
                yield path
    for name in ('README.md','README.de.md','VALIDATION.md','themes-settings.png'):
        path = PROJECT / name
        if path.exists():
            yield path
    yield from PROJECT.glob('theme-*.png')

def build(output=None):
    config = (APP / 'config.yaml').read_text(encoding='utf-8-sig')
    match = re.search(r'^version:\s*[\"\']?([^\"\'\s]+)',config,re.MULTILINE)
    if not match:
        raise ValueError('No app version in wusel/config.yaml')
    version = match.group(1)
    output = (output or PROJECT / 'dist' / f'wusel-{version}.zip').resolve()
    selected = sorted(set(files()))
    for path in selected:
        relative = path.relative_to(PROJECT).as_posix()
        if any(name in relative for name in LEGACY_NAMES):
            raise ValueError('Legacy path in distribution: '+relative)
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as archive:
        for path in selected:
            archive.write(path,Path('wusel')/path.relative_to(PROJECT))
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity check failed')
        required = ('wusel/wusel/config.yaml','wusel/README.md','wusel/README.de.md','wusel/tools/package.py')
        if any(name not in archive.namelist() for name in required):
            raise ValueError('Required distribution file missing')
        if any(any(old in name for old in LEGACY_NAMES) for name in archive.namelist()):
            raise ValueError('Legacy path in archive')
    print(f'Created {output.name}: {len(selected)} files ({output.stat().st_size} bytes)')
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Optional destination ZIP path')
    build(parser.parse_args().output)
