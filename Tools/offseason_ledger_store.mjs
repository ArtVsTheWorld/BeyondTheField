import fs from 'node:fs/promises';
import path from 'node:path';
export function offseasonLedgerFile(folder,s){
 if(!Number.isInteger(s.leagueId)||!Number.isInteger(s.userTeamIndex))throw Error('Invalid ledger path identity');
 return path.join(folder,'RuntimeHistory',String(s.leagueId),String(s.userTeamIndex),'offseason-ledger.json');
}
export async function readOffseasonLedger(file){
 try{const stat=await fs.stat(file);if(stat.size>64*1024*1024)throw Error('Offseason ledger exceeds bounds');return JSON.parse(await fs.readFile(file,'utf8'));}
 catch(e){if(e.code==='ENOENT')return null;throw e;}
}
