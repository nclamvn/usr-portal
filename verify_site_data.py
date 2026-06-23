# -*- coding: utf-8 -*-
# INDEPENDENT auditor (Chủ thầu) — verify a Thợ-built site-data.json against the
# live master_registry.json. Does NOT trust the adapter. Fail-loud (exit 2).
# Usage: python3 verify_site_data.py <master_registry.json> <site-data.json>
import json, sys, collections

SHOW_STATUSES = {"verified","derived","disputed","inherited"}  # may carry a value
NULL_STATUSES = {"unverified", None, "absent", "none"}          # MUST be null on site

def load(p): return json.load(open(p))

def master_cells(m):
    # map canonical_id -> {field: cell}; real variants only (exclude own_product)
    fam={f["family_id"]:f for f in m["families"]}
    out={}
    for v in m["variants"]:
        if v.get("provenance_class")=="own_product": continue
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

    real_count=sum(1 for v in M["variants"] if v.get("provenance_class")!="own_product")
    # 1) entity count + no own_product
    if len(ents)!=real_count:
        fails.append("ENTITY COUNT: site-data %d != real entities %d"%(len(ents),real_count))
    for e in ents:
        pc = e.get("provenance_class") or (e.get("provenance_class",{}) or {})
        if (isinstance(pc,dict) and pc.get("value")=="own_product") or pc=="own_product":
            fails.append("OWN_PRODUCT leaked into site-data: %s"%e.get("canonical_id"))

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

    print("entities checked: %d | field-cells checked: %d | real expected: %d"%(len(ents),checked_fields,real_count))
    if fails:
        print("\nAUDIT FAIL (%d):"%len(fails))
        for f in fails[:40]: print("  -",f)
        sys.exit(2)
    print("\nAUDIT PASS: count ok · honest-null both directions · no leaked draft values · no invented values · aggregates live.")

if __name__=="__main__":
    main()
