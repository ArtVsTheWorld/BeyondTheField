import fs from 'node:fs/promises';
import {readRuntime} from './read_runtime.mjs';
import {buildFeed} from './feed_engine.mjs';
const [input,output]=process.argv.slice(2);
const s=await readRuntime(JSON.parse(await fs.readFile(input,'utf8')));
s.newOffers=[];const f=buildFeed(s);
if(output)await fs.writeFile(output,JSON.stringify(s));
console.log(JSON.stringify({leagueId:s.leagueId,userTeamIndex:s.userTeamIndex,season:s.season,teams:s.teams.length,players:s.players.length,games:s.games.length,performances:s.performances.length,heisman:s.heisman,commitments:s.commitments.length,offers:s.offers.length,events:f.events?.length??0,contentStatus:f.contentStatus??null,stories:f.stories.length,posts:f.posts.length}));
