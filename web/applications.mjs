import {escapeHtml as h,STATUSES} from "./store.mjs";
import {button,heading,empty} from "./components.mjs";
export function applicationRows(rows,q="",filter="All"){
const query=q.trim().toLowerCase();
const sorted=rows.filter(r=>(filter==="All"||r.status===filter)&&(!query||[r.company,r.role,r.location,r.source].some(v=>String(v||"").toLowerCase().includes(query)))).sort((a,b)=>String(b.updated_at||"").localeCompare(String(a.updated_at||"")));
if(!sorted.length)return empty("No matching applications","Try another filter or add your first application.");
return '<div class="table-scroll"><table class="data-table"><thead><tr><th>Company / Role</th><th>Status</th><th>Priority</th><th>Applied</th><th>Match</th><th>Actions</th></tr></thead><tbody>'+
sorted.map(r=>'<tr><td><strong>'+h(r.company)+'</strong><br><span class="tiny">'+h(r.role)+'</span></td><td><span class="badge '+h(r.status)+'">'+h(r.status)+'</span></td><td><span class="badge '+h(r.priority)+'">'+h(r.priority)+'</span></td><td>'+h(r.applied_date||"—")+'</td><td>'+Math.max(0,Math.min(100,Number(r.match_score)||0))+'%</td><td><button type="button" class="btn small" data-edit="'+h(r.id)+'">Edit</button><button type="button" class="btn small danger" data-delete="'+h(r.id)+'">Delete</button></td></tr>').join("")+'</tbody></table></div>';
}
export function applications(rows){
return heading("APPLICATION COMMAND CENTER","Application pipeline","Manage opportunities, deadlines and follow-ups in one private workspace.")+
'<div class="panel"><div class="panel-head"><h2>All applications <span class="tiny">('+rows.length+')</span></h2>'+button("＋ New application","new","primary")+'</div><div class="search-row"><input class="control" id="search-apps" type="search" placeholder="Search company, role, location…" aria-label="Search applications"><select class="control" id="filter-apps" aria-label="Filter status"><option>All</option>'+STATUSES.map(s=>'<option>'+s+'</option>').join("")+'</select>'+button("Export CSV","csv")+'</div><div id="application-results">'+applicationRows(rows)+'</div></div>';
}
