import {escapeHtml as h,STATUSES} from "./store.mjs";
import {counts,recentWeeks} from "./metrics.mjs";
export const button=(text,action,extra="")=>'<button type="button" class="btn '+extra+'" data-action="'+action+'">'+text+'</button>';
export const heading=(k,title,body)=>'<div class="section-top"><div><div class="kicker">'+k+'</div><h1>'+title+'</h1><p class="subtitle">'+body+'</p></div></div>';
export const panel=(title,body,description="")=>'<section class="panel"><div class="panel-head"><h2>'+title+'</h2><small>'+description+'</small></div>'+body+'</section>';
export const metric=(label,value,note)=>'<div class="metric"><div class="metric-label">'+label+'</div><div class="metric-value">'+h(value)+'</div><div class="metric-hint">'+note+'</div></div>';
export const empty=(title,body)=>'<div class="empty"><div class="empty-icon">+</div><h3>'+title+'</h3><p>'+body+'</p></div>';
export function pipeline(rows){
const cs=counts(rows),max=Math.max(1,...cs.map(x=>x.count));
return '<div class="pipeline-list">'+cs.map(x=>'<div class="pipeline-row"><span class="pipeline-label">'+h(x.status)+'</span><div class="pipeline-track"><div class="pipeline-fill" style="width:'+Math.round(x.count*100/max)+'%"></div></div><span class="pipeline-number">'+x.count+'</span></div>').join("")+'</div>';
}
export function activity(rows){
const weeks=recentWeeks(rows),max=Math.max(1,...weeks.map(x=>x.count));
return '<div class="activity-chart">'+weeks.map(x=>'<div class="activity-col"><div class="activity-bar" style="height:'+Math.max(2,Math.round(x.count*135/max))+'px" title="'+x.count+' applications"></div><small>'+h(x.label)+'</small></div>').join("")+'</div><div class="chart-foot">Applications submitted over the last six weeks</div>';
}
