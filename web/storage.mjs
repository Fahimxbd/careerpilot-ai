export const KEY = "careerpilot-browser-v1";
export function loadRecords(){try{return JSON.parse(localStorage.getItem(KEY) || "[]");}catch{return [];}}
export function persist(rows){localStorage.setItem(KEY,JSON.stringify(rows));}
