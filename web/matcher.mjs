// Browser-side, deterministic adaptation of the Python CareerPilot matcher.
// No CV or job description leaves the device.
export const SKILLS = {
  "Python":["python"], "JavaScript":["javascript","java script","js"],
  "TypeScript":["typescript","type script","ts"], "Java":["java"], "C++":["c++","cpp"],
  "C#":["c#","c sharp"], "SQL":["sql","mysql","postgresql","postgres","sqlite"],
  "HTML":["html","html5"], "CSS":["css","css3","tailwind","bootstrap"],
  "React":["react","reactjs","react.js"], "Next.js":["next.js","nextjs"],
  "Node.js":["node.js","nodejs","express"], "Django":["django"], "Flask":["flask"],
  "FastAPI":["fastapi","fast api"], "Streamlit":["streamlit"],
  "Git":["git","github","gitlab"], "Docker":["docker","containerization","containers"],
  "Kubernetes":["kubernetes","k8s"], "AWS":["aws","amazon web services"],
  "Azure":["azure"], "GCP":["gcp","google cloud"], "Linux":["linux","ubuntu"],
  "REST APIs":["rest api","rest apis","restful","api development"],
  "Machine Learning":["machine learning","ml"], "Deep Learning":["deep learning","neural network","neural networks"],
  "NLP":["natural language processing","nlp"], "Computer Vision":["computer vision","opencv"],
  "Pandas":["pandas"], "NumPy":["numpy"], "scikit-learn":["scikit-learn","sklearn"],
  "PyTorch":["pytorch","torch"], "TensorFlow":["tensorflow","keras"],
  "Data Analysis":["data analysis","data analytics"],
  "Data Visualization":["data visualization","matplotlib","plotly","power bi","tableau"],
  "Testing":["pytest","unit testing","automated testing","test automation"],
  "CI/CD":["ci/cd","continuous integration","github actions"],
  "Agile":["agile","scrum","kanban"], "WordPress":["wordpress"],
  "SEO":["seo","search engine optimization"], "Firebase":["firebase","firestore"]
};
const STOP_WORDS = new Set(("a about above across after afterwards again against all almost alone along already also although always am among amongst an and another any anyhow anyone anything anyway anywhere are around as at back be became because become becomes becoming been before beforehand behind being below beside besides between beyond both but by can cannot could did do does doing done down during each either else elsewhere enough etc even ever every everyone everything everywhere except few first for former formerly from further had has have having he hence her here hereafter hereby herein hereupon hers herself him himself his how however i if in indeed into is it its itself just keep last latter latterly least less made make many may me meanwhile might mine more moreover most mostly much must my myself namely neither never nevertheless next no nobody none noone nor not nothing now nowhere of off often on once one only onto or other others otherwise our ours ourselves out over own per perhaps please rather same seem seemed seeming seems several she should since so some somehow someone something sometime sometimes somewhere still such than that the their theirs them themselves then thence there thereafter thereby therefore therein thereupon these they this those though through throughout thru thus to together too toward towards under until up upon us very via was we well were what whatever when whence whenever where whereafter whereas whereby wherein whereupon wherever whether which while who whoever whole whom whose why will with within without would yet you your yours yourself yourselves").split(" "));
export function normalize(text) {
  return String(text || "").toLowerCase()
    .replace(/https?:\/\/\S+|www\.\S+/g, " ")
    .replace(/[^a-z0-9+#.\-\s]/g," ").replace(/\s+/g," ").trim();
}
export function extractSkills(text) {
  const input=" "+normalize(text)+" ";
  return Object.entries(SKILLS).filter(([,aliases])=>aliases.some(alias=>{
    const escaped=alias.replace(/[.*+?^\x24{}()|[\]\\]/g,"\\\x24&");
    return new RegExp("(?<![a-z0-9])"+escaped+"(?![a-z0-9])").test(input);
  })).map(([name])=>name).sort();
}
function terms(text) {
  const tokens=(normalize(text).match(/[a-z0-9]{2,}/g)||[]).filter(t=>!STOP_WORDS.has(t));
  return [...tokens,...tokens.slice(1).map((t,i)=>tokens[i]+" "+t)];
}
function tfidfCosine(a,b) {
  const aa=terms(a),bb=terms(b);
  if(!aa.length||!bb.length)return 0;
  const count=list=>{const map=new Map();for(const word of list)map.set(word,(map.get(word)||0)+1);return map;};
  const A=count(aa),B=count(bb);
  const all=new Set([...A.keys(),...B.keys()]);
  let dot=0,normA=0,normB=0;
  for(const word of all) {
    const df=Number(A.has(word))+Number(B.has(word));
    const idf=Math.log((1+2)/(1+df))+1;
    const va=A.has(word)?(1+Math.log(A.get(word)))*idf:0;
    const vb=B.has(word)?(1+Math.log(B.get(word)))*idf:0;
    dot+=va*vb;normA+=va*va;normB+=vb*vb;
  }
  return normA&&normB?Math.min(1,dot/Math.sqrt(normA*normB)):0;
}
export function analyzeMatch(cvText,jobText) {
  const cvSkills=extractSkills(cvText),jobSkills=extractSkills(jobText);
  const matched=jobSkills.filter(s=>cvSkills.includes(s));
  const missing=jobSkills.filter(s=>!cvSkills.includes(s));
  const skillRatio=jobSkills.length?matched.length/jobSkills.length:(normalize(jobText)?0.5:0);
  const similarity=tfidfCosine(cvText,jobText);
  const overall=Math.round((similarity*.65+skillRatio*.35)*100);
  const recommendations=[];
  if(missing.length) recommendations.push("Show real evidence for these missing skills: "+missing.slice(0,5).join(", ")+".");
  if(similarity<.35) recommendations.push("Use relevant language from the job description in your CV where it is truthful.");
  if(cvSkills.length<5) recommendations.push("Add a focused skills section and back up each skill with evidence.");
  if(overall>=75) recommendations.push("Strong fit. Tailor your opening paragraph and share a relevant project.");
  else if(overall>=50) recommendations.push("Moderate fit. Tailor your CV before applying.");
  else recommendations.push("Weak fit today. Develop key skills or prioritize closer matches.");
  return {
    overall_score:Math.max(0,Math.min(100,overall)),
    text_similarity:Math.round(similarity*100),skill_score:Math.round(skillRatio*100),
    matched_skills:matched,missing_skills:missing,cv_skills:cvSkills,job_skills:jobSkills,recommendations
  };
}
