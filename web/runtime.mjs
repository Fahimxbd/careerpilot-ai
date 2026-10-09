import {loadRecords,persist} from "./storage.mjs";
import {overview} from "./overview.mjs";
import {applications,applicationRows} from "./applications.mjs";
import {analytics,about,matchPage} from "./other-pages.mjs";
import {recordForm} from "./form.mjs";
export const state={records:[],page:"overview"};
export const names={overview:"Overview",applications:"Applications",match:"CV Match Lab",analytics:"Analytics",about:"About"};
export function toast(message){
 const el=document.querySelector("#toast");el.textContent=message;el.hidden=false;
 clearTimeout(toast.timeout);toast.timeout=setTimeout(()=>{el.hidden=true},3700);
}
export function render(){
 document.querySelector("#page-crumb").textContent=names[state.page];
 document.querySelector("#nav-count").textContent=state.records.length;
 document.querySelectorAll("[data-page]").forEach(el=>{
  el.classList.toggle("active",el.dataset.page===state.page);
  if(el.dataset.page===state.page)el.setAttribute("aria-current","page");else el.removeAttribute("aria-current");
 });
 const views={overview:()=>overview(state.records),applications:()=>applications(state.records),match:matchPage,analytics:()=>analytics(state.records),about};
 document.querySelector("#main").innerHTML='<div class="main-container">'+views[state.page]()+'</div>';
 closeMenu();
}
export function go(page){
 if(!names[page])return;
 state.page=page;location.hash=page;render();window.scrollTo(0,0);
}
export function save(records){
 try{persist(records);state.records=records;render();return true;}
 catch{toast("Unable to save. Check browser storage settings.");return false;}
}
export function openModal(record={}){
 document.querySelector("#dialog-content").innerHTML=recordForm(record);
 document.querySelector("#record-dialog").showModal();
}
export function closeMenu(){
 document.querySelector("#sidebar").classList.remove("open");
 document.querySelector("#backdrop").hidden=true;
 document.querySelector("#menu-toggle").setAttribute("aria-expanded","false");
}
export function refreshList(){
 const area=document.querySelector("#application-results");if(!area)return;
 area.innerHTML=applicationRows(state.records,document.querySelector("#search-apps")?.value||"",document.querySelector("#filter-apps")?.value||"All");
}
export function download(content,filename,mime){
 const url=URL.createObjectURL(new Blob([content],{type:mime}));
 const a=document.createElement("a");a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
const raw=loadRecords();state.records=Array.isArray(raw)?raw:[];
state.page=names[location.hash.slice(1)]?location.hash.slice(1):"overview";
render();
window.addEventListener("hashchange",()=>{const p=location.hash.slice(1);if(names[p]&&state.page!==p){state.page=p;render();}});
window.addEventListener("storage",()=>{const fresh=loadRecords();state.records=Array.isArray(fresh)?fresh:[];render();});
