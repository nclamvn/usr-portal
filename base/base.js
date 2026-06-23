/* TIP-001 — Design-system base behaviours.
   Exports (window.USRBase): arrow(), designerAudit(), initI18n(), initTheme(), initReveal().
   No framework. Browser-only (getBBox / getBoundingClientRect). */
(function (root) {
  "use strict";

  /* Canonical arrow: SVG shaft + chevron. NEVER a unicode arrow glyph. */
  var ARROW_NS = "http://www.w3.org/2000/svg";
  function arrow() {
    // canonical geometry reconciled to portal-in-action.html (STEP 0):
    // shaft + chevron as a single path  M4.5 12H16.5 M11 6.5 L16.5 12 L11 17.5
    var svg = document.createElementNS(ARROW_NS, "svg");
    svg.setAttribute("class", "arrow");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    var p = document.createElementNS(ARROW_NS, "path");
    p.setAttribute("data-shaft", "");
    p.setAttribute("d", "M4.5 12H16.5M11 6.5L16.5 12L11 17.5");
    svg.appendChild(p);
    return svg;
  }
  /* Replace any element carrying [data-arrow] with the SVG component. */
  function mountArrows(rootEl) {
    (rootEl || document).querySelectorAll("[data-arrow]").forEach(function (slot) {
      slot.replaceChildren(arrow());
    });
  }

  /* designerAudit — getBBox/rect overlap detector.
     Returns [] when clean; otherwise a list of {a, b, kind} overlapping pairs.
     Audited: text labels, evidence chips, solid graphics, leader lines. */
  function rectOf(el) {
    if (typeof el.getBBox === "function" && el.ownerSVGElement) {
      var b = el.getBBox(), ctm = el.getScreenCTM();
      if (ctm) return { x: b.x * ctm.a + ctm.e, y: b.y * ctm.d + ctm.f,
                        w: b.width * ctm.a, h: b.height * ctm.d };
    }
    var r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  }
  function overlaps(p, q, pad) {
    pad = pad || 0;
    return !(p.x + p.w <= q.x + pad || q.x + q.w <= p.x + pad ||
             p.y + p.h <= q.y + pad || q.y + q.h <= p.y + pad);
  }
  function label(el) {
    return (el.getAttribute("data-audit") || el.tagName.toLowerCase()) +
      (el.id ? "#" + el.id : "") +
      (el.textContent && el.textContent.trim() ? '("' + el.textContent.trim().slice(0, 18) + '")' : "");
  }
  function designerAudit(rootEl) {
    var scope = rootEl || document.body;
    // elements that must never collide: text, chips, and anything tagged [data-audit]
    var nodes = Array.prototype.slice.call(
      scope.querySelectorAll("text, .chip, [data-audit], h1, h2, h3, .btn"));
    var hits = [], i, j, ri, rj;
    for (i = 0; i < nodes.length; i++) {
      ri = rectOf(nodes[i]);
      if (ri.w === 0 || ri.h === 0) continue;
      for (j = i + 1; j < nodes.length; j++) {
        if (nodes[i].contains(nodes[j]) || nodes[j].contains(nodes[i])) continue;
        rj = rectOf(nodes[j]);
        if (rj.w === 0 || rj.h === 0) continue;
        if (overlaps(ri, rj, 1)) hits.push({ a: label(nodes[i]), b: label(nodes[j]), kind: "element-vs-element" });
      }
    }
    return hits;
  }

  function initTheme(btn) {
    var rootHtml = document.documentElement;
    if (!rootHtml.getAttribute("data-theme")) rootHtml.setAttribute("data-theme", "light");
    if (btn) btn.addEventListener("click", function () {
      rootHtml.setAttribute("data-theme",
        rootHtml.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }
  function initI18n(btn) {
    var rootHtml = document.documentElement;
    if (!rootHtml.getAttribute("data-lang")) rootHtml.setAttribute("data-lang", "en");
    if (btn) btn.addEventListener("click", function () {
      rootHtml.setAttribute("data-lang",
        rootHtml.getAttribute("data-lang") === "en" ? "vn" : "en");
    });
  }
  /* initDraw — measure each [data-draw] path so the stroke-dashoffset draw-in animates the
     full length (design-system.css drives the transition; initReveal adds .is-in to trigger it). */
  function initDraw(rootEl) {
    (rootEl || document).querySelectorAll("[data-draw]").forEach(function (el) {
      try { el.style.setProperty("--len", Math.ceil(el.getTotalLength())); }
      catch (e) { el.style.setProperty("--len", "1200"); }
    });
  }
  function initReveal(rootEl) {
    var els = (rootEl || document).querySelectorAll(".reveal, [data-draw]");
    if (!("IntersectionObserver" in window)) {  // graceful: show everything
      els.forEach(function (e) { e.classList.add("is-in"); }); return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { threshold: 0.15 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* initRegistry — client-side facet + search + sort over BAKED cards.
     Filter never hides a card for being null/disputed — only facet/search mismatch hides it
     (honest-null & disputed stay visible in the filtered set). State round-trips through the URL
     querystring so a filtered view is citable. Perf budget: a filter pass must stay < 100ms. */
  function initRegistry(opts) {
    opts = opts || {};
    var grid = document.querySelector(opts.grid || ".grid");
    if (!grid) return;
    var item = opts.item || ".card";
    var cards = Array.prototype.slice.call(grid.querySelectorAll(item));
    var search = document.getElementById("reg-search");
    var countEl = document.getElementById("reg-count-n");
    var sortBtn = document.getElementById("reg-sort");
    var toggles = Array.prototype.slice.call(document.querySelectorAll(".tg[data-facet]"));
    var GROUPS = ["segment", "klass", "country", "flag"];   // value-groups + boolean flags
    var SORTS = ["name", "segment", "country"];
    var SORT_LABELS = {
      name: { en: "Sort: A–Z", vn: "Sắp: A–Z" },
      segment: { en: "Sort: segment", vn: "Sắp: phân khúc" },
      country: { en: "Sort: country", vn: "Sắp: quốc gia" }
    };
    var state = { segment: new Set(), klass: new Set(), country: new Set(), flag: new Set(), q: "", sort: "name" };

    function loadURL() {
      var u = new URLSearchParams(location.search);
      GROUPS.forEach(function (g) {
        (u.get(g) || "").split(",").filter(Boolean).forEach(function (v) { state[g].add(v); });
      });
      state.q = u.get("q") || "";
      if (SORTS.indexOf(u.get("sort")) >= 0) state.sort = u.get("sort");
    }
    function writeURL() {
      var u = new URLSearchParams();
      GROUPS.forEach(function (g) {
        if (state[g].size) u.set(g, Array.prototype.join.call(Array.prototype.slice.call(state[g]), ","));
      });
      if (state.q) u.set("q", state.q);
      if (state.sort !== "name") u.set("sort", state.sort);
      var qs = u.toString();
      history.replaceState(null, "", qs ? "?" + qs : location.pathname);
    }
    function matches(c) {
      var d = c.dataset;
      if (state.segment.size && !state.segment.has(d.segment)) return false;
      if (state.klass.size && !state.klass.has(d.klass)) return false;
      if (state.country.size && !state.country.has(d.country)) return false;
      if (state.flag.has("blue") && d.blue !== "1") return false;
      if (state.flag.has("ndaa") && d.ndaa !== "1") return false;
      if (state.q && (d.name || "").indexOf(state.q.toLowerCase()) < 0) return false;
      return true;
    }
    function apply() {
      var t0 = performance.now(), shown = 0, i, c;
      for (i = 0; i < cards.length; i++) {
        c = cards[i];
        if (matches(c)) { c.classList.remove("hidden"); c.classList.add("is-in"); shown++; }
        else { c.classList.add("hidden"); }
      }
      var vis = cards.filter(function (x) { return !x.classList.contains("hidden"); });
      var k = state.sort;
      vis.sort(function (a, b) {
        var av = k === "name" ? a.dataset.name : (a.dataset[k] || "￿");
        var bv = k === "name" ? b.dataset.name : (b.dataset[k] || "￿");
        return av < bv ? -1 : av > bv ? 1 : 0;
      });
      vis.forEach(function (x) { grid.appendChild(x); });   // reorder in place
      if (countEl) countEl.textContent = shown;
      writeURL();
      window.__regMs = performance.now() - t0;   // exposed for the perf gate
    }
    function renderSort() {
      if (!sortBtn) return;
      var l = SORT_LABELS[state.sort];
      sortBtn.innerHTML = '<span data-lang-en>' + l.en + '</span><span data-lang-vn>' + l.vn + '</span>';
    }

    loadURL();
    toggles.forEach(function (btn) {
      var g = btn.dataset.facet, v = btn.dataset.value;
      if (state[g] && state[g].has(v)) btn.setAttribute("aria-pressed", "true");
      btn.addEventListener("click", function () {
        var on = btn.getAttribute("aria-pressed") === "true";
        btn.setAttribute("aria-pressed", on ? "false" : "true");
        if (on) state[g].delete(v); else state[g].add(v);
        apply();
      });
    });
    if (search) {
      search.value = state.q;
      search.addEventListener("input", function () { state.q = search.value.trim(); apply(); });
    }
    if (sortBtn) sortBtn.addEventListener("click", function () {
      state.sort = SORTS[(SORTS.indexOf(state.sort) + 1) % SORTS.length];
      renderSort(); apply();
    });
    renderSort();
    apply();
  }

  root.USRBase = { arrow: arrow, mountArrows: mountArrows, designerAudit: designerAudit,
                   initTheme: initTheme, initI18n: initI18n, initReveal: initReveal,
                   initDraw: initDraw, initRegistry: initRegistry };
})(window);
