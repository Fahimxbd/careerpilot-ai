export const STATUSES=["Saved","Applied","Screening","Interview","Offer","Rejected","Withdrawn"];
export const PRIORITIES=["Low","Medium","High"];
export const TYPES=["Remote","Hybrid","On-site","Part-time","Internship","Contract"];
export const FIELDS=["company","role","location","job_type","source","job_url","salary_range","status","priority","applied_date","deadline","contact_person","contact_email","cv_version","match_score","notes"];
export function escapeHtml(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
