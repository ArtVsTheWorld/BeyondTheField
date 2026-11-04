"""Extract local recruiting UI evidence. Game/cache inputs are read-only.

Private ASTs and disassembly remain under ignored Evidence, never in a package.
This developer helper uses the existing local extraction/disassembly tools.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--toolkit', type=Path, default=Path('C:/Apps/CFB 27/Working/Teambuilder Import Plugin'))
parser.add_argument('--index', type=Path)
parser.add_argument('--cache', type=Path, default=Path('C:/Apps/CFB 27/MMC/MMC_Editor_v1.1.0.6/Caches/collegefootball27.cache'))
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'Evidence/RecruitingFog/Assets')
args = parser.parse_args()
sys.path.insert(0, str(args.toolkit/'OfflinePlaycall/Tools'))
from extract_assets import read_asset
sys.path.insert(0, str(args.toolkit/'Tools'))
from inspect_tb_ast import load, walk

legacy = json.loads((args.toolkit/'FbmodMigrationResearch/Evidence/legacy-index.json').read_text(encoding='utf8'))
names = [name for name in legacy if name.endswith('.ast') and any(prefix in name for prefix in [
    '/art_control/recruitinghub/', '/art_screen/recruitinghub/', '/node_cfm/recruitinghub/',
])]
if args.index:
    index = json.loads(args.index.read_text(encoding='utf8'))
else:
    from index_recruiting_cache import read_cache
    index = read_cache(args.cache, {legacy[name]['guid'] for name in names}, args.toolkit)
args.output.mkdir(parents=True, exist_ok=True)
chunks = {}
report = []
for name in sorted(names):
    entry = legacy[name]
    if entry['guid'] not in chunks:
        try:
            chunks[entry['guid']] = read_asset(index['chunks'][entry['guid']])
        except Exception as error:
            report.append({'asset': name, 'readError': repr(error), 'decodeErrors': []})
            continue
    raw = chunks[entry['guid']]
    data = raw[entry['offset']:entry['offset']+entry['size']]
    dest = args.output / name.replace('/', '__')
    dest.write_bytes(data)
    apt = load(dest)
    strings = [{'index': i, 'value': v} for i, v in enumerate(apt.const) if isinstance(v, str)]
    dest.with_suffix('.strings.json').write_text(json.dumps(strings, indent=2), encoding='utf8')
    streams, lines, errors, unsupported = [], [], [], []
    for label, offset in apt.root_streams():
        try:
            items = apt.decode(offset)
            streams.append({'label': label, 'offset': offset, 'instructions': len(items)})
            lines.append(label)
            for parents, i, item in walk(items):
                lines.append('  '*len(parents) + repr(item[:3]))
                if item[1] == -1:
                    unsupported.append({'label': label, 'offset': item[0], 'detail': str(item[2])[:512]})
        except Exception as error:
            errors.append({'label': label, 'error': str(error)})
    dest.with_suffix('.actions.txt').write_text('\n'.join(lines), encoding='utf8')
    report.append({'asset': name, 'sha256': hashlib.sha256(data).hexdigest(),
                   'bytes': len(data), 'strings': strings, 'streams': streams, 'decodeErrors': errors,
                   'unsupportedInstructions': unsupported})
(args.output/'asset-report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps({'assets': len(report), 'decodeErrors': sum(len(r['decodeErrors']) for r in report),'readErrors': sum('readError' in r for r in report),
                  'unsupportedInstructions': sum(len(r.get('unsupportedInstructions', [])) for r in report),
                  'report': str(args.output/'asset-report.json')}))
