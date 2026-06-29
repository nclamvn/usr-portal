/* TIP-UX2.1 STEP 0 — THEME_PURITY gate (engine-parametrized; Chromium here, WebKit slot when env has it).
   Một theme MỘT value, không patchwork: render mỗi loại surface ở light + dark; với mỗi CONTAINER
   (block đủ lớn) lấy nền hữu-hiệu (background-color, hoặc rgb-stops của gradient) -> luminance ->
   assert polarity: light = nền sáng (lum > .5), dark = nền tối (lum < .5). Lệch -> exit 2 (THEME_PURITY).
   Chỉ soi BACKGROUND container (w>=240 & h>=120), KHÔNG soi stroke/line/dot/chip nhỏ (đúng chỉ-thị). */
const { spawn } = require("child_process");

const CHROME = process.env.WEBKIT_BIN || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const ENGINE = process.env.THEME_ENGINE || "chromium";
const PORT = 9231;
const BASE = "http://127.0.0.1:8011";
const THRESH = 0.5;                 // luminance split: clearly-light vs clearly-dark
const MINW = 240, MINH = 120;       // a "container" — ignore dots/chips/pills/ribs/lines

// one representative page per surface kind (the home carries hero + masthead + cards + footer).
const SURFACES = [
  "/index.html", "/reference.html", "/data.html", "/compare.html", "/search.html",
  "/knowledge.html", "/review.html", "/news.html", "/monitor.html", "/registry.html",
  "/uav/uav-dji-mavic-3-pro-mavic-3-pro.html",
  "/company/dji.html", "/country/united-states.html", "/segment/military-tactical.html",
  "/news/bai-01-data-note-phuong-phap.html",
];
const COMBOS = ["light", "dark"];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json`);
      const t = await r.json();
      const p = t.find((x) => x.type === "page");
      if (p && p.webSocketDebuggerUrl) return p.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(250);
  }
  throw new Error("CDP not reachable");
}
function cdp(ws) {
  let id = 0; const pend = new Map();
  ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  return (method, params = {}) => new Promise((res) => { const my = ++id; pend.set(my, res); ws.send(JSON.stringify({ id: my, method, params })); });
}
async function evalOnPage(send, expression) {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.result && r.result.exceptionDetails) throw new Error("eval error");
  return r.result.result.value;
}

// in-page auditor: returns offenders = sizable containers whose bg luminance is on the wrong side.
function auditExpr(theme) {
  return `(async () => {
    const h = document.documentElement;
    h.setAttribute('data-theme', ${JSON.stringify(theme)});
    h.setAttribute('data-lang','en');
    document.querySelectorAll('.reveal,[data-draw]').forEach(e=>e.classList.add('is-in'));
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const MINW=${MINW}, MINH=${MINH}, TH=${THRESH}, want=${JSON.stringify(theme)};
    const lum = (r,g,b) => { const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4);};
      return .2126*f(r)+.7152*f(g)+.0722*f(b); };
    const rgbsIn = s => { const out=[]; const re=/rgba?\\(([^)]+)\\)/g; let m;
      while((m=re.exec(s))){const p=m[1].split(',').map(x=>parseFloat(x));
        const a=p.length>3?p[3]:1; if(a>=.5) out.push([p[0],p[1],p[2]]);} return out; };
    const offenders=[];
    for (const el of document.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width < MINW || r.height < MINH) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility==='hidden' || cs.display==='none') continue;
      let cols=[];
      const bc = cs.backgroundColor || '';
      const bm = bc.match(/rgba?\\(([^)]+)\\)/);
      if (bm){ const p=bm[1].split(',').map(x=>parseFloat(x)); const a=p.length>3?p[3]:1; if(a>=.5) cols.push([p[0],p[1],p[2]]); }
      if (cs.backgroundImage && cs.backgroundImage.includes('gradient')) cols=cols.concat(rgbsIn(cs.backgroundImage));
      for (const c of cols){
        const L = lum(c[0],c[1],c[2]);
        const bad = want==='light' ? L < TH : L > TH;
        if (bad){
          const id = (el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.trim().split(/\\s+/).slice(0,3).join('.'):''));
          offenders.push({ sel:id.slice(0,80), lum:+L.toFixed(3), rgb:'rgb('+c.map(Math.round).join(',')+')', w:Math.round(r.width), hgt:Math.round(r.height) });
          break;
        }
      }
    }
    // dedupe by selector+rgb
    const seen=new Set(), uniq=[];
    for (const o of offenders){ const k=o.sel+'|'+o.rgb; if(!seen.has(k)){seen.add(k);uniq.push(o);} }
    return uniq;
  })()`;
}

async function main() {
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`,
    "--hide-scrollbars", "--no-first-run", "--user-data-dir=/tmp/cdp-theme"]);
  let failures = 0;
  try {
    const ws = new WebSocket(await getWsUrl());
    await new Promise((r) => ws.addEventListener("open", r));
    const send = cdp(ws);
    await send("Page.enable"); await send("Runtime.enable");
    console.log(`theme-purity: engine=${ENGINE} · ${SURFACES.length} surfaces × ${COMBOS.length} themes · container >= ${MINW}x${MINH}px`);
    for (const page of SURFACES) {
      for (const theme of COMBOS) {
        await send("Page.navigate", { url: BASE + page });
        await sleep(700);
        let offenders;
        try { offenders = await evalOnPage(send, auditExpr(theme)); }
        catch (e) { offenders = [{ sel: "(eval error)", lum: -1, rgb: "", w: 0, hgt: 0 }]; }
        const ok = offenders.length === 0;
        if (!ok) failures++;
        console.log(`  ${ok ? "PASS" : "FAIL"}  ${page}  [${theme}]  ${ok ? "pure" : offenders.length + " off-value container(s)"}`);
        if (!ok) for (const o of offenders.slice(0, 6))
          console.log(`        · ${o.sel}  bg=${o.rgb} lum=${o.lum}  (${o.w}x${o.hgt})  — should be ${theme}`);
      }
    }
    ws.close();
  } finally { chrome.kill(); }
  if (failures) { console.log(`\nTHEME_PURITY FAIL: ${failures} surface/theme(s) carry an off-value container (patchwork).`); process.exit(2); }
  console.log("THEME_PURITY PASS: every surface is one value per theme — no inverted plate.");
}

module.exports = { auditExpr, getWsUrl, cdp, evalOnPage, CHROME, BASE };
if (require.main === module) main().catch((e) => { console.error(e); process.exit(2); });
