/* TIP-005/A+B — headless designerAudit via Chrome DevTools Protocol.
   No puppeteer/playwright (registry blocked); drives system Chrome over CDP using
   node's built-in fetch + WebSocket (node >= 21). Audits index.html + reference.html
   across 4 combos (theme x lang) after fonts+reveal+scroll. Exit 2 on any overlap.
   Includes a TEETH self-proof: inject an overlap -> must be caught. */
const { spawn } = require("child_process");
const fs = require("fs");

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9222;
const BASE = "http://127.0.0.1:8011";
const PAGES = ["/index.html", "/reference.html"];
const COMBOS = [["light", "en"], ["light", "vn"], ["dark", "en"], ["dark", "vn"]];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json`);
      const targets = await r.json();
      const page = targets.find((t) => t.type === "page");
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(250);
  }
  throw new Error("CDP not reachable");
}

function cdp(ws) {
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  });
  return (method, params = {}) =>
    new Promise((res) => { const myId = ++id; pending.set(myId, res);
      ws.send(JSON.stringify({ id: myId, method, params })); });
}

async function evalOnPage(send, expression) {
  const r = await send("Runtime.evaluate",
    { expression, awaitPromise: true, returnByValue: true });
  if (r.result && r.result.exceptionDetails) throw new Error("eval error");
  return r.result.result.value;
}

// expression run IN the page: set state, wait fonts, force reveal, scroll, audit.
function auditExpr(theme, lang, inject) {
  return `(async () => {
    const h = document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang', ${JSON.stringify(lang)});
    document.querySelectorAll('.reveal,[data-draw]').forEach(e=>e.classList.add('is-in'));
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    ${inject ? `
      const a=document.createElement('span'); a.setAttribute('data-audit','TEETH-a'); a.textContent='OVERLAP-A';
      const b=document.createElement('span'); b.setAttribute('data-audit','TEETH-b'); b.textContent='OVERLAP-B';
      for (const el of [a,b]){ el.style.cssText='position:fixed;left:40px;top:40px;font-size:20px'; document.body.appendChild(el); }
      await new Promise(r=>requestAnimationFrame(r));
    ` : ``}
    return USRBase.designerAudit(document);
  })()`;
}

// FILTERED state: press the first segment facet, then audit the visible row subset.
// Proves filtering creates no overlaps, narrows the set, meets the <100ms perf budget, and
// round-trips its state to the URL (a filtered view is citable).
function filterExpr(theme, lang) {
  return `(async () => {
    const h=document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang', ${JSON.stringify(lang)});
    const tg=document.querySelector('.tg[data-facet="segment"]');
    if(tg) tg.click();
    document.querySelectorAll('.reveal,[data-draw]').forEach(e=>e.classList.add('is-in'));
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const total=document.querySelectorAll('.row-item').length;
    const shown=document.querySelectorAll('.row-item:not(.hidden)').length;
    const urlOk=/[?&]segment=/.test(location.search);
    const hits=USRBase.designerAudit(document);
    return { total, shown, urlOk, ms: window.__regMs, hits };
  })()`;
}

// DETAIL page: audit overlaps + prove the provenance apparatus is present (numbered source
// footnotes + tier badges) and that honest-null cells are shown, never hidden.
function detailExpr(theme, lang) {
  return `(async () => {
    const h=document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang', ${JSON.stringify(lang)});
    document.querySelectorAll('.reveal,[data-draw]').forEach(e=>e.classList.add('is-in'));
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const sources=document.querySelectorAll('.sources li[id^="s"]').length;
    const tiers=document.querySelectorAll('.sources .tierbadge').length;
    const nullChips=document.querySelectorAll('.chip[data-status="absent"], .chip[data-status="unverified"]').length;
    const specRows=document.querySelectorAll('.drow.spec').length;
    const ticks=document.querySelectorAll('.drow.spec .tick').length;
    const nullRails=document.querySelectorAll('.drow.spec .trk.null').length;
    const rngs=document.querySelectorAll('.drow.spec .rng').length;
    const hits=USRBase.designerAudit(document);
    return { sources, tiers, nullChips, specRows, ticks, nullRails, rngs, hits };
  })()`;
}

// EDITORIAL pages (news/analysis): overlap sweep + assert the intelligence signatures present.
function pageAuditExpr(theme, lang) {
  return `(async () => {
    const h=document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang', ${JSON.stringify(lang)});
    document.querySelectorAll('.reveal,[data-draw]').forEach(e=>e.classList.add('is-in'));
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const intel=!!document.querySelector('.intel');
    const echip=!!document.querySelector('.echip');
    const hits=USRBase.designerAudit(document);
    return { intel, echip, hits };
  })()`;
}

// COMPANY page (P1.1): overlap sweep + assert derived rollup (fleet links) + honest-null sourced rows.
function companyExpr(theme, lang) {
  return `(async () => {
    const h=document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang', ${JSON.stringify(lang)});
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const fleet=document.querySelectorAll('.fleet a').length;
    const nulls=document.querySelectorAll('.crow .v.null').length;
    const hits=USRBase.designerAudit(document);
    return { fleet, nulls, hits };
  })()`;
}

async function main() {
  fs.rmSync("/tmp/cdp-profile", { recursive: true, force: true });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`,
    "--user-data-dir=/tmp/cdp-profile", "--no-first-run", "--disable-gpu",
    "--hide-scrollbars", "about:blank"], { stdio: "ignore" });

  let failures = 0, teethOk = false;
  try {
    const wsUrl = await getWsUrl();
    const ws = new WebSocket(wsUrl);
    await new Promise((res, rej) => { ws.addEventListener("open", res); ws.addEventListener("error", rej); });
    const send = cdp(ws);
    await send("Page.enable"); await send("Runtime.enable");

    for (const page of PAGES) {
      await send("Page.navigate", { url: BASE + page });
      await sleep(1200);  // load + fonts
      for (const [theme, lang] of COMBOS) {
        const hits = await evalOnPage(send, auditExpr(theme, lang, false));
        const n = Array.isArray(hits) ? hits.length : -1;
        const ok = n === 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  ${page}  [${theme}/${lang}]  overlaps=${n}` +
          (n > 0 ? "  " + JSON.stringify(hits.slice(0, 3)) : ""));
      }
    }

    // HERO presence — regression guard: the home must carry the approved editorial hero
    // (field + lead headline + a field-file card linking to a real detail page).
    await send("Page.navigate", { url: BASE + "/index.html" });
    await sleep(800);
    // HERO is now the live featured rotator (TIP-HERO-LIVE): the manifesto slide keeps .lead-h; the
    // article slides carry source+tier figures; a CTA leads into the registry. Only one slide is in
    // layout at rest (display:none others) — the overlap sweep above already proves that holds.
    const hero = await evalOnPage(send, `(() => {
      var slides = Array.prototype.slice.call(document.querySelectorAll('.lhero .lhero-slide'));
      var manifesto = slides.filter(s => s.getAttribute('data-kind') === 'manifesto');
      var news = slides.filter(s => s.getAttribute('data-kind') !== 'manifesto');
      // every NEWS slide must carry a source+tier; the manifesto is the only allowed source-less slide
      var newsSourced = news.filter(s => s.querySelector('.tier') && s.querySelector('.nf-svg, svg')).length;
      var inLayout = slides.filter(s => s.getBoundingClientRect().height > 0).length;
      return { lhero: !!document.querySelector('.lhero'), lead: !!document.querySelector('.lhero .lead-h'),
               slides: slides.length, manifesto: manifesto.length, news: news.length, newsSourced: newsSourced,
               inLayout: inLayout, cta: !!document.querySelector('.lhero-foot[href="reference.html"]') };
    })()`);
    // tight NEWSROOM_SOURCED-on-hero: exactly one manifesto, and EVERY news slide is sourced (a news
    // slide that drops its source is caught — not masked by a loose >=2 count).
    const heroOk = hero.lhero && hero.lead && hero.slides >= 3 && hero.manifesto === 1 &&
      hero.news >= 2 && hero.newsSourced === hero.news && hero.cta && hero.inLayout === 1;
    if (!heroOk) failures++;
    console.log(`  ${heroOk ? "PASS" : "FAIL"}  /index.html  [hero]  rotator=${hero.lhero}  manifesto=${hero.manifesto}  ` +
      `news=${hero.news}  news-sourced=${hero.newsSourced}  in-layout-at-rest=${hero.inLayout}  cta=${hero.cta}`);

    // FILTERED state on reference.html — functional + perf + honest-null gate.
    await send("Page.navigate", { url: BASE + "/reference.html" });
    await sleep(1200);
    const fr = await evalOnPage(send, filterExpr("light", "en"));
    const noOverlap = Array.isArray(fr.hits) && fr.hits.length === 0;
    const filtered = fr.shown > 0 && fr.shown < fr.total;       // facet actually narrowed the set
    const perfOk = typeof fr.ms === "number" && fr.ms < 100;    // perf budget
    const urlOk = fr.urlOk === true;                            // state round-tripped to URL
    [noOverlap, filtered, perfOk, urlOk].forEach((ok) => { if (!ok) failures++; });
    console.log(`  ${noOverlap && filtered && perfOk && urlOk ? "PASS" : "FAIL"}  /reference.html  [filtered]  ` +
      `showing=${fr.shown}/${fr.total}  overlaps=${fr.hits.length}  filter=${fr.ms.toFixed(1)}ms` +
      `  url=${urlOk ? "✓" : "✗"}` + (perfOk ? "  <100ms ✓" : "  >=100ms ✗"));

    // DETAIL page (entity/<slug>.html) — overlap + provenance apparatus + honest-null.
    let slug = "";
    try { const sd = await (await fetch(BASE + "/out/site-data.json")).json();
      slug = (sd.entities.find(e => (e.entity_type || "uav") === "uav") || {}).slug; } catch (e) {}
    if (slug) {
      await send("Page.navigate", { url: BASE + "/entity/" + slug + ".html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const dr = await evalOnPage(send, detailExpr(theme, lang));
        // micro-track two-way: every numeric-spec row is EXACTLY one of tick | null-rail | range
        const trackOk = dr.specRows > 0 && (dr.ticks + dr.nullRails + dr.rngs) === dr.specRows;
        const ok = dr.hits.length === 0 && dr.sources > 0 && dr.tiers > 0 && dr.nullChips > 0 && trackOk;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /entity/${slug}  [${theme}/${lang}]  overlaps=${dr.hits.length}  ` +
          `sources=${dr.sources}  honest-null=${dr.nullChips}  tracks=${dr.ticks}tick/${dr.nullRails}null/${dr.rngs}rng of ${dr.specRows}`);
      }
    } else { failures++; console.log("  FAIL  detail page: could not resolve a slug"); }

    // COMPANY page (company/<slug>.html) — overlap + derived rollup + honest-null sourced (P1.1)
    let cslug = "";
    try { const sd = await (await fetch(BASE + "/out/site-data.json")).json();
      const co = sd.entities.filter(e => e.entity_type === "company")
        .sort((a, b) => (b.rollup && b.rollup.uav_count || 0) - (a.rollup && a.rollup.uav_count || 0))[0];
      cslug = co ? co.slug : ""; } catch (e) {}
    if (cslug) {
      await send("Page.navigate", { url: BASE + "/company/" + cslug + ".html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const ok = r.hits.length === 0 && r.fleet > 0 && r.nulls > 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /company/${cslug}  [${theme}/${lang}]  overlaps=${r.hits.length}  fleet=${r.fleet}  honest-null=${r.nulls}`);
      }
    } else { failures++; console.log("  FAIL  company page: could not resolve a slug"); }

    // TAXONOMY pages (country/<slug>, segment/<slug>) — overlap + real index links (P1.4)
    for (const tpath of ["country/united-states", "segment/military-tactical"]) {
      await send("Page.navigate", { url: BASE + "/" + tpath + ".html" });
      await sleep(700);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));  // reuse: hits + fleet(=.tlist a? no)
        const links = await evalOnPage(send, `document.querySelectorAll('.tlist a').length`);
        const ok = r.hits.length === 0 && links > 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /${tpath}  [${theme}/${lang}]  overlaps=${r.hits.length}  links=${links}`);
      }
    }

    // COMPARE page (?uav=a,b) — table renders side-by-side, overlap-clean (P1.3)
    try {
      const sd = await (await fetch(BASE + "/out/compare-data.json")).json();
      const two = sd.uavs.slice(0, 2).map(u => u.slug).join(",");
      await send("Page.navigate", { url: BASE + "/compare.html?uav=" + two });
      await sleep(1000);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const cols = await evalOnPage(send, `document.querySelectorAll('table.cmp thead th').length`);
        const tracks = await evalOnPage(send, `document.querySelectorAll('.cmpcell .track').length`);
        const ok = r.hits.length === 0 && cols >= 3 && tracks > 0;  // 1 label col + 2 uav cols
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /compare?uav=2  [${theme}/${lang}]  overlaps=${r.hits.length}  cols=${cols}  tracks=${tracks}`);
      }
      // empty-state usability: suggestions render on load (not a blank screen) + typing filters
      await send("Page.navigate", { url: BASE + "/compare.html" });
      await sleep(800);
      const sug = await evalOnPage(send, `document.querySelectorAll('#results button').length`);
      const filtered = await evalOnPage(send, `(function(){var q=document.getElementById('q');q.value='puma';q.dispatchEvent(new Event('input'));return document.querySelectorAll('#results button').length;})()`);
      const sok = sug > 0 && filtered > 0;
      if (!sok) failures++;
      console.log(`  ${sok ? "PASS" : "FAIL"}  /compare  [suggestions]  on-load=${sug}  typed'puma'=${filtered}`);
    } catch (e) { failures++; console.log("  FAIL  compare page: " + e.message); }

    // SEARCH page (?q=dji) — multi-type hits, overlap-clean, filter latency (P2.1)
    try {
      await send("Page.navigate", { url: BASE + "/search.html?q=dji" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const hits = await evalOnPage(send, `document.querySelectorAll('.hit a').length`);
        const ms = await evalOnPage(send, `(function(){var q=document.getElementById('q');var t=performance.now();q.value='puma';q.dispatchEvent(new Event('input'));return performance.now()-t;})()`);
        const ok = r.hits.length === 0 && hits > 0 && ms < 100;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /search?q  [${theme}/${lang}]  overlaps=${r.hits.length}  hits=${hits}  filter=${ms.toFixed(1)}ms`);
      }
    } catch (e) { failures++; console.log("  FAIL  search page: " + e.message); }

    // DATA overview (/data) — live distributions + coverage, overlap-clean (P2.3)
    try {
      await send("Page.navigate", { url: BASE + "/data.html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const bars = await evalOnPage(send, `document.querySelectorAll('.brow').length`);
        const cov = await evalOnPage(send, `document.querySelectorAll('.colstrip').length`);
        const ok = r.hits.length === 0 && bars > 0 && cov === 11;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /data  [${theme}/${lang}]  overlaps=${r.hits.length}  bars=${bars}  coverage-cols=${cov}`);
      }
    } catch (e) { failures++; console.log("  FAIL  data page: " + e.message); }

    // KNOWLEDGE term page (knowledge/<slug>) — definition + related, overlap-clean (P3.1)
    try {
      const g = await (await fetch(BASE + "/content/glossary.json")).json();
      const kslug = Object.keys(g.terms)[0].toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
      await send("Page.navigate", { url: BASE + "/knowledge/" + kslug + ".html" });
      await sleep(700);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const hasDef = await evalOnPage(send, `!!document.querySelector('.def')`);
        const ok = r.hits.length === 0 && hasDef;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /knowledge/${kslug}  [${theme}/${lang}]  overlaps=${r.hits.length}  def=${hasDef}`);
      }
    } catch (e) { failures++; console.log("  FAIL  knowledge page: " + e.message); }

    // REVIEW (/review) — spec-derived ranked table + honest-null dims, overlap-clean (P3.2)
    try {
      await send("Page.navigate", { url: BASE + "/review.html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const rows = await evalOnPage(send, `document.querySelectorAll('table.rv tbody tr').length`);
        const nulls = await evalOnPage(send, `document.querySelectorAll('.dim.null').length`);
        const ok = r.hits.length === 0 && rows > 0 && nulls > 0;  // honest-null dims must be visible
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /review  [${theme}/${lang}]  overlaps=${r.hits.length}  rows=${rows}  null-dims=${nulls}`);
      }
    } catch (e) { failures++; console.log("  FAIL  review page: " + e.message); }

    // NEWSROOM objective article (news/bai-*) — real authored content, overlap-clean (P3.3)
    try {
      await send("Page.navigate", { url: BASE + "/news/bai-01-data-note-phuong-phap.html" });
      await sleep(700);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const body = await evalOnPage(send, `document.querySelectorAll('.nbody p').length`);
        const ok = r.hits.length === 0 && body > 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /news/bai-01  [${theme}/${lang}]  overlaps=${r.hits.length}  paras=${body}`);
      }
    } catch (e) { failures++; console.log("  FAIL  newsroom page: " + e.message); }

    // EDITORIAL: analysis (4-questions + entity-chip) + news, overlap-clean light/dark.
    let aslug = "", nslug = "";
    try {
      const c = await (await fetch(BASE + "/content/articles.json")).json();
      const an = c.articles.find((a) => a.type === "analysis");
      const nw = c.articles.find((a) => a.type === "news");
      aslug = an && an.slug; nslug = nw && nw.slug;
    } catch (e) {}
    if (aslug) {
      await send("Page.navigate", { url: BASE + "/analysis/" + aslug + ".html" });
      await sleep(900);
      for (const [t, l] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, pageAuditExpr(t, l));
        const ok = r.hits.length === 0 && r.intel && r.echip;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /analysis/${aslug}  [${t}/${l}]  overlaps=${r.hits.length}  four-questions=${r.intel}  entity-chip=${r.echip}`);
      }
    } else { failures++; console.log("  FAIL  analysis page: no slug"); }
    if (nslug) {
      await send("Page.navigate", { url: BASE + "/news/" + nslug + ".html" });
      await sleep(700);
      const r = await evalOnPage(send, pageAuditExpr("light", "en"));
      const ok = r.hits.length === 0;
      if (!ok) failures++;
      console.log(`  ${ok ? "PASS" : "FAIL"}  /news/${nslug}  [light/en]  overlaps=${r.hits.length}`);
    } else { failures++; console.log("  FAIL  news page: no slug"); }

    // MONITOR (Mode L world map, TIP-L1) — overlap-clean + points plotted + ZERO svg <text>
    // (the discipline that keeps the audit honest) + a real point opens its provenance panel with
    // an http(s) source link. Proves the new surface holds every invariant.
    try {
      await send("Page.navigate", { url: BASE + "/monitor.html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const pins = await evalOnPage(send, `document.querySelectorAll('.mon-pin[data-name]').length`);
        const texts = await evalOnPage(send, `document.querySelectorAll('.mon-svg text').length`);
        const opened = await evalOnPage(send, `(function(){var g=document.querySelector('.mon-pin[data-url]');if(!g)return false;g.dispatchEvent(new MouseEvent('click',{bubbles:true}));var p=document.getElementById('mon-panel');return !p.hidden && document.getElementById('mp-name').textContent.length>0 && document.getElementById('mp-link').getAttribute('href').indexOf('http')===0;})()`);
        const ok = r.hits.length === 0 && pins >= 15 && texts === 0 && opened;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /monitor  [${theme}/${lang}]  overlaps=${r.hits.length}  points=${pins}  svg-text=${texts}  panel→source=${opened}`);
      }
    } catch (e) { failures++; console.log("  FAIL  monitor page: " + e.message); }

    // NEWSROOM FEED (news.html, TIP-NEWSROOM) — editorial frame: overlap-clean + lead/secondary carry
    // source+tier+figure + ZERO borrowed image (every figure is inline SVG generated from data).
    try {
      // measure at DESKTOP width — the column-balance/void only exists in the >=920px two-column layout
      await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 1100, deviceScaleFactor: 1, mobile: false });
      await send("Page.navigate", { url: BASE + "/news.html" });
      await sleep(900);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const m = await evalOnPage(send, `(function(){
          var lead=document.querySelector('article.lead');
          var leadOk = !!lead && !!lead.querySelector('.tier') && !!lead.querySelector('.nf-svg');
          var secs=[].slice.call(document.querySelectorAll('article.sec'));
          var secOk = secs.length>=2 && secs.every(function(s){return s.querySelector('.tier')&&s.querySelector('.nf-svg');});
          var figs=document.querySelectorAll('.nf-svg').length;
          var extImg=[].slice.call(document.querySelectorAll('img')).filter(function(i){return !/^base\\//.test(i.getAttribute('src')||'');}).length;
          var mrows=[].slice.call(document.querySelectorAll('.mrow'));
          var moreSourced = mrows.length>0 && mrows.every(function(r){return r.querySelector('.tier');});
          // void: with align-items:start each column is its own content height; the two should be
          // close so neither half leaves a big empty band (the bug TIP-NEWSROOM.1 fixes).
          var cl=document.querySelector('.col-lead'), cs=document.querySelector('.col-stream');
          var voidPx = (cl&&cs) ? Math.abs(cl.getBoundingClientRect().height - cs.getBoundingClientRect().height) : 999;
          return {leadOk:leadOk, secOk:secOk, figs:figs, extImg:extImg, more:mrows.length, moreSourced:moreSourced, voidPx:Math.round(voidPx)};
        })()`);
        const ok = r.hits.length === 0 && m.leadOk && m.secOk && m.figs >= 3 && m.extImg === 0 &&
          m.more > 0 && m.moreSourced && m.voidPx < 170;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /news.html  [${theme}/${lang}]  overlaps=${r.hits.length}  ` +
          `lead=${m.leadOk}  secondary=${m.secOk}  figures=${m.figs}  more=${m.more}(sourced=${m.moreSourced})  ` +
          `void=${m.voidPx}px  borrowed-img=${m.extImg}`);
      }
    } catch (e) { failures++; console.log("  FAIL  newsroom feed: " + e.message); }

    // HOMEPAGE newsroom block (TIP-NEWSROOM.1 STEP 2) — the compact editorial frame replaced the old
    // card-grid: assert .nfeed-mini present with a sourced lead figure, and ZERO legacy .nr-card.
    try {
      await send("Page.navigate", { url: BASE + "/index.html" });
      await sleep(800);
      const h = await evalOnPage(send, `(function(){
        var mini=document.querySelector('.nfeed-mini');
        return {mini:!!mini, leadFig:!!(mini&&mini.querySelector('.nf-svg')&&mini.querySelector('.tier')),
                oldCards:document.querySelectorAll('.nr-card').length};
      })()`);
      const ok = h.mini && h.leadFig && h.oldCards === 0;
      if (!ok) failures++;
      console.log(`  ${ok ? "PASS" : "FAIL"}  /index.html  [home-news]  nfeed-mini=${h.mini}  sourced-lead=${h.leadFig}  legacy-cards=${h.oldCards}`);
    } catch (e) { failures++; console.log("  FAIL  homepage news block: " + e.message); }
    await send("Emulation.clearDeviceMetricsOverride");

    // REGISTRY surface (TIP-FP1) — Mode-D field-cards: overlap-clean + cards present + each sourced +
    // grouped into desks. (Titles-are-fields / 0-prose is proven statically by verify_registry_cards.)
    try {
      await send("Page.navigate", { url: BASE + "/registry.html" });
      await sleep(800);
      for (const [theme, lang] of [["light", "en"], ["dark", "vn"]]) {
        const r = await evalOnPage(send, companyExpr(theme, lang));
        const m = await evalOnPage(send, `(function(){
          var cards=[].slice.call(document.querySelectorAll('.rcard'));
          var sourced=cards.filter(function(c){return c.querySelector('.tier');}).length;
          var desks=document.querySelectorAll('.rdesk').length;
          var extImg=[].slice.call(document.querySelectorAll('img')).filter(function(i){return !/^base\\//.test(i.getAttribute('src')||'');}).length;
          return {cards:cards.length, sourced:sourced, desks:desks, extImg:extImg};
        })()`);
        const ok = r.hits.length === 0 && m.cards >= 10 && m.sourced === m.cards && m.desks >= 3 && m.extImg === 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  /registry.html  [${theme}/${lang}]  overlaps=${r.hits.length}  ` +
          `cards=${m.cards}  sourced=${m.sourced}  desks=${m.desks}  borrowed-img=${m.extImg}`);
      }
    } catch (e) { failures++; console.log("  FAIL  registry surface: " + e.message); }

    // TEETH: inject a deliberate overlap on index.html — must be caught.
    await send("Page.navigate", { url: BASE + "/index.html" });
    await sleep(1000);
    const teeth = await evalOnPage(send, auditExpr("light", "en", true));
    teethOk = Array.isArray(teeth) && teeth.length > 0;
    console.log(`\n  TEETH-PROOF: injected overlap -> caught=${teeth.length} overlap(s) -> ` +
      (teethOk ? "detected (gate has teeth)" : "NOT CAUGHT (gate toothless!)"));
    // exit-code teeth: under TEETH=1 the injected overlap counts as a real page defect,
    // so the gate must exit non-zero. Proves the EXIT CODE fails on a present overlap.
    if (process.env.TEETH) { failures += teeth.length; }

    ws.close();
  } finally {
    chrome.kill("SIGKILL");
  }

  console.log(`\nAUDIT: ${failures === 0 ? "clean: 8 base + hero + filtered + 2 detail + 2 company + 2 taxonomy + 2 compare + 2 search + 2 data + 2 knowledge + 2 review + 2 newsroom + 3 editorial (news/analysis)" : failures + " issue(s)"} | teeth ${teethOk ? "proven" : "FAILED"}`);
  if (failures > 0 || !teethOk) process.exit(2);
  process.exit(0);
}

main().catch((e) => { console.error("AUDIT ERROR:", e.message); process.exit(3); });
