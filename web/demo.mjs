import {normalizeRecord} from "./validate.mjs";
export function sampleRecords(){return [
{company:"Nordic Byte Labs",role:"Junior Python Developer",location:"Helsinki, Finland",job_type:"Hybrid",source:"LinkedIn",status:"Applied",applied_date:"2026-07-03",priority:"High",match_score:78,cv_version:"CV-Python-v2",notes:"Fictional example only."},
{company:"Arctic Analytics",role:"Data Analyst Intern",location:"Remote / Finland",job_type:"Remote",source:"Company website",status:"Interview",applied_date:"2026-06-27",priority:"High",match_score:72,notes:"Fictional example only."},
{company:"Saimaa Software",role:"WordPress Support Assistant",location:"Lappeenranta, Finland",job_type:"Part-time",source:"Direct outreach",status:"Screening",applied_date:"2026-07-08",priority:"Medium",match_score:84,notes:"Fictional example only."},
{company:"Cloudberry Tech",role:"Machine Learning Trainee",location:"Espoo, Finland",job_type:"Hybrid",source:"Job board",status:"Saved",deadline:"2026-07-30",priority:"Medium",match_score:61,notes:"Fictional example only."},
{company:"Polar Commerce",role:"Technical Support Intern",location:"Remote",job_type:"Remote",source:"Referral",status:"Rejected",applied_date:"2026-06-15",priority:"Low",match_score:69,notes:"Fictional example only."}
].map(r=>normalizeRecord(r));}
export function backupCsv(records) {
const columns=["company","role","location","job_type","source","job_url","salary_range","status","priority","applied_date","deadline","contact_person","contact_email","cv_version","match_score","notes"];
const cell=v=>{let s=String(v??"");if(/^[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
return [columns.join(","),...records.map(r=>columns.map(c=>cell(r[c])).join(","))].join("\r\n");
}
