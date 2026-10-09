import {field} from "./field.mjs";
import {escapeHtml as h} from "./store.mjs";
export function recordForm(record={}){
 const fields=["company","role","location","job_type","source","job_url","salary_range","status","priority","applied_date","deadline","contact_person","contact_email","cv_version","match_score","notes"];
 return '<div class="dialog-body"><div class="dialog-head"><h2 id="dialog-title">'+(record.id?"Edit application":"New application")+'</h2><button type="button" class="icon-btn" data-action="close-modal" aria-label="Close">×</button></div><form id="record-form" data-id="'+h(record.id||"")+'"><div class="form-grid">'+fields.map(f=>field(f,record)).join("")+'</div><div class="dialog-actions"><button type="button" class="btn ghost" data-action="close-modal">Cancel</button><button type="submit" class="btn primary">Save application</button></div></form></div>';
}
