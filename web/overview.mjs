import {escapeHtml as h} from "./store.mjs";
import {summary} from "./metrics.mjs";
import {button,panel,metric,empty,pipeline,activity} from "./components.mjs";
const active=new Set(["Saved","Applied","Screening","Interview"]);
export function overview(rows){
const m=summary(rows);
const queue=rows.filter(r=>active.has(r.status)).sort((a,b)=>["High","Medium","Low"].indexOf(a.priority)-["High","Medium","Low"].indexOf(b.priority)).slice(0,5);
return '<div class="hero"><div><div class="kicker">YOUR CAREER CONTROL CENTER</div><h1>Find your next<br>opportunity.</h1><p>Stay on top of every application. Discover skill gaps. Make every next step count.</p><div class="actions">'+button("＋ Add application","new","primary")+button("✧ Analyze my CV","go-match","ghost")+'</div></div><div class="hero-art"><span>↗</span></div></div>'+
'<div class="grid metrics">'+metric("Total applications",m.total,"Every opportunity tracked")+metric("Active pipeline",m.active,"Applications in progress")+metric("Interviews",m.interviews,"Conversations started")+metric("Offers",m.offers,"Your results")+metric("Average CV match",m.avg_match+"%","Across saved roles")+metric("Response rate",m.response_rate+"%","Of applications submitted")+'</div>'+
(rows.length?'<div class="grid two-col">'+panel("Pipeline overview",pipeline(rows),"By application status")+panel("Weekly activity",activity(rows),"Recent progress")+'</div>'+panel("Next up",queue.length?'<div class="queue">'+queue.map(r=>'<div class="queue-item"><div><div class="company">'+h(r.company)+'</div><div class="role">'+h(r.role)+(r.deadline?" • Deadline "+h(r.deadline):"")+'</div></div><div class="queue-right"><span class="badge '+h(r.status)+'">'+h(r.status)+'</span><div class="tiny">'+h(r.priority||"Medium")+' priority</div></div></div>').join("")+'</div>':empty("All caught up","Keep finding roles that fit."),"Priority queue"):panel("Ready to get started?",empty("Your workspace is ready","Add your first role or explore fictional sample applications.")+'<div class="actions">'+button("Add an application","new","primary")+button("Load sample data","seed")+'</div>'));
}
