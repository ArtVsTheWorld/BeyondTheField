"""Offline audit of installed broadcast definitions; no game/process writes.

Private game assets and complete definition reports stay in ignored Evidence.
Only semantic rating identifiers and custom conversion code enter the package.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys


def audit(asset, toolkit, ibx_tools):
    sys.path.insert(0, str(toolkit / 'OfflineDynastySettingsFbmod/Tools'))
    sys.path.insert(0, str(ibx_tools))
    from apt_patch import Bgfa
    from ibx_read import Ibx

    raw = asset.read_bytes()
    archive = Bgfa(raw)
    banners, columns, non_direct, non_default = {}, {}, [], []
    parsed_banners = 0
    for index, entry in enumerate(archive.entries):
        # The bounded reader rejects truncation, extra bytes and deep nesting.
        document = Ibx(entry['raw']).root
        for banner in document.iter('Banners.Banner'):
            parsed_banners += 1
            fields = []
            for text in banner.iter('Muse.TextVariable'):
                for query in text.iter('Muse.GameQueryVariable'):
                    name = query.get('DisplayName', '')
                    if not name.startswith('PLAYER_GAME_VIEW.PLYR_'):
                        continue
                    if query.get('table') != 'AGLP':
                        raise ValueError('Player rating query has an unsupported table')
                    column = query.get('column')
                    if column in columns and columns[column] != name:
                        raise ValueError('Ambiguous rating column semantics')
                    columns[column] = name
                    field = {'query': name, 'table': query.get('table'), 'column': column,
                             'format': text.get('Format'), 'direct': list(text) == [query]}
                    fields.append(field)
                    if not field['direct']:
                        non_direct.append({'title': banner.get('Title'), **field})
                    if field['format'] != '0':
                        non_default.append({'title': banner.get('Title'), **field})
            if fields:
                title = banner.get('Title')
                if title in banners and banners[title]['fields'] != fields:
                    raise ValueError('Conflicting rating definitions for ' + title)
                banners[title] = {'entry': index, 'definition': dict(banner.attrib), 'fields': fields}

    policy = (Path(__file__).resolve().parents[1] / 'Source/PlayerPresentationPolicy.h').read_text()
    compiled_columns = set(re.findall(r'fourcc\("(.{4})"\)', policy)) - {'AGLP'}
    if compiled_columns != set(columns):
        raise ValueError('Presentation whitelist differs from the installed definitions: ' +
                         repr(compiled_columns.symmetric_difference(columns)))
    return {'asset': str(asset), 'sha256': hashlib.sha256(raw).hexdigest(),
            'archiveEntries': len(archive.entries), 'parsedBannerDefinitions': parsed_banners,
            'uniqueRatingBanners': len(banners),
            'uniqueRatingCells': sum(len(b['fields']) for b in banners.values()),
            'columns': columns, 'banners': banners, 'nonDirect': non_direct,
            'nonDefaultFormat': non_default,
            'coverage': 'Static query identity and native formatter support; scene execution is not implied.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset', type=Path, default=Path('Evidence/PlayerFog/Presentations/common__presentation__broadcast__banners__banners.ast'))
    parser.add_argument('--toolkit', type=Path, default=Path('C:/Apps/CFB 27/Working/Teambuilder Import Plugin'))
    parser.add_argument('--ibx-tools', type=Path, default=Path('C:/Apps/CFB 27/MMC/DynamicAttendance/Research'))
    parser.add_argument('--output', type=Path, default=Path('Evidence/PlayerFog/Presentations/rating-audit.json'))
    args = parser.parse_args()
    report = audit(args.asset, args.toolkit, args.ibx_tools)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ('archiveEntries', 'parsedBannerDefinitions',
          'uniqueRatingBanners', 'uniqueRatingCells', 'nonDirect', 'nonDefaultFormat')}))
