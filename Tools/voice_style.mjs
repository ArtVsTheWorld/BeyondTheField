import {hash} from './story_authors.mjs';
export function personalVoice(account,player){
 const seed=account.styleSeed??hash(account.handle??player?.id??'');
 if(player?.position==='QB'&&player.personality!=='Unpredictable')return 'measured';
 if(player?.personality==='Leader')return seed%4===0?'conversational':'measured';
 if(['Entertainer','Intense'].includes(player?.personality))return seed%3===0?'conversational':'expressive';
 return ['measured','conversational','expressive'][seed%3];
}
export function finishPersonalText(body,style){
 if(style==='measured'&&/[\p{L}\p{N}]$/u.test(body))return body+'.';
 if(style==='conversational')return body.replace(/\.$/,'');
 return body;
}
