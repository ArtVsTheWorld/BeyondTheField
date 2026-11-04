"""Prewritten recruiting updates and portal reactions, separate from detection."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];families={}
def add(key,*lines):families[key]=[{'id':key+'.recruitcopy.'+str(i+1),'body':line} for i,line in enumerate(dict.fromkeys(lines))]
def forms(key,pattern,*phrases):add(key,*[pattern.replace('~',p) for p in phrases])
def pairs(key,leads,ends):add(key,*[a+' '+b for a in leads for b in ends])

forms('portal.entrant','{position} {playerName} ~{originDetail}. No new destination is confirmed.',
    'is in the transfer portal','has entered the transfer pool','is listed among portal entrants',
    'is on the transfer-portal list','is a portal entrant','appears in the portal pool',
    'is in the pool of transfer recruits','has a transfer-portal entry','is part of the portal class','is listed in the portal')
forms('portal.interest','{position} {playerName} ~ {schools}. No commitment has been made.',
    'currently lists leading schools including','has a leading group including','has interest centered on',
    'lists schools in the mix including','has a current leading group of','is considering a leading group including',
    'has schools at the front including','has leading options including','has a top group including','currently has a leading group including')
pairs('portal.announcement',[
    'I am in the portal and looking for the right next fit.',
    'Entering the portal for the next chapter.',
    'I am in the transfer portal. Ready to find the right opportunity.',
    'The next step for me is the portal.',
    'I am looking for my next opportunity through the transfer portal.'],
    ['Grateful for everyone who supported me{originDetail}.','Appreciate the people who were with me{originDetail}.'])
for key in ['portal.unsigned','portal.unsigned-local']:
    forms(key,'{starDetail}{position} {playerName} is still uncommitted, No. {nationalRecruitRank} nationally. ~',
        'A remaining high school name to track before the next signing day.',
        'One of the unsigned high school players in the offseason recruiting picture.',
        'The high school recruitment remains open.','The next signing day is still ahead.',
        'A player still available on the high school board.','There is another signing-day decision to come.',
        'A remaining high school target as offseason recruiting continues.','The player is still looking for the next school.',
        'An unsigned high school option worth keeping in view.','The recruitment has not reached a commitment yet.')
forms('portal.unsigned-schools','{position} {playerName} remains uncommitted. ~ {schools}.',
    'The current leading group includes','Schools in the current mix include','The leading schools are',
    'The current front group includes','The top group currently includes','The leading options include',
    'Schools at the front of the recruitment include','The current options include',
    'The recruitment\'s leading group includes','The leading-school list includes')
forms('roster.underdog','{school} is involved with 2-star {prospectType}{position} {playerName}{originDetail}. ~',
    'An under-the-radar recruitment with a chance to surprise.','A quieter name on the recruiting board.',
    'Not a headline ranking, but an opportunity to make a different impression.','One of the lower-profile recruitments to follow.',
    'A prospect looking to outperform the early label.','An underdog name in this class.',
    'A less-heralded player worth a closer look.','The stars are a starting point, with the football still ahead.',
    'A quieter story on a busy recruiting board.','A chance to prove more than the initial ranking suggests.')
forms('roster.commit','{school} ~ {starDescription}{prospectType}{position} {playerName}{originDetail}.{recruitRankDetail}',
    'adds','lands a commitment from','gets a commitment from','secures a commitment from','has a new commitment from',
    'picks up','adds a commitment from','receives a commitment from','welcomes a commitment from','has landed')
forms('roster.major','COMMITMENT: {school} ~ 5-star {prospectType}{position} {playerName}{originDetail}.{recruitRankDetail}',
    'lands','adds','secures a commitment from','picks up','receives a commitment from','gets a commitment from',
    'has a commitment from','has landed','has added','wins a commitment from')
forms('roster.rival-transfer','{starDescription}transfer {position} {playerName} ~ {school} from rival {formerSchool}.',
    'has committed to','is committed to','chooses','will head to','has picked','makes the move to',
    'takes the next step with','is headed to','has chosen','has decided on')
forms('roster.destination','Transfer {position} {playerName} ~ {school} after {formerSchool}. {starDescription}addition to the class.',
    'has committed to','is committed to','chooses','will head to','has picked','makes the move to',
    'takes the next step with','is headed to','has chosen','has decided on')
forms('roster.interest','Transfer {position} {playerName}{originDetail} has {schools} in the leading group. ~',
    'There is no commitment yet.','The recruitment remains open.','That is the current interest, not a final decision.',
    'The next school is not confirmed.','The commitment decision is still ahead.','No new destination has been selected.',
    'Interest is not a commitment.','This is the current leading group.','The player has not committed.',
    'A decision remains to be made.')
forms('roster.unsigned','~ {starDescription}{prospectType}{position} {playerName}.{recruitRankDetail}',
    'Still on the board:','An unsigned name to track:','Available in the recruiting class:',
    'The unsigned watch:','Still without a commitment:','One remaining recruiting option:',
    'The open recruitment list includes','A name still in the recruiting mix:',
    'An open recruitment to follow:','On the remaining-prospect list:')
add('roster.offer','AGTG! Blessed to receive an offer from {school}.',
    'All glory to God. Thankful for an offer from {school}.',
    'Blessed with an offer from {school}. Appreciate the opportunity.',
    'AGTG! Thankful to the {school} staff for the offer.',
    'God is good. Blessed to receive an offer from {school}.',
    'Thankful for this journey. Blessed with an offer from {school}.',
    'AGTG. Another opportunity from {school}. Grateful for it.',
    'Blessed with a {school} offer. Thank you to everybody helping me get here.',
    'AGTG! An offer from {school}. A lot to be thankful for.',
    'All glory to God. Appreciate the {school} offer.')
forms('roster.transfer-offer','~ {school}. After my time at {formerSchool}, I am looking for the right next fit.',
    'Grateful for an offer from','Thankful to receive an offer from','Appreciate the offer from',
    'Excited to share an offer from','Happy to receive an offer from','Thankful for the opportunity from',
    'An offer came in from','Appreciate a new opportunity from','Grateful for the opportunity from','Excited about an offer from')
add('roster.announce','Committed to {school}. Thankful for everyone who helped me get here.',
    'My next chapter is {school}. Appreciate all the support.',
    '{school} is home. Excited to get started.', 'Proud to be joining {school}. Committed!',
    'I am committed to {school}. Thank you to my family and coaches.',
    'The decision is {school}. Looking forward to the next chapter.',
    'Excited to call {school} home. Committed.', 'Found my fit at {school}. Thankful for the opportunity.',
    '{school}! Ready to be part of this group.', 'Next stop: {school}. Appreciate everybody who supported the decision.')
forms('roster.transfer-announce','After my time at {formerSchool}, ~ {school}. Grateful for the people who helped me get here.',
    'I am committed to','my next chapter is','I have chosen','I am headed to','I am joining',
    'I have committed to','I am making the move to','I have picked','my next home is','I will continue my career at')
pairs('roster.departure-kind',[
    'Good luck with the next chapter, {targetHandle}.','Wishing you well, {targetHandle}.',
    'Hope the next opportunity is a good one, {targetHandle}.','All the best with what comes next, {targetHandle}.',
    'Good luck at the next stop, {targetHandle}.'],
    ['Appreciate what you gave {school}','Thanks for the time in {school} colors'])
pairs('roster.departure-sour',[
    '{targetHandle} leaving {school} still stings.','I do not have to enjoy {targetHandle} leaving {school}.',
    'The {school} part of me is not happy with this, {targetHandle}.','Not the {school} update I wanted, {targetHandle}.',
    '{targetHandle} moving on from {school}. Yeah that one is frustrating.'],
    ['I will be cheering for the guys who stayed','The farewell is going to need a little time'])
forms('roster.pitch','{targetHandle} ~ {school}.',
    'Come be part of','You would look good at','The next stop should be','Take a good look at',
    'Come check out','We could use you at','Come find your spot at','You should come to',
    'Would love to see you at','There is a fanbase waiting for you at')
pairs('roster.rival-fan',[
    '{targetHandle} from {formerSchool} to {school}? Of all the choices.',
    'The rivalry line too, {targetHandle}? {formerSchool} to {school} is rough to read.',
    '{formerSchool} to {school}. Really, {targetHandle}?','{targetHandle} picked {school} after {formerSchool}. That rivalry game got a little louder.',
    'Not just leaving {formerSchool}, but going to {school}. {targetHandle}, come on.'],
    ['We will remember that on rivalry week','The fanbase is going to have opinions about this'])
pairs('roster.welcome',[
    'Welcome to {school}, {targetHandle}.','Good to have you, {targetHandle}. {school} fans are excited.',
    '{targetHandle} in {school} colors. I like it.','A new chapter at {school}, {targetHandle}. Welcome.',
    '{school} picked up {targetHandle}. Welcome to the group.'],
    ['Ready to see you out there','Looking forward to the next season'])
forms('beat.commit','{position} {playerName} ~ {school}.{recruitRankDetail}{coachDetail}',
    'has committed to','is committed to','chooses','is headed to','has picked','has chosen','has decided on',
    'will join','takes the next step with','has made a commitment to')
forms('beat.recruit_pickup','{school} ~ {starDescription}{position} {playerName}.{recruitRankDetail}',
    'adds','lands a commitment from','secures a commitment from','receives a commitment from','gets a commitment from',
    'picks up','has a commitment from','has landed','has added','welcomes a commitment from')
forms('beat.recruit_questioned','{school} adds {starDescription}{position} {playerName}.{recruitRankDetail} ~',
    'A lower-profile pickup than the program usually targets.','The staff is looking beyond a lower recruiting profile here.',
    'A pickup below this program\'s usual recruiting tier.','It is fair to ask what fit the staff sees beyond the ranking.',
    'This is a less-heralded addition than the school usually brings in.','The recruiting fit deserves a closer look.',
    'A different sort of recruiting bet for a program at this level.','The ranking makes this a surprising addition for this program.',
    'The staff is taking a chance on a less-heralded prospect.','The evaluation has to explain the fit beyond the stars.')

root.joinpath('Content/Runtime/recruiting-variety-pack.json').write_text(json.dumps({'revision':'recruiting-variety-v99','families':families},indent=2)+'\n',encoding='utf-8')
