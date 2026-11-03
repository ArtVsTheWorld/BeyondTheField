"""Summarize query-only process observations and an offline Node CPU profile."""
from collections import Counter
import json
from pathlib import Path


root = Path(__file__).resolve().parents[1] / 'Evidence' / 'Week12'
profile = json.loads((root / 'generator.cpuprofile').read_text())
nodes = {n['id']: n['callFrame'] for n in profile['nodes']}
functions, files = Counter(), Counter()
total = 0
for node, delta in zip(profile.get('samples', []), profile.get('timeDeltas', [])):
    frame = nodes[node]
    functions[(frame['functionName'], frame['url'], frame['lineNumber']+1)] += delta
    files[frame['url'] or frame['functionName']] += delta
    total += delta
result = dict(sampledSeconds=round(total/1e6, 3), functions=[
    dict(name=key[0], file=key[1], line=key[2], seconds=round(value/1e6, 3),
         percent=round(100*value/total, 1)) for key, value in functions.most_common(16)],
    files=[dict(file=key, seconds=round(value/1e6, 3), percent=round(100*value/total, 1))
           for key, value in files.most_common(12)])
(root / 'generator-profile-summary.json').write_text(json.dumps(result, indent=2))
observations = {}
for filename in ('baseline-stationary-22736.jsonl', 'disabled-stationary-22736.jsonl'):
    rows = [json.loads(line) for line in (root / filename).read_text().splitlines()]
    # Discard the first three seconds, including any in-flight capture at stop.
    stable = [row for row in rows if row['sample'] >= 4]
    threads = Counter()
    for row in stable:
        threads.update(row['thread_cpu'])
    elapsed = sum(row['elapsed'] for row in stable)
    observations[filename] = dict(seconds=round(elapsed, 3),
        processCpuSeconds=round(sum(row['cpu_seconds'] for row in stable), 3),
        readerCpuSeconds=round(threads['31240'], 3),
        readerCorePercent=round(100*threads['31240']/elapsed, 1),
        minimumPrivateMB=round(min(row['private_bytes'] for row in stable)/2**20, 1),
        maximumPrivateMB=round(max(row['private_bytes'] for row in stable)/2**20, 1))
result['observations'] = observations
(root / 'performance-summary.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
