"""Dashboard tests (run: python test_rev3_dashboard.py). Checks that the dashboard
data equals the existing Rev3 results and that the generated HTML/JS is sound."""
import os, sys, json, re, subprocess, tempfile
os.environ["MPLBACKEND"] = "Agg"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, Rev3 as R, rev3_dashboard as D
res = []
def rec(n, ok, d): res.append(ok); print(f"[{'PASS' if ok else 'FAIL'}] {n}\n        {d}")

data = D.collect(R)
with tempfile.TemporaryDirectory() as t:
    out = R.build_dashboard(os.path.join(t, "r.html")); html = open(out, encoding="utf-8").read()
m = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
emb = json.loads(m.group(1).replace("<\\/", "</"))
rec("D1 HTML generated with embedded data", emb == json.loads(json.dumps(data)) and "__DATA__" not in html and "__GENERATED__" not in html, f"{len(html)} bytes")
rec("D2 all 8 load cases present", [c["id"] for c in emb["cases"]] == list(range(1, 9)), str([c["name"] for c in emb["cases"]]))
F = R.R2.to_display_force; ok = True; worst = 0
for c in emb["comp"]:
    vec = R.assemble_load_vector(R.LOAD_CASES_BY_ID[c["case"]]); s = R._sum_components(vec)
    worst = max(worst, max(abs(c[k] - F(v)) for k, v in zip(("sfx", "sfy", "sfz"), s)))
rec("D3 comparison sums equal assemble_load_vector sums", worst < 1e-12, f"max diff {worst:.2e}")
g = [abs(n["x"]) for n in emb["nodes"]]
ok = all(abs(R.R2.to_display_length(R.R2.nodes[n["id"]][0]) - n["x"]) < 1e-12 and abs(R.R2.to_display_length(R._member_length(1)) - emb["members"][0]["length"]) < 1e-12 for n in emb["nodes"])
rec("D4 node coordinates and member lengths match model", ok and len(emb["nodes"]) == 8 and len(emb["members"]) == 12 and emb["dims"] == [6.0, 6.0, 6.0], f"dims {emb['dims']}")
# load arrows: resultant of arrow data == intended load totals
bad = 0
for lc in R.LOAD_CASES:
    intended = R.validate_load_case(lc)[0]; tot = np.zeros(3)
    rows = [l for l in emb["loads"] if l["case"] == lc.id]
    for l in rows:
        v = np.array([l["fx"], l["fy"], l["fz"]])
        if l["kind"].startswith("Distributed"):
            i, j = R._member_end_nodes(int(l["target"].split()[1])); v = v * R._member_length(int(l["target"].split()[1]))
        tot += v
    bad += float(np.max(np.abs(tot - np.array([F(x) for x in intended])))) > 1e-9
rec("D5 per-load table resultants equal intended totals (all 8 cases)", bad == 0, f"{bad} mismatching cases")
rec("D6 combinations: 20 rows, equal assemble_combination", len(emb["combos"]) == 20 and all(abs(c["fy"] - F(R._sum_components(R.assemble_combination(R.LOAD_COMBINATIONS_BY_ID[c["id"]]))[1])) < 1e-12 for c in emb["combos"]), "20 combos")
rec("D7 no unsupported results (reactions/displacements) in data", not any(k in emb for k in ("reactions", "displacements", "member_forces")), "keys: " + ",".join(emb))
# JS logic tests in node (no browser available): syntax, render, CSV, sort-free
js = re.search(r"<script>\n(.*)</script></body>", html, re.S).group(1)
with tempfile.TemporaryDirectory() as t:
    open(os.path.join(t, "d.js"), "w").write("const __DATA__=" + json.dumps(emb) + ";\n" + js)
    open(os.path.join(t, "t.js"), "w").write(r'''
const M=require('./d.js');let calls={};
const ctx=new Proxy({},{get:(o,k)=>k==='measureText'?(s=>({width:s.length*6})):(k in o?o[k]:(...a)=>{calls[k]=(calls[k]||0)+1}),set:(o,k,v)=>{o[k]=v;return true}});
let bad=[];
for(const lc of M.DATA.cases){for(const v of Object.keys(M.PRE)){calls={};const cam=M.newCam();cam.az=M.PRE[v][0];cam.el=M.PRE[v][1];
 const r=M.render(ctx,400,400,cam,lc,{nodes:1,mem:1,len:1,dim:1,lbl:1,face:1});
 const exp=lc.arrows.reduce((n,a)=>n+(a.kind==='dist'?5:1),0);
 if(r.arrows!==exp||!calls.fill||!calls.stroke)bad.push(lc.id+v);}}
// direction fidelity: head-tail direction equals vec direction
for(const lc of M.DATA.cases){const A=M.arrowsFor(lc),src=[];lc.arrows.forEach(a=>{for(let i=0;i<(a.kind==='dist'?5:1);i++)src.push(a.vec)});
 A.forEach((a,i)=>{const d=a.head.map((x,k)=>x-a.tail[k]),n=Math.hypot(...d),m=Math.hypot(...src[i]);
  for(let k=0;k<3;k++)if(Math.abs(d[k]/n-src[i][k]/m)>1e-9)bad.push('dir'+lc.id)});}
// projection: shared camera => identical node screen positions across cases; preset front view puts X to the right
const p0=M.proj({az:0,el:0,zoom:1,px:0,py:0},400,400,[0,0,0]),p1=M.proj({az:0,el:0,zoom:1,px:0,py:0},400,400,[6,0,0]);
if(!(p1[0]>p0[0]&&Math.abs(p1[1]-p0[1])<1e-9))bad.push('front');
const top=M.proj({az:0,el:90,zoom:1,px:0,py:0},400,400,[0,6,0]),bot=M.proj({az:0,el:90,zoom:1,px:0,py:0},400,400,[0,0,0]);
if(Math.abs(top[0]-bot[0])>1e-9||Math.abs(top[1]-bot[1])>1e-9)bad.push('top');
const csv=M.csvOf([{k:'a',h:'A,1'},{k:'b',h:'B'}],[{a:'x"y',b:1.23456789}]);
if(csv!=='"A,1",B\r\n"x""y",1.23456789')bad.push('csv:'+csv);
console.log(bad.length?'FAIL '+bad.join(','):'OK '+M.DATA.cases.length+' cases x '+Object.keys(M.PRE).length+' views rendered');process.exit(bad.length?1:0)''')
    r = subprocess.run(["node", "t.js"], cwd=t, capture_output=True, text=True)
    rec("D8 JS render/projection/CSV logic under node (stub canvas, 8 cases x 7 views)", r.returncode == 0, (r.stdout + r.stderr).strip()[:300])
n = sum(res); print(f"SUMMARY: {n}/{len(res)} dashboard tests passed"); sys.exit(0 if n == len(res) else 1)
