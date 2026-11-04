"""Import factual school/city/state data from the user-requested NCAA lists.

Football-specific lists exclude institutions which do not sponsor football.
Downloaded HTML stays in ignored Evidence; no browser automation is involved.
"""
import json,re
from pathlib import Path
from urllib.request import Request,urlopen
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
class Tables(HTMLParser):
    def __init__(self):super().__init__();self.tables=[];self.depth=0;self.rows=[];self.row=[];self.cell=None;self.skip=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='table':
            if self.depth:self.depth+=1
            elif 'wikitable' in attrs.get('class','').split():self.depth=1;self.rows=[]
        if self.depth!=1:return
        if tag=='tr':self.row=[]
        elif tag in ('th','td'):self.cell=[];self.span=(int(attrs.get('rowspan','1')),int(attrs.get('colspan','1')))
        elif tag=='sup':self.skip+=1
        elif tag=='br' and self.cell is not None:self.cell.append(' ')
    def handle_endtag(self,tag):
        if tag=='table' and self.depth:
            self.depth-=1
            if not self.depth:self.tables.append(self.expand(self.rows))
            return
        if self.depth!=1:return
        if tag=='sup':self.skip=max(0,self.skip-1)
        if tag in ('td','th') and self.cell is not None:self.row.append((re.sub(r'\s+',' ',''.join(self.cell)).strip(),*self.span));self.cell=None
        if tag=='tr' and self.row:self.rows.append(self.row)
    @staticmethod
    def expand(rows):
        pending={};out=[]
        for i,row in enumerate(rows):
            cells={c:v for (r,c),v in pending.items() if r==i};col=0
            for text,height,width in row:
                while col in cells:col+=1
                for dc in range(width):
                    cells[col+dc]=text
                    for dr in range(1,height):pending[i+dr,col+dc]=text
                col+=width
            out.append([cells.get(c,'') for c in range(max(cells,default=-1)+1)])
        return out
    def handle_data(self,text):
        if self.depth==1 and self.cell is not None and not self.skip:self.cell.append(text)

sources={
 'FCS':'https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_FCS_football_programs',
 'D2':'https://en.wikipedia.org/wiki/List_of_NCAA_Division_II_football_programs',
 'D3':'https://en.wikipedia.org/wiki/List_of_NCAA_Division_III_football_programs'}
schools=[]
for level,url in sources.items():
    request=Request(url,headers={'User-Agent':'DynastyEnhancer research/0.1'})
    with urlopen(request,timeout=30) as response:html=response.read()
    (ROOT/'Evidence/RecruitingFog'/('schools-'+level+'.html')).write_bytes(html)
    parser=Tables();parser.feed(html.decode('utf8'))
    table=next(t for t in parser.tables if t and any('State' in c for c in t[0]) and any(c in ('Program','Team','School') for c in t[0]))
    headers=table[0]
    def column(text):return next(i for i,c in enumerate(headers) if c==text or c.startswith(text))
    name=column('Team' if level=='FCS' else 'Common name' if level=='D2' else 'Team');city=column('City');state=column('State');institution=column('School') if level in ('FCS','D2') else name
    for row in table[1:]:
        if len(row)<=max(name,city,state,institution):continue
        school=row[name].rstrip(' *^').strip();home=re.sub(r'[^A-Za-z]','',row[state]);home='DistrictOfColumbia' if home=='DistrictofColumbia' else home
        if not school or not home or home not in set(json.loads((ROOT/'Config/high-school-state-strength.json').read_text())['rankedStates'])|{'DistrictOfColumbia'}:raise ValueError('Unrecognized school/state row: '+repr(row))
        schools.append({'level':level,'name':school,'institution':row[institution].rstrip(' *^').strip(),'city':row[city],'state':home})
    print(level,sum(s['level']==level for s in schools))
if len(schools)<450:raise ValueError('School catalog unexpectedly small')
data={'version':1,'retrieved':'2026-11-04','requestedSources':['https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_FCS_football_programs','https://en.wikipedia.org/wiki/List_of_NCAA_Division_II_institutions','https://en.wikipedia.org/wiki/List_of_NCAA_Division_III_institutions'],'footballSources':sources,'schools':schools}
(ROOT/'Config/lower-division-schools.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
