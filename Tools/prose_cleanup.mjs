// Final surface cleanup preserves handles, abbreviations and statistic values.
export function capitalizeSentences(body){
 return body.replace(/^((?:@[A-Za-z0-9_.]+\s+)+)([a-z])/,(_,mentions,letter)=>mentions+letter.toUpperCase()).replace(/(^|\n|[!?]\s+|\.\s+)(["'“‘(]*)([a-z])/g,(all,before,quote,letter,offset,source)=>{
  if(before.startsWith('.')&&/(?:\b(?:vs|No|Mr|Mrs|Dr|Jr|Sr|St|i\.e|e\.g)|\b[A-Z])\.$/i.test(source.slice(0,offset+1)))return all;
  return before+quote+letter.toUpperCase();
 }).replace(/\bi(?=(?:['’](?:m|ve|ll|d))?\b)/g,(letter,offset,source)=>source[offset-1]==='@'||/^i\.e\./.test(source.slice(offset))?letter:'I');
}
