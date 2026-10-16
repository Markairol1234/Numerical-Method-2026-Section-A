"""rev3_dashboard.py - builds the interactive 3D dashboard (self-contained HTML).

Reads ONLY what Rev3 already computes (geometry, loads, assembled vectors,
equilibrium totals, combinations). No new structural analysis is performed:
reactions / member forces / displacements are not computed by Rev3 (Rev4 scope)
and are therefore not shown.
"""
import datetime as dt
import json
import os
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(_HERE, "rev3_dashboard_template.html")


def collect(R):
    """Collect every displayed quantity from the Rev3 module `R` (display units)."""
    R2 = R.R2
    lab = R2.get_unit_labels()
    fu, lu = lab["force"], lab["length"]
    F, Ln = R2.to_display_force, R2.to_display_length
    mu = f"{fu}*{lu}"
    L1 = Ln(1.0)

    nodes = []
    for n in sorted(R2.nodes):
        x, y, z = (Ln(float(c)) for c in R2.nodes[n])
        fixed = [d for d in R2.DOF_NAMES if R._is_restrained(n, d)]
        nodes.append(dict(id=n, x=x, y=y, z=z,
                          support=("Restrained: " + ",".join(fixed)) if fixed else "-",
                          is_support=bool(fixed)))
    ext = [(min(n[k] for n in nodes), max(n[k] for n in nodes)) for k in "xyz"]
    dims = [b - a for a, b in ext]

    members = []
    for k, (i, j, t) in enumerate(R2.members, start=1):
        members.append(dict(id=k, type=t, i=int(i), j=int(j), length=Ln(R._member_length(k))))
    roof = [n["id"] for n in nodes if abs(n["y"] - ext[1][1]) < 1e-9]

    props = [dict(group="Material (SI)", prop=k, value=float(v))
             for k, v in R2.MATERIAL.items() if isinstance(v, (int, float))]
    props += [dict(group="Section (SI)", prop=k, value=float(v))
              for k, v in R2.SECTION.items() if isinstance(v, (int, float))]

    cases, loads, equiv, comp = [], [], [], []
    for lc in R.LOAD_CASES:
        vec = R.assemble_load_vector(lc)
        intended, computed, err = R.validate_load_case(lc)
        tot = [F(float(c)) for c in computed]
        arrows = []
        for ld in lc.loads:
            if isinstance(ld, R.NodalLoad):
                v = [F(ld.fx), F(ld.fy), F(ld.fz)]
                if not any(v):
                    continue
                pos = [nodes[ld.node_id - 1][k] for k in "xyz"]
                lbl = f"{np.linalg.norm(v):.2f} {fu} @N{ld.node_id}"
                arrows.append(dict(kind="nodal", pos=pos, vec=v, label=lbl))
                loads.append(dict(case=lc.id, kind="Nodal", target=f"Node {ld.node_id}", a="",
                                  fx=v[0], fy=v[1], fz=v[2], unit=fu))
            elif isinstance(ld, R.MemberDistributedLoad):
                w = [F(c) / L1 for c in ld.signed_vector()]
                i, j = R._member_end_nodes(ld.member_id)
                pi, pj = (np.array([nodes[n - 1][k] for k in "xyz"]) for n in (i, j))
                lbl = f"{np.linalg.norm(w):.2f} {fu}/{lu}  M{ld.member_id}"
                arrows.append(dict(kind="dist", p0=list(pi), p1=list(pj), vec=w, label=lbl))
                loads.append(dict(case=lc.id, kind="Distributed (uniform)", target=f"Member {ld.member_id}",
                                  a="", fx=w[0], fy=w[1], fz=w[2], unit=f"{fu}/{lu}"))
            elif isinstance(ld, R.MemberPointLoad):
                v = [F(c) for c in ld.signed_vector()]
                i, j = R._member_end_nodes(ld.member_id)
                pi, pj = (np.array([nodes[n - 1][k] for k in "xyz"]) for n in (i, j))
                pos = list(pi + (pj - pi) * ld.location)
                lbl = f"{np.linalg.norm(v):.2f} {fu}  M{ld.member_id} @a={ld.location:.2f}"
                arrows.append(dict(kind="point", pos=pos, vec=v, label=lbl))
                loads.append(dict(case=lc.id, kind="Member point", target=f"Member {ld.member_id}",
                                  a=ld.location, fx=v[0], fy=v[1], fz=v[2], unit=fu))
        if lc.self_weight:
            sw = R.self_weight_nodal_forces() * lc.self_weight_factor
            first = True
            for n in nodes:
                fy = F(float(sw[R._full_dof_index(n["id"], "Uy")]))
                lbl = (f"Self-weight {abs(F(R.total_self_weight_n() * lc.self_weight_factor)):.2f} {fu} total"
                       if first else None)
                first = False
                arrows.append(dict(kind="self", pos=[n["x"], n["y"], n["z"]], vec=[0.0, fy, 0.0], label=lbl))
                loads.append(dict(case=lc.id, kind="Self-weight (equiv. nodal)", target=f"Node {n['id']}",
                                  a="", fx=0.0, fy=fy, fz=0.0, unit=fu))
        maxf = maxm = 0.0
        for n in nodes:
            ix = [R._full_dof_index(n["id"], d) for d in R2.DOF_NAMES]
            fv = [F(float(vec[k])) for k in ix[:3]]
            mv = [F(float(vec[k])) * L1 for k in ix[3:]]
            equiv.append(dict(case=lc.id, node=n["id"], fx=fv[0], fy=fv[1], fz=fv[2],
                              mx=mv[0], my=mv[1], mz=mv[2]))
            maxf = max(maxf, float(np.linalg.norm(fv)))
            maxm = max(maxm, float(np.linalg.norm(mv)))
        res = float(np.linalg.norm(tot))
        cases.append(dict(id=lc.id, name=lc.name, category=lc.category, desc=lc.description,
                          arrows=arrows, tot=tot,
                          summary=f"{lc.category}: {lc.description}"))
        comp.append(dict(case=lc.id, name=lc.name, category=lc.category, sfx=tot[0], sfy=tot[1],
                         sfz=tot[2], res=res, maxf=maxf, maxm=maxm, err=err))

    combos = []
    for c in R.LOAD_COMBINATIONS:
        _, computed, err = R.validate_combination(c)
        t = [F(float(v)) for v in computed]
        fac = ", ".join(f"LC{k}x{R._fmt_factor(f)}" for k, f in sorted(c.factors.items()))
        combos.append(dict(id=c.id, method=c.design_method, name=c.name, factors=fac,
                           fx=t[0], fy=t[1], fz=t[2], err=err))

    def gov(rows, key, what, idf):
        r = max(rows, key=lambda q: abs(q[key]))
        return dict(label=what, value=r[key], who=idf(r))
    govs = [gov(comp, "sfx", f"Max |sum Fx| ({fu})", lambda r: f"LC{r['case']} {r['name']}"),
            gov(comp, "sfy", f"Max |sum Fy| ({fu})", lambda r: f"LC{r['case']} {r['name']}"),
            gov(comp, "sfz", f"Max |sum Fz| ({fu})", lambda r: f"LC{r['case']} {r['name']}"),
            gov(comp, "maxf", f"Max equiv. nodal force ({fu})", lambda r: f"LC{r['case']} {r['name']}"),
            gov(combos, "fy", f"Max |sum Fy| of combinations ({fu})", lambda r: r["name"]),
            gov(combos, "fx", f"Max |sum Fx| of combinations ({fu})", lambda r: r["name"])]
    nb = sum(1 for m in members if m["type"] == "Beam")
    return dict(units=dict(force=fu, length=lu, moment=mu, system=R2.UNIT_SYSTEM),
                nodes=nodes, members=members, roof=roof, dims=dims, props=props,
                cases=cases, loads=loads, equiv=equiv, comp=comp, combos=combos, gov=govs,
                counts=dict(nodes=len(nodes), members=len(members), beams=nb,
                            columns=len(members) - nb, cases=len(cases), combos=len(combos),
                            supports=sum(1 for n in nodes if n["is_support"])))


def build_html(data):
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        t = f.read()
    blob = json.dumps(data).replace("</", "<\\/")
    return (t.replace("__DATA__", blob)
             .replace("__GENERATED__", f"{dt.datetime.now():%Y-%m-%d %H:%M}"))


def write_dashboard(R, out_html):
    html = build_html(collect(R))
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return out_html
