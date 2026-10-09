import test from "node:test";
import assert from "node:assert/strict";
import {normalize, extractSkills, analyzeMatch} from "./matcher.mjs";

test("normalize removes URLs and normalizes case",()=>assert.equal(normalize("PYTHON https://a.test X"),"python x"));
test("extract skills handles aliases and word boundaries",()=>{
  assert.deepEqual(extractSkills("Python, PostgreSQL and JS"),["JavaScript","Python","SQL"]);
  assert.ok(!extractSkills("reactivity").includes("React"));
});
test("identical CV and role descriptions match highly",()=>{
  const cv="Python SQL Docker automated testing fastapi javascript rest api";
  const result=analyzeMatch(cv,cv);
  assert.ok(result.overall_score>=95);
  assert.equal(result.missing_skills.length,0);
});
test("empty skills do not yield an inflated perfect score",()=>{
  const result=analyzeMatch("editing photography","accounting finance");
  assert.ok(result.overall_score<40);
});
test("missing relevant skills are reported",()=>{
  const result=analyzeMatch("Python and SQL","Python SQL Docker Kubernetes");
  assert.ok(result.missing_skills.includes("Docker"));
  assert.ok(result.missing_skills.includes("Kubernetes"));
});
