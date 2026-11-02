// Applied to final prose and stored editions. Whole words keep names such as
// Massachusetts, Dickerson and Shittu intact, and handles remain unchanged.
const equivalents={fucking:'fricking',fucked:'messed up',fuck:'frick',fucks:'fricks',bullshit:'nonsense',shitty:'lousy',shit:'trash',shits:'trash',goddamn:'gosh darn',goddamned:'gosh darn',damned:'darned',damn:'dang',hell:'heck',bitch:'jerk',bitches:'jerks',bitching:'complaining',asshole:'jerk',assholes:'jerks',ass:'butt',bastard:'jerk',bastards:'jerks',crap:'crud',pissed:'ticked off',piss:'crud',wtf:'what the heck'};
const words=new RegExp('\\b('+Object.keys(equivalents).sort((a,b)=>b.length-a.length).join('|')+')\\b','gi');
export function cleanLanguage(body){return body.replace(words,(word,_,offset,source)=>{
 if(source[offset-1]==='@')return word;
 const text=equivalents[word.toLowerCase()];return word===word.toUpperCase()?text.toUpperCase():word[0]===word[0].toUpperCase()?text[0].toUpperCase()+text.slice(1):text;
});}
export function cleanFeedLanguage(feed){
 let changed=false;const stories=feed.stories.map(p=>{const body=cleanLanguage(p.body),rawBody=p.rawBody?cleanLanguage(p.rawBody):p.rawBody;if(body===p.body&&rawBody===p.rawBody)return p;changed=true;return {...p,body,...(p.rawBody?{rawBody}:{})};});
 if(!changed)return feed;const map=new Map(stories.map(p=>[p.id,p]));return {...feed,stories,posts:(feed.views?.all??feed.posts?.map(p=>p.id)??[]).map(id=>map.get(id)).filter(Boolean)};
}
