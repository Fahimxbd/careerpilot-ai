import {FIELDS,STATUSES,PRIORITIES,TYPES} from "./store.mjs";
export function normalizeRecord(raw,prev={}){
 const row={};
 for(const field of FIELDS)row[field]=String(raw[field]??(field==="match_score"?"0":"")).trim().slice(0,field==="notes"?5000:500);
 if(!row.company||!row.role)throw Error("Company and role are required.");
 if(!STATUSES.includes(row.status))row.status="Saved";
 if(!PRIORITIES.includes(row.priority))row.priority="Medium";
 if(!TYPES.includes(row.job_type))row.job_type="Remote";
 if(row.contact_email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.contact_email))throw Error("Invalid contact email.");
 if(row.job_url){
  let url;
  try{url=new URL(row.job_url);}catch{throw Error("Enter a valid job URL.");}
  if(!["https:","http:"].includes(url.protocol))throw Error("Only HTTPS or HTTP job URLs are supported.");
 }
 row.match_score=Math.max(0,Math.min(100,Number(row.match_score)||0));
 for(const field of ["applied_date","deadline"])if(row[field]&&!/^\d{4}-\d{2}-\d{2}$/.test(row[field]))throw Error("Invalid date.");
 row.id=prev.id||crypto.randomUUID();
 row.created_at=prev.created_at||new Date().toISOString();
 row.updated_at=new Date().toISOString();
 return row;
}
