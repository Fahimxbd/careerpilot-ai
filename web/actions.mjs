import {state,go,save,toast,openModal,download} from "./runtime.mjs";
import {sampleRecords,backupCsv} from "./demo.mjs";
export function act(action){
 if(action==="new"){openModal();return;}
 if(action==="go-match"){go("match");return;}
 if(action==="close-modal"){document.querySelector("#record-dialog").close();return;}
 if(action==="seed"){
  if(state.records.length){toast("Samples load only into an empty workspace.");return;}
  if(save(sampleRecords()))toast("Five fictional applications loaded.");
  return;
 }
 if(action==="reset"){
  if(confirm("Delete all browser applications? Export a backup first.")){if(save([]))toast("Records deleted.");}
  return;
 }
 if(action==="backup"){
  const content=JSON.stringify({format:"careerpilot-backup-v1",exported_at:new Date().toISOString(),records:state.records},null,2);
  download(content,"careerpilot-backup.json","application/json");toast("JSON backup downloaded.");return;
 }
 if(action==="csv"){
  if(!state.records.length){toast("No applications to export.");return;}
  download(backupCsv(state.records),"careerpilot-applications.csv","text/csv;charset=utf-8");toast("CSV exported.");
 }
}
