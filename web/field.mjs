import {escapeHtml as h,STATUSES,PRIORITIES,TYPES} from "./store.mjs";
const names={company:"Company *",role:"Role *",location:"Location",job_type:"Work type",source:"Source",job_url:"Job URL",salary_range:"Salary / rate",status:"Status",priority:"Priority",applied_date:"Applied date",deadline:"Deadline",contact_person:"Contact",contact_email:"Contact email",cv_version:"CV version",match_score:"Match (%)",notes:"Notes / next action"};
export function field(name,record={}){
const value=h(record[name]??"");
let input="";
if(name==="notes")input='<textarea class="control" name="notes" maxlength="5000">'+value+'</textarea>';
else if(["status","priority","job_type"].includes(name)){
const options=({status:STATUSES,priority:PRIORITIES,job_type:TYPES})[name];
const selected=record[name]||({status:"Saved",priority:"Medium",job_type:"Remote"})[name];
input='<select class="control" name="'+name+'">'+options.map(v=>'<option'+(v===selected?' selected':'')+'>'+h(v)+'</option>').join("")+'</select>';
}else{
const type=({contact_email:"email",applied_date:"date",deadline:"date",match_score:"number",job_url:"url"})[name]||"text";
input='<input class="control" type="'+type+'" name="'+name+'" value="'+value+'"'+(["company","role"].includes(name)?" required":"")+(name==="match_score"?' min="0" max="100"':"")+' maxlength="500">';
}
return '<label class="field '+(name==="notes"?"full":"")+'"><span>'+h(names[name])+'</span>'+input+'</label>';
}
