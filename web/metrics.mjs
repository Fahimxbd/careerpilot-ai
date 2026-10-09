import {STATUSES} from "./store.mjs";
const ACTIVE=new Set(["Applied","Screening","Interview","Offer"]);
const RESPONSE=new Set(["Screening","Interview","Offer","Rejected"]);
export function summary(rows){
const statuses=rows.map(r=>r.status);
const applied=statuses.filter(s=>ACTIVE.has(s)||s==="Rejected"||s==="Withdrawn").length;
const scores=rows.map(r=>Number(r.match_score)).filter(Number.isFinite);
return {total:rows.length,active:statuses.filter(s=>ACTIVE.has(s)).length,
interviews:statuses.filter(s=>s==="Interview").length,offers:statuses.filter(s=>s==="Offer").length,
avg_match:scores.length?Math.round(scores.reduce((a,b)=>a+b,0)/scores.length):0,
response_rate:applied?Math.round(100*statuses.filter(s=>RESPONSE.has(s)).length/applied):0};
}
export function counts(rows){return STATUSES.map(status=>({status,count:rows.filter(r=>r.status===status).length}));}
export function recentWeeks(rows){
const start=new Date();start.setUTCHours(0,0,0,0);
start.setUTCDate(start.getUTCDate()-((start.getUTCDay()+6)%7)-35);
return Array.from({length:6},(_,i)=>{
const date=new Date(start);date.setUTCDate(date.getUTCDate()+i*7);
const end=new Date(date);end.setUTCDate(end.getUTCDate()+7);
return {label:date.toLocaleDateString("en",{month:"short",day:"numeric",timeZone:"UTC"}),
count:rows.filter(r=>r.applied_date&&new Date(r.applied_date+"T00:00:00Z")>=date&&new Date(r.applied_date+"T00:00:00Z")<end).length};});
}
export function sourceStats(rows){
const map=new Map();
for(const r of rows){const s=r.source||"Unknown";if(!map.has(s))map.set(s,{source:s,total:0,responses:0});const p=map.get(s);p.total++;if(RESPONSE.has(r.status))p.responses++;}
return [...map.values()].map(v=>({...v,rate:Math.round(v.responses*1000/v.total)/10})).sort((a,b)=>b.rate-a.rate||b.total-a.total);
}
