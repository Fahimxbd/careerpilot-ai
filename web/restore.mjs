import {state,save,toast} from "./runtime.mjs";
import {normalizeRecord} from "./validate.mjs";
document.querySelector("#restore-file").addEventListener("change",event=>{
 const file=event.target.files?.[0];event.target.value="";
 if(!file)return;
 if(file.size>3000000){toast("Backup file is too large.");return;}
 file.text().then(text=>{
  let data;try{data=JSON.parse(text);}catch{throw Error("Invalid JSON backup.");}
  if(!data||data.format!=="careerpilot-backup-v1"||!Array.isArray(data.records))throw Error("Not a CareerPilot backup.");
  if(data.records.length>5000)throw Error("Backup has too many records.");
  const rows=data.records.map(item=>normalizeRecord(item,item));
  if(!confirm("Replace "+state.records.length+" saved records with "+rows.length+" from backup?"))return;
  if(save(rows))toast("Backup restored.");
 }).catch(err=>toast(err.message||"Unable to import backup."));
});
