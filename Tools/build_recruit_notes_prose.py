"""Validate the authored Notes catalog and emit DLL-owned C++ literals."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
catalog=json.loads((root/'Config/recruit-notes-prose.json').read_text(encoding='utf8'))
lines=['// Generated from Config/recruit-notes-prose.json; edit the catalog.','#pragma once','namespace recruitingfog::resume {','struct Prose {const char* attribute;const char* bands[3][3];};','inline constexpr Prose prose[]={']
all_text=[]
for attribute,bands in catalog.items():
    values=[]
    for band in ['strong','neutral','concern']:
        phrases=bands[band]
        if len(phrases)!=3 or len(set(phrases))!=3:raise ValueError('Every condition requires three distinct observations')
        for phrase in phrases:
            if not phrase[0].isupper() or re.search(r'\d',phrase) or len(phrase)>180:raise ValueError('Invalid qualitative observation')
        values.append('{'+','.join(json.dumps(s,ensure_ascii=False) for s in phrases)+'}');all_text+=phrases
    lines.append('{'+json.dumps(attribute)+',{'+','.join(values)+'}},')
if len(all_text)<300 or len(set(all_text))!=len(all_text):raise ValueError('Catalog is too small or repeats exact passages')
lines+=['};',f'inline constexpr unsigned prosePassages={len(all_text)};','}']
(root/'Source/RecruitNotesProse.h').write_text('\n'.join(lines)+'\n',encoding='utf8')
state_config=json.loads((root/'Config/high-school-state-strength.json').read_text(encoding='utf8'))
states=state_config['rankedStates']
if len(states)!=50 or len(set(states))!=50:raise ValueError('Expected 50 distinct state rank entries')
rank_lines=['// Generated from Config/high-school-state-strength.json.','#pragma once','#include <string>','namespace recruitingfog::resume {','inline int stateRank(const std::string& state){']
aliases={}
for alias,target in state_config['aliases'].items():aliases.setdefault(states.index(target)+1,[]).append(alias)
for rank,names in aliases.items():rank_lines.append('if('+'||'.join('state=='+json.dumps(s) for s in sorted(names,key=len,reverse=True))+f')return {rank};')
rank_lines+=['static constexpr const char* states[]={'+','.join(json.dumps(s) for s in states)+'};','for(int i=0;i<50;++i)if(state==states[i])return i+1;return 0;','}','}']
(root/'Source/RecruitResumeStateRanks.h').write_text('\n'.join(rank_lines)+'\n',encoding='utf8')
print(json.dumps({'attributes':len(catalog),'passages':len(all_text),'alternativesPerCondition':3}))
