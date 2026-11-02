// Explicit development font test only. Never configured by the production exporter.
import fs from 'node:fs/promises';
import {readRuntime} from './read_runtime.mjs';
import {publishWeek,buildCatalog} from './feed_selection.mjs';
import {weekKey} from './story_events.mjs';
const [input,output]=process.argv.slice(2);
const s=await readRuntime(JSON.parse(await fs.readFile(input,'utf8')));
const bodies=[
 ['Text and symbol control','ASCII: TOUCHDOWN! | UTF-8: café – it’s gameday.\nSymbols: star [★] check [✓] arrow [→] heart [♡] smile [☺]'],
 ['Single-codepoint emoji','Football [🏈]  Fire [🔥]  Trophy [🏆]\nClap [👏]  Raised hands [🙌]  Eyes [👀]'],
 ['Variation and sequence test','Heart text [♥]  Heart emoji [❤️]  Sun [☀️]\nSkin tone [👏🏽]  Flag [🇺🇸]  ZWJ [👨‍👩‍👧]']
];
const feed=publishWeek({format:1,engineVersion:2,key:weekKey(s),leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,season:s.season.CurrentSeasonYear,week:s.season.CurrentWeek,phase:s.season.CurrentWeekType,source:s.source,sourceKind:'runtime',sourceUnchanged:true,sha256:s.sha256,conference:null,contentStatus:'emoji-probe',stories:bodies.map(([author,body],i)=>({id:'font-probe:'+i,author,handle:'@DynastyEnhancer',body,stamp:'Font Test',imageLibrary:79,imageValue:598,category:'status',scopes:['national','conference','team'],priority:100-i}))});
feed.views.all=feed.stories.map(p=>p.id);feed.posts=feed.stories;
await fs.writeFile(output,JSON.stringify(buildCatalog(feed)));
console.log('Temporary emoji probe; no archives modified');
