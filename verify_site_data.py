# -*- coding: utf-8 -*-
# INDEPENDENT auditor (Chủ thầu) — verify a Thợ-built site-data.json against the
# live master_registry.json. Does NOT trust the adapter. Fail-loud (exit 2).
# Usage: python3 verify_site_data.py <master_registry.json> <site-data.json>
import json, sys, collections

SHOW_STATUSES = {"verified","derived","disputed","inherited"}  # may carry a value
NULL_STATUSES = {"unverified", None, "absent", "none"}          # MUST be null on site

def load(p): return json.load(open(p))

def master_cells(m):
    # map canonical_id -> {field: cell}; ALL variants now public (own_product surfaced as "RtR product")
    fam={f["family_id"]:f for f in m["families"]}
    out={}
    for v in m["variants"]:
        cid=v.get("canonical_id") or (v.get("cells",{}).get("canonical_id",{}) or {}).get("value")
        cells=dict(v.get("cells",{}))
        f=fam.get(v["family_id"],{})
        for k,c in f.get("cells",{}).items(): cells.setdefault(k,c)  # inherited family fields
        out[cid]={k:c for k,c in cells.items()}
    return out

def site_entities(s):
    ents = s["entities"] if isinstance(s,dict) and "entities" in s else (s if isinstance(s,list) else s.get("data"))
    return ents

def field_cells(entity):
    # any sub-dict with both 'value' and 'status' is a field-cell
    out={}
    for k,val in entity.items():
        if isinstance(val,dict) and "status" in val and "value" in val:
            out[k]=val
    return out

def main():
    M=load(sys.argv[1]); S=load(sys.argv[2])
    mc=master_cells(M)
    ents=site_entities(S)
    fails=[]; checked_fields=0

    real_count=len(M["variants"])   # all variants public now (incl. RtR own_product, labelled)
    # 1) entity count == all variants
    if len(ents)!=real_count:
        fails.append("ENTITY COUNT: site-data %d != variants %d"%(len(ents),real_count))

    # join by canonical_id
    def cid_of(e):
        c=e.get("canonical_id")
        return c.get("value") if isinstance(c,dict) else c

    for e in ents:
        cid=cid_of(e); mcells=mc.get(cid,{})
        for fname,fc in field_cells(e).items():
            checked_fields+=1
            st=fc.get("status"); val=fc.get("value")
            # 2) honest-null FORWARD: unverified/None status must be null on site
            if st in NULL_STATUSES and val is not None:
                fails.append('HONEST-NULL: %s.%s status=%r but value=%r (must be null)'%(cid,fname,st,val))
            # 3) value fidelity + honest-null REVERSE vs master Cell
            mcell=mcells.get(fname)
            if mcell is not None:
                mst=mcell.get("status"); mval=mcell.get("value")
                if mst in NULL_STATUSES and val is not None:
                    fails.append('LEAK: %s.%s is %s in registry but site shows value=%r'%(cid,fname,mst,val))
                if val is not None and mst in SHOW_STATUSES and val!=mval:
                    fails.append('INVENTED: %s.%s site=%r != registry=%r'%(cid,fname,val,mval))

    # 4) aggregates computed-live (CONSTRAINT 8)
    agg = S.get("aggregates") if isinstance(S,dict) else None
    if agg:
        live_count=len(ents)
        if agg.get("entity_count") not in (None,live_count):
            fails.append("AGGREGATE entity_count=%r != live %d (hardcoded?)"%(agg.get("entity_count"),live_count))
        # recompute field_status_counts from site-data
        fsc=collections.Counter()
        for e in ents:
            for _,fc in field_cells(e).items(): fsc[fc.get("status")]+=1
        stored=agg.get("field_status_counts")
        if stored is not None:
            norm={str(k):v for k,v in stored.items()}
            live={str(k):v for k,v in fsc.items()}
            if norm!=live:
                fails.append("AGGREGATE field_status_counts stored=%s != live %s"%(norm,live))

    # --- TIP-P02: frame_glyph audit (fail-loud) — total mapping + no rotor-count fabrication ---
    import collections as _c
    GLYPHS={"quad","hexa","octo","multirotor","fixed","vtol","heli","ducted","unknown"}
    dist=_c.Counter()
    for e in ents:
        fg=e.get("frame_glyph"); dist[fg]+=1
        if fg not in GLYPHS:
            fails.append("FRAME_GLYPH invalid/empty: %s -> %r"%(cid_of(e),fg))
        at=(e.get("airframe_type") or {}).get("value")
        if at=="multirotor" and fg!="multirotor":
            fails.append("FRAME_GLYPH LEAK: multirotor -> %s (must stay 'multirotor', no rotor count)"%fg)
        if at=="octocopter" and fg!="octo":
            fails.append("FRAME_GLYPH: octocopter -> %s (expect octo)"%fg)
    print("frame_glyph distribution:", dict(sorted(dist.items(), key=lambda kv:(-kv[1],str(kv[0])))), "| sum=%d"%sum(dist.values()))

    # --- TIP-P03: spec_range must be LIVE (== recompute, not hardcoded) + coverage consistency ---
    spec=S["field_groups"]["spec"]; rng=S["aggregates"].get("spec_range",{})
    recomp={}
    for e in ents:
        for f in spec:
            v=(e.get(f) or {}).get("value")
            if isinstance(v,(int,float)) and not isinstance(v,bool):
                r=recomp.setdefault(f,[v,v]); r[0]=min(r[0],v); r[1]=max(r[1],v)
    for f,(lo,hi) in recomp.items():
        sr=rng.get(f)
        if not sr or sr.get("min")!=lo or sr.get("max")!=hi:
            fails.append("SPEC_RANGE %s stored=%s != live min=%s max=%s (hardcoded?)"%(f,sr,lo,hi))
    fillagg=S["aggregates"]["spec_fill_rate"]
    present=sum(d["present"] for d in fillagg.values()); tot=sum(d["total"] for d in fillagg.values())
    rp=sum(1 for e in ents for f in spec if (e.get(f) or {}).get("value") is not None)
    if rp!=present:
        fails.append("COVERAGE present recompute %d != aggregate %d"%(rp,present))
    print("spec_range fields: %d | coverage matrix present/total: %d/%d (%d%%)"%(len(rng),present,tot,round(100*present/tot) if tot else 0))

    print("entities checked: %d | field-cells checked: %d | real expected: %d"%(len(ents),checked_fields,real_count))
    if fails:
        print("\nAUDIT FAIL (%d):"%len(fails))
        for f in fails[:40]: print("  -",f)
        sys.exit(2)
    print("\nAUDIT PASS: count ok · honest-null both directions · no leaked draft values · no invented values · aggregates live.")

if __name__=="__main__":
    main()
