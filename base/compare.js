/* TIP-P1.3 — Compare client. Reads out/compare-data.json (built live from site-data), lets the
   user pick 2–4 UAVs, renders a side-by-side spec table reusing the micro-track (log), honest-null
   and tier primitives. Selection is mirrored in ?uav=… so a comparison is shareable + reloadable.
   No framework. */
(function () {
  "use strict";
  var D = null, sel = [], MAX = 4;
  var q = document.getElementById("q"), results = document.getElementById("results"),
      chips = document.getElementById("chips"), table = document.getElementById("table");

  function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }
  function tslug(v) { return (v || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, ""); }
  function bi(en, vn) { return '<span data-lang-en>' + esc(en) + '</span><span data-lang-vn>' + esc(vn) + '</span>'; }

  // log-scale position (mirrors build_detail.log_pos — value-small still gets a visible tick)
  function logPos(v, lo, hi) {
    lo = Math.max(lo, 1e-9);
    if (hi <= lo || v <= 0) return 50;
    var p = (Math.log10(v) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)) * 100;
    return Math.max(2, Math.min(98, p));
  }
  function bySlug(s) { for (var i = 0; i < D.uavs.length; i++) if (D.uavs[i].slug === s) return D.uavs[i]; return null; }

  function syncURL() {
    var u = sel.length ? "?uav=" + sel.join(",") : location.pathname;
    history.replaceState(null, "", u);
  }

  function glyph(kind) {
    var t = document.querySelector('template[data-glyph-kind="' + kind + '"]');
    return t ? t.innerHTML : "";
  }

  // suggestions when the box is empty/focused — one system from each largest manufacturer, so the
  // screen is never blank and the user has recognizable starting points to click.
  function suggestions() {
    var count = {};
    D.uavs.forEach(function (u) { count[u.maker] = (count[u.maker] || 0) + 1; });
    var makers = Object.keys(count).sort(function (a, b) { return count[b] - count[a]; });
    var out = [];
    makers.forEach(function (m) {
      if (out.length >= 10) return;
      for (var i = 0; i < D.uavs.length; i++) {
        if (D.uavs[i].maker === m && sel.indexOf(D.uavs[i].slug) < 0) { out.push(D.uavs[i]); break; }
      }
    });
    return out;
  }

  // unit for a spec key (from compare-data specs), and a compact "13 kg · 30 km" readout (honest-null safe)
  function specUnit(key) { for (var i = 0; i < D.specs.length; i++) if (D.specs[i].key === key) return D.specs[i].unit; return ""; }
  function micro(u) {
    var keys = ["mtow_kg", "max_range_km"], parts = [];
    keys.forEach(function (k) { var c = u.specs[k]; if (c && c.v != null) parts.push(c.v + " " + specUnit(k)); });
    return parts.length ? parts.join(" · ") : "—";
  }

  function renderResults() {
    var query = (q.value || "").trim().toLowerCase();
    var hits, head;
    if (!query) {
      hits = suggestions();
      head = '<div class="rhint">' + bi("Suggestions — or type a model / manufacturer",
        "Gợi ý — hoặc gõ tên mẫu / hãng") + '</div>';
    } else {
      hits = D.uavs.filter(function (u) { return (u.name + " " + u.maker).toLowerCase().indexOf(query) >= 0; }).slice(0, 40);
      head = "";
    }
    results.innerHTML = head + hits.map(function (u) {
      var dis = sel.indexOf(u.slug) >= 0 || sel.length >= MAX;
      return '<button class="sugg" data-slug="' + esc(u.slug) + '"' + (dis ? " disabled" : "") + '>' +
        '<span class="gl">' + glyph(u.glyph) + '</span>' +
        '<span class="snm">' + esc(u.name) + '</span>' +
        '<span class="smk">' + esc(u.maker) + '</span>' +
        '<span class="sspec">' + esc(micro(u)) + '</span>' +
        '<span class="sadd">' + (dis ? bi("added", "đã thêm") : bi("+ add", "+ thêm")) + '</span></button>';
    }).join("");
    results.hidden = !hits.length;
  }
  q.addEventListener("focus", renderResults);

  // selected systems as a 4-bay rack: filled bays keep class .chip (audit + remove handler), empties are dashed
  function renderChips() {
    var html = "";
    for (var i = 0; i < MAX; i++) {
      var s = sel[i], u = s ? bySlug(s) : null;
      var bay = '<span class="bnum">' + bi("Bay", "Khoang") + ' ' + (i + 1) + '</span>';
      if (u) {
        html += '<div class="chip bay">' + bay +
          '<span class="gl">' + glyph(u.glyph) + '</span>' +
          '<span class="bnm">' + esc(u.name) + '</span>' +
          '<span class="bmk">' + esc(u.maker) + '</span>' +
          '<b class="brm" data-rm="' + esc(s) + '" title="remove">×</b></div>';
      } else {
        html += '<div class="bay empty">' + bay + '<span class="dots">+ + +</span></div>';
      }
    }
    chips.innerHTML = html;
  }

  function colHeader(u) {
    var maker = u.company_slug
      ? '<span class="mk"><a href="company/' + esc(u.company_slug) + '.html">' + esc(u.maker) + '</a></span>'
      : '<span class="mk">' + esc(u.maker) + '</span>';
    var tags = [];
    if (u.country) tags.push('<a href="country/' + esc(tslug(u.country)) + '.html">' + esc(u.country) + '</a>');
    if (u.segment) {
      var sl = D.segment_labels[u.segment] || { en: u.segment, vn: u.segment };
      tags.push('<a href="segment/' + esc(tslug(u.segment)) + '.html">' + bi(sl.en, sl.vn) + '</a>');
    }
    if (u.blue) tags.push('<span class="b">Blue UAS</span>');
    if (u.ndaa) tags.push('<span class="b">NDAA</span>');
    return '<div class="col-h"><span class="gl">' + glyph(u.glyph) + '</span>' +
      '<span class="nm"><a href="uav/' + esc(u.slug) + '.html">' + esc(u.name) + '</a></span>' +
      maker + '<span class="tags">' + tags.join(" · ") + '</span></div>';
  }

  function cell(u, spec) {
    var c = u.specs[spec.key] || {}, r = D.spec_range[spec.key];
    if (c.claims && c.claims.length) {  // disputed — keep every claim
      var lo = Math.min.apply(null, c.claims), hi = Math.max.apply(null, c.claims), trk;
      if (r) { var a = logPos(lo, r.min, r.max), b = logPos(hi, r.min, r.max);
        trk = '<span class="ri-spark"><i style="margin-left:' + a + '%;width:' + Math.max(2, b - a) + '%"></i></span>'; }
      else trk = '<span class="ri-spark null"></span>';
      return '<div class="cmpcell">' + trk + '<span class="disp">' +
        c.claims.map(function (x) { return esc(x); }).join(" / ") + " " + esc(spec.unit) +
        ' ' + bi("disputed", "tranh chấp") + '</span></div>';
    }
    if (c.v == null) {  // honest-null — dashed rail, no tick, "—"
      return '<div class="cmpcell"><span class="ri-spark null"></span><span class="val null">—</span></div>';
    }
    var pos = r ? logPos(c.v, r.min, r.max) : 50;
    var tier = c.tier ? '<span class="tier">' + esc(c.tier) + '</span>' : "";
    return '<div class="cmpcell"><span class="ri-spark"><i style="width:' + pos + '%"></i></span>' +
      '<span class="val">' + esc(c.v) + " " + esc(spec.unit) + '</span>' + tier + '</div>';
  }

  function renderTable() {
    if (sel.length < 2) {
      table.innerHTML = '<p class="empty">' + bi("Pick at least 2 systems to compare.",
        "Chọn ít nhất 2 hệ thống để so sánh.") + '</p>';
      return;
    }
    var cols = sel.map(bySlug).filter(Boolean);
    var head = '<tr><th></th>' + cols.map(function (u) { return '<th>' + colHeader(u) + '</th>'; }).join("") + '</tr>';
    var rows = D.specs.map(function (sp) {
      return '<tr><td class="rk">' + bi(sp.en, sp.vn) + '</td>' +
        cols.map(function (u) { return '<td>' + cell(u, sp) + '</td>'; }).join("") + '</tr>';
    }).join("");
    table.innerHTML = '<table class="cmp"><thead>' + head + '</thead><tbody>' + rows + '</tbody></table>';
  }

  function add(s) { if (sel.indexOf(s) < 0 && sel.length < MAX && bySlug(s)) { sel.push(s); refresh(); } }
  function rm(s) { var i = sel.indexOf(s); if (i >= 0) { sel.splice(i, 1); refresh(); } }
  function refresh() { renderChips(); renderResults(); renderTable(); syncURL(); }

  results.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-slug]"); if (b && !b.disabled) { add(b.getAttribute("data-slug")); q.value = ""; }
  });
  chips.addEventListener("click", function (e) {
    var b = e.target.closest("b[data-rm]"); if (b) rm(b.getAttribute("data-rm"));
  });
  q.addEventListener("input", renderResults);

  fetch("out/compare-data.json").then(function (r) { return r.json(); }).then(function (data) {
    D = data;
    var pre = new URLSearchParams(location.search).get("uav");
    if (pre) pre.split(",").forEach(function (s) { if (s) add(s.trim()); });
    refresh();
  }).catch(function () {
    table.innerHTML = '<p class="empty">' + bi("Could not load comparison data.",
      "Không tải được dữ liệu so sánh.") + '</p>';
  });
})();
