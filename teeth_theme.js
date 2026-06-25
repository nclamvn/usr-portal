/* TIP-UX2.1 teeth — prove THEME_PURITY bites. Loads the REAL home (light), confirms pure, then injects
   one dark-plate container and re-runs the SAME in-page auditor: it must be caught. Restore -> pure.
   Exercises verify_theme's actual detection logic; no file is mutated. */
const { spawn } = require("child_process");
const { auditExpr, getWsUrl, cdp, evalOnPage, CHROME, BASE } = require("./verify_theme.js");
const PORT = 9232;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`,
    "--hide-scrollbars", "--no-first-run", "--user-data-dir=/tmp/cdp-teeth-theme"]);
  const results = [];
  try {
    // getWsUrl in verify_theme is bound to its own PORT(9231); poll ours directly.
    let wsUrl = null;
    for (let i = 0; i < 40 && !wsUrl; i++) {
      try { const r = await fetch(`http://127.0.0.1:${PORT}/json`); const t = await r.json();
        const p = t.find((x) => x.type === "page"); if (p) wsUrl = p.webSocketDebuggerUrl; } catch (e) {}
      await sleep(250);
    }
    const ws = new WebSocket(wsUrl);
    await new Promise((r) => ws.addEventListener("open", r));
    const send = cdp(ws);
    await send("Page.enable"); await send("Runtime.enable");

    // (restore) real home, light -> pure
    await send("Page.navigate", { url: BASE + "/index.html" }); await sleep(700);
    const clean = await evalOnPage(send, auditExpr("light"));
    results.push(["restore · real home light is pure", clean.length === 0]);

    // (a) inject a dark plate into the light page -> must be caught
    await send("Page.navigate", { url: BASE + "/index.html" }); await sleep(600);
    const bit = await evalOnPage(send, `(async () => {
      const d=document.createElement('div');
      d.style.cssText='position:relative;width:600px;height:300px;background:#15171B';
      document.body.appendChild(d);
      return await ${auditExpr("light")};
    })()`);
    results.push(["inject dark-plate into light → caught", bit.length > 0]);

    ws.close();
  } finally { chrome.kill(); }

  const ok = results.every(([, x]) => x);
  for (const [name, x] of results) console.log(`  ${x ? "BITE" : "MISS"}  ${name}`);
  console.log("TEETH-THEME:", ok ? "PASS — THEME_PURITY has teeth" : "FAIL");
  process.exit(ok ? 0 : 2);
}
main().catch((e) => { console.error(e); process.exit(2); });
