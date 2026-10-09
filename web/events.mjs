import {state,go,save,toast,openModal,closeMenu,refreshList} from "./runtime.mjs";
import {act} from "./actions.mjs";
import {normalizeRecord} from "./validate.mjs";
import {analyzeMatch} from "./matcher.mjs";
import {matchResults} from "./other-pages.mjs";
document.addEventListener("click",event=>{
 const nav=event.target.closest("[data-page]");if(nav){go(nav.dataset.page);return;}
 const cmd=event.target.closest("[data-action]");if(cmd){act(cmd.dataset.action);return;}
 const edit=event.target.closest("[data-edit]");
 if(edit){const row=state.records.find(r=>String(r.id)===edit.dataset.edit);if(row)openModal(row);return;}
 const remove=event.target.closest("[data-delete]");
 if(remove){
  const row=state.records.find(r=>String(r.id)===remove.dataset.delete);
  if(row&&confirm("Delete "+row.company+" / "+row.role+"?")){
   if(save(state.records.filter(r=>r.id!==row.id)))toast("Application deleted.");
  }
 }
});
document.addEventListener("submit",event=>{
 if(event.target.id==="record-form"){
  event.preventDefault();
  const form=event.target,previous=state.records.find(r=>String(r.id)===form.dataset.id);
  const input=Object.fromEntries(new FormData(form).entries());
  try{
   const row=normalizeRecord(input,previous||{});
   const list=previous?state.records.map(r=>r.id===previous.id?row:r):[row,...state.records];
   if(save(list)){document.querySelector("#record-dialog").close();toast(previous?"Application updated.":"Application saved.");}
  }catch(err){toast(err.message);}
 }
 if(event.target.id==="match-form"){
  event.preventDefault();
  const input=new FormData(event.target),cv=String(input.get("cv")||""),job=String(input.get("job")||"");
  if(!cv.trim()||!job.trim()){toast("Paste both documents.");return;}
  document.querySelector("#match-results").innerHTML=matchResults(analyzeMatch(cv,job));
 }
});
document.addEventListener("input",event=>{if(event.target.id==="search-apps")refreshList();});
document.addEventListener("change",event=>{if(event.target.id==="filter-apps")refreshList();});
const menu=document.querySelector("#menu-toggle"),backdrop=document.querySelector("#backdrop");
menu.addEventListener("click",()=>{
 const open=document.querySelector("#sidebar").classList.toggle("open");
 backdrop.hidden=!open;menu.setAttribute("aria-expanded",String(open));
});
backdrop.addEventListener("click",closeMenu);
