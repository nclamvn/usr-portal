# -*- coding: utf-8 -*-
# INDEPENDENT auditor (Chủ thầu) — verify a Thợ-built site-data.json against the
# live master_registry.json. Does NOT trust the adapter. Fail-loud (exit 2).
# Usage: python3 verify_site_data.py <master_registry.json> <site-data.json>
import json, sys, collections
from canon import canon_country, canonical_slug, ALIAS

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

# schema/2 — the discriminator's domain + the contract's per-type required keys (P0).
ENTITY_TYPES = {"uav", "company", "technology"}
REQUIRED_KEYS = {"uav": ["canonical_id"], "company": ["slug", "name"], "technology": ["slug", "term"]}

# P1.1 — company sourced attributes. When present each MUST be honest-null, a sourced cell
# {value,source,tier(A/B/C)}, or a disputed set {disputed:[≥2 claims]} — never a bare value.
COMPANY_SOURCED = ["legal_name", "founded_year", "hq_country", "hq_city", "hq_address",
                   "website", "founder", "contact_email", "contact_phone"]
TIERS = {"A", "B", "C"}

def cslug(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")

def etype(e):
    # absent entity_type -> "uav" (backward-compat with any site-data/1 reader/producer)
    return e.get("entity_type", "uav")

def claim_values(obj):
    # all distinct claimed values a disputed cell/master-cell carries (invariant #10 currency)
    src = obj.get("claims") or obj.get("sources") or []
    return [c.get("claimed_value") for c in src if c.get("claimed_value") is not None]

def main():
    M=load(sys.argv[1]); S=load(sys.argv[2])
    mc=master_cells(M)
    ents=site_entities(S)
    fails=[]; checked_fields=0

    uav_ents=[e for e in ents if etype(e)=="uav"]

    # 0) discriminator valid + per-type required keys (teeth a/b)
    for e in ents:
        et=etype(e)
        if et not in ENTITY_TYPES:
            fails.append("ENTITY_TYPE: %r not in %s"%(et,sorted(ENTITY_TYPES))); continue
        for req in REQUIRED_KEYS[et]:
            if req not in e or e[req] in (None,"",{}):
                fails.append("%s_REQUIRED: entity missing %r (type=%s)"%(et.upper(),req,et))

    real_count=len(M["variants"])   # all variants public (incl. RtR own_product, labelled)
    # 1) UAV count == all master variants (non-uav entities are out of master's domain)
    if len(uav_ents)!=real_count:
        fails.append("ENTITY COUNT: uav %d != variants %d"%(len(uav_ents),real_count))

    # join by canonical_id
    def cid_of(e):
        c=e.get("canonical_id")
        return c.get("value") if isinstance(c,dict) else c

    for e in ents:
        et=etype(e); cid=cid_of(e) or e.get("slug")
        mcells=mc.get(cid_of(e),{}) if et=="uav" else {}  # only uav cross-checks vs master
        for fname,fc in field_cells(e).items():
            checked_fields+=1
            st=fc.get("status"); val=fc.get("value")
            # 2) honest-null FORWARD (ALL types): unverified/None status must be null on site
            if st in NULL_STATUSES and val is not None:
                fails.append('HONEST-NULL: %s.%s status=%r but value=%r (must be null)'%(cid,fname,st,val))
            # 2b) INVARIANT #10 (ALL types): disputed cell must keep ALL claims, never collapse to one
            if st=="disputed" or fc.get("disputed"):
                if len(claim_values(fc))<2:
                    fails.append('DISPUTED_CLAIM_DROP: %s.%s disputed but keeps %d claim(s) (must keep all, >=2)'
                                 %(cid,fname,len(claim_values(fc))))
            # 3) value fidelity + honest-null REVERSE vs master Cell (uav only)
            mcell=mcells.get(fname)
            if mcell is not None:
                mst=mcell.get("status"); mval=mcell.get("value")
                if mst in NULL_STATUSES and val is not None:
                    fails.append('LEAK: %s.%s is %s in registry but site shows value=%r'%(cid,fname,mst,val))
                # value fidelity — country is canon-compared (P1.2 hygiene normalize is allowed,
                # but ONLY the declared canonical map; any other divergence is still INVENTED).
                sval, smval = (canon_country(val), canon_country(mval)) if fname=="manufacturer_country" else (val, mval)
                if val is not None and mst in SHOW_STATUSES and sval!=smval:
                    fails.append('INVENTED: %s.%s site=%r != registry=%r'%(cid,fname,val,mval))
                # 3b) REVERSE invariant #10: master-disputed field must stay disputed + keep every claim
                if mst=="disputed":
                    if not (st=="disputed" or fc.get("disputed")) or len(claim_values(fc))<len(claim_values(mcell)):
                        fails.append('DISPUTED_CLAIM_DROP: %s.%s registry keeps %d claims, site keeps %d'
                                     %(cid,fname,len(claim_values(mcell)),len(claim_values(fc))))

    # 3b2) ALIAS integrity (P1.2) — every uav's CANONICAL company slug must resolve to a company
    # entity (0 orphan), and every alias key must be a real manufacturer (no dead/typo alias).
    company_slugs={e.get("slug") for e in ents if etype(e)=="company"}
    mfr_set={(e.get("manufacturer") or {}).get("value") for e in uav_ents}
    for e in uav_ents:
        mfr=(e.get("manufacturer") or {}).get("value")
        if mfr and canonical_slug(mfr) not in company_slugs:
            fails.append("ALIAS_ORPHAN: uav %s -> company %r has no entity"%(cid_of(e),canonical_slug(mfr)))
    for k in ALIAS:
        if k not in mfr_set:
            fails.append("ALIAS_ORPHAN: alias key %r is not a manufacturer in the registry"%k)

    # 3c) COMPANY entities (P1.1) — rollup two-way (derived == live) + sourced-attr shape.
    # rollup uav_count is keyed by the CANONICAL slug (alias-merged), matching derive_companies.
    uav_by_mslug=collections.Counter(
        canonical_slug((e.get("manufacturer") or {}).get("value"))
        for e in uav_ents if (e.get("manufacturer") or {}).get("value"))
    for e in ents:
        if etype(e)!="company": continue
        slug=e.get("slug")
        roll=e.get("rollup") or {}
        live=uav_by_mslug.get(slug,0)
        if roll.get("uav_count")!=live:                       # rollup must match live UAV data
            fails.append("ROLLUP: company %s uav_count=%r != live %d (derived must be live)"%(slug,roll.get("uav_count"),live))
        if sorted(roll.get("uav_slugs") or [])!=(roll.get("uav_slugs") or []):
            fails.append("ROLLUP: company %s uav_slugs not sorted (non-idempotent)"%slug)
        for a in COMPANY_SOURCED:                             # sourced-attr shape (no bare values)
            if a not in e: continue
            v=e[a]
            if v is None: continue                            # honest-null OK
            if isinstance(v,dict) and "disputed" in v:        # invariant #10 on company attrs
                claims=[c for c in (v.get("disputed") or []) if c.get("value") is not None]
                if len(claims)<2:
                    fails.append("DISPUTED_CLAIM_DROP: company %s.%s disputed keeps %d claim(s) (>=2)"%(slug,a,len(claims)))
                for c in (v.get("disputed") or []):
                    if not c.get("source") or c.get("tier") not in TIERS:
                        fails.append("SOURCED_ATTR: company %s.%s claim missing source/tier"%(slug,a))
            elif isinstance(v,dict) and "value" in v:         # sourced cell — must carry source+tier
                if not v.get("source") or v.get("tier") not in TIERS:
                    fails.append("SOURCED_ATTR: company %s.%s has value but no source/tier (bare value forbidden)"%(slug,a))
            else:
                fails.append("SOURCED_ATTR: company %s.%s invalid shape (%s)"%(slug,a,type(v).__name__))

    # 4) aggregates computed-live (CONSTRAINT 8) — UAV-scoped (schema/2)
    agg = S.get("aggregates") if isinstance(S,dict) else None
    if agg:
        if agg.get("entity_count") not in (None,len(uav_ents)):
            fails.append("AGGREGATE entity_count=%r != live uav %d (hardcoded?)"%(agg.get("entity_count"),len(uav_ents)))
        # recompute field_status_counts from uav entities
        fsc=collections.Counter()
        for e in uav_ents:
            for _,fc in field_cells(e).items(): fsc[fc.get("status")]+=1
        stored=agg.get("field_status_counts")
        if stored is not None:
            norm={str(k):v for k,v in stored.items()}
            live={str(k):v for k,v in fsc.items()}
            if norm!=live:
                fails.append("AGGREGATE field_status_counts stored=%s != live %s"%(norm,live))

    # --- TIP-P02: frame_glyph audit (uav-scoped) — total mapping + no rotor-count fabrication ---
    import collections as _c
    GLYPHS={"quad","hexa","octo","multirotor","fixed","vtol","heli","ducted","unknown"}
    dist=_c.Counter()
    for e in uav_ents:
        fg=e.get("frame_glyph"); dist[fg]+=1
        if fg not in GLYPHS:
            fails.append("FRAME_GLYPH invalid/empty: %s -> %r"%(cid_of(e),fg))
        at=(e.get("airframe_type") or {}).get("value")
        if at=="multirotor" and fg!="multirotor":
            fails.append("FRAME_GLYPH LEAK: multirotor -> %s (must stay 'multirotor', no rotor count)"%fg)
        if at=="octocopter" and fg!="octo":
            fails.append("FRAME_GLYPH: octocopter -> %s (expect octo)"%fg)
    print("frame_glyph distribution:", dict(sorted(dist.items(), key=lambda kv:(-kv[1],str(kv[0])))), "| sum=%d"%sum(dist.values()))

    # --- TIP-P03: spec_range must be LIVE (== recompute, not hardcoded) + coverage consistency (uav) ---
    spec=S["field_groups"]["spec"]; rng=S["aggregates"].get("spec_range",{})
    recomp={}
    for e in uav_ents:
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
    rp=sum(1 for e in uav_ents for f in spec if (e.get(f) or {}).get("value") is not None)
    if rp!=present:
        fails.append("COVERAGE present recompute %d != aggregate %d"%(rp,present))
    print("spec_range fields: %d | coverage matrix present/total: %d/%d (%d%%)"%(len(rng),present,tot,round(100*present/tot) if tot else 0))
    print("entity_type tally:", dict(_c.Counter(etype(e) for e in ents)))

    print("entities checked: %d | field-cells checked: %d | real expected: %d"%(len(ents),checked_fields,real_count))
    if fails:
        print("\nAUDIT FAIL (%d):"%len(fails))
        for f in fails[:40]: print("  -",f)
        sys.exit(2)
    print("\nAUDIT PASS: count ok · honest-null both directions · no leaked draft values · no invented values · aggregates live.")

if __name__=="__main__":
    main()
