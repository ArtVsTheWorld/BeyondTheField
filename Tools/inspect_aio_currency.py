"""Map supplied AIO callbacks against local original AST evidence, read-only.
Requires Evidence/Aio141/string-diffs.json from the local resource comparison.
Does not redistribute mod resources or edit either mod.
"""
import sys,json,pathlib,struct
sys.path.insert(0,'Tools');import build_currency_ui as cu,build_currency_budget_ui as cb,build_currency_topbar_ui as ct,build_currency_recruitdetail_ui as cd,build_currency_recruiteditor_ui as ce
sys.path.insert(0,r'C:/Apps/CFB 27/Working/Teambuilder Import Plugin/Tools');from inspect_tb_ast import load,walk
pairs=[r for r in json.load(open('Evidence/Aio141/string-diffs.json')) if r['similarity']>.99]
specs=[]
for group,(source,ss) in cu.SPECS.items():
 for off,*_ in ss:specs.append((str(pathlib.Path(source).resolve()),group,off))
for group,source in [('corePrograms',cb.CFM),('animationPrograms',cb.CONTROL),('artPrograms',cb.ART)]:
 for g,off,*_ in cb.SPECS:
  if g==group:specs.append((str(pathlib.Path(source).resolve()),group,off))
specs.append((str(ct.ASSET.resolve()),'topbar',ct.OFFSET))
for _,ss in ct.GROUPS.values():
 for off,*_ in ss:
  if off!=ct.OFFSET:specs.append((str(ct.RECRUITING_ASSET.resolve()),'recruiting',off))
for _,off,*_ in ce.SPECS:specs.append((str(ce.ASSET.resolve()),'editor',off))
specs.append((str(cb.CFM.resolve()),'team',0x728d0))
for mod,g in [(cd,'detail')]:specs.append((str(mod.ASSET.resolve()),g,mod.OFFSET))
result=[]
for src,g,off in specs:
 pair=next((r for r in pairs if str(pathlib.Path(r['old']).resolve()).lower()==src.lower()),None)
 if not pair:
  sa=set(v for v in load(src).const if isinstance(v,str))
  candidates=[]
  for r in pairs:
   sb=set(v for v in load(r['new']).const if isinstance(v,str));candidates.append((len(sa&sb)/max(1,len(sa|sb)),r))
  score,pair=max(candidates,key=lambda x:x[0])
  if score<.98:continue
 a=load(src);b=load(pair['new']);br=dict(b.root_streams())
 for label,ro in a.root_streams():
  try:items=a.decode(ro)
  except Exception:continue
  methods=[]
  for i,it in enumerate(items):
   if it[1] in (0x8e,0x9b):methods.append((int(it[2][3],16)-48,items[i-1][2],it))
  found=next((r for r in methods if r[0]==off),None)
  if not found:continue
  name=found[1][1];ni=b.decode(br[label]);nm=[it for i,it in enumerate(ni) if it[1] in (0x8e,0x9b) and ni[i-1][2]==found[1]]
  if len(nm)!=1:raise ValueError((g,name,len(nm)))
  new=int(nm[0][2][3],16)-48;h=b.data[new:new+48];result.append({'group':g,'source':src,'old':off,'new':new,'name':name,'asset':pair['new'],'argc':struct.unpack_from('<I',h,8)[0],'registers':struct.unpack_from('<H',h,12)[0],'flags':struct.unpack_from('<H',h,14)[0],'size':struct.unpack_from('<I',h,24)[0],'nested':[int(it[2][3],16)-48 for _,_,it in walk(nm[0][3]) if it[1] in (0x8e,0x9b)]});break
pathlib.Path('Evidence/Aio141/method-map.json').write_text(json.dumps(result,indent=2));print(json.dumps([{k:r[k] for k in ['group','name','old','new','registers','size']} for r in result],indent=2))
