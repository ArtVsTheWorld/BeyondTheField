"""Match bounded live definition observations to private native asset metadata."""
from pathlib import Path
import inspect,json,sys,textwrap,types
sys.path.insert(0,'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools')
from inspect_tb_ast import load,walk

rows=[json.loads(line) for line in Path('Build/player-ui-trace.jsonl').read_text().splitlines()]
by_key={}
for row in rows:by_key.setdefault((row['argc'],row['registers'],row['flags'],row['size']),[]).append(row)
assets=[Path('C:/Apps/CFB 27/MMC/AbilityColors/Research/assets/common/ui/art_control/scriptpod.ast'),
        Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/scriptpod.ast'),
        Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_com/frameworkscriptpod.ast'),
        Path('C:/Apps/CFB 27/MMC/PlayerAnalytics/Research/assets/common/ui/node_cfm/corenode.ast'),
        Path('Evidence/PlayerFog/manageplayerart.ast'),Path('Evidence/PlayerFog/manageplayer-skills.ast'),
        Path('Evidence/PlayerFog/node-fe-scriptpodart.ast')]
matches=[];matched=set();failures=[]
for asset in assets:
    apt=load(asset)
    source=textwrap.dedent(inspect.getsource(type(apt).decode)).replace('elif op==0xad:','elif op in (0xac,0xad):')
    namespace={};exec('from apt_uniform_disasm import *\n'+source,namespace);apt.decode=types.MethodType(namespace['decode'],apt)
    for label,root in apt.root_streams():
        try:items=apt.decode(root)
        except Exception as error:failures.append({'asset':str(asset),'root':root,'error':str(error)});continue
        pool=next((i[2] for i in items if i[1]==0x88),[])
        class_names=[v for v in pool if isinstance(v,str) and v.count('.')>=2 and v.startswith(('art_control.','art_screen.','logic_cfm.','ion.','widget.','madden.'))]
        for parents,index,item in walk(items):
            if len(item)<4 or item[1]!=0x8E:continue
            name,argc,register_flags,body_hex,size=item[2]
            if not register_flags:continue
            key=(argc,*register_flags,size);candidates=by_key.get(key,[])
            if not candidates:continue
            body=int(body_hex,16);prefix=apt.data[body:body+min(64,size)].hex()
            container=items
            for parent in parents:container=container[parent][3]
            context=[str(i[2]) for i in container[max(0,index-3):index]]
            for row in candidates:
                if row['prefix64']!=prefix:continue
                matched.add(row['definition'])
                matches.append({'asset':str(asset),'root':root,'classes':class_names,'context':context,'body':body,'definitionOffset':body-48,'argc':argc,'registers':register_flags[0],'flags':register_flags[1],'size':size,'liveDefinition':row['definition'],'path':row['path']})
result={'observedDefinitions':len(rows),'matchedDefinitions':len(matched),'matches':matches,'decodeFailures':failures}
out=Path('Evidence/PlayerFog/ui-trace-matches.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
print(json.dumps({'observed':len(rows),'matched':len(matched),'candidateMethods':len(matches),'decodeFailures':len(failures)}))
for match in matches:
    description=' '.join(match['classes']+match['context'])
    if any(s.lower() in description.lower() for s in ['AttributeSlider','Subskill','GetTemplate','Skills','DetermineCellColor']):
        print(json.dumps({k:match[k] for k in ['classes','context','body','registers','flags','size','path']}))
