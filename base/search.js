/* TIP-P2.1 — Search client. Reads out/search-index.json (built live from site-data), filters by
   token over .terms, groups hits by type with a type-badge, links to the real page. Query mirrors
   to ?q=… (shareable + reloadable). No framework, no search lib. */
(function () {
  "use strict";
  var IDX = null, TYPES = {}, ORDER = ["uav", "company", "country", "segment"], CAP = 50;
  var q = document.getElementById("q"), out = document.getElementById("out");

  function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : String(s); return d.innerHTML; }
  function bi(en, vn) { return '<span data-lang-en>' + esc(en) + '</span><span data-lang-vn>' + esc(vn) + '</span>'; }

  function syncURL(query) {
    history.replaceState(null, "", query ? "?q=" + encodeURIComponent(query) : location.pathname);
  }

  function render(query) {
    query = (query || "").trim().toLowerCase();
    if (!query) { out.innerHTML = '<p class="empty">' + bi("Type to search across systems, manufacturers, countries and segments.",
      "Gõ để tìm trong hệ thống, nhà sản xuất, quốc gia và phân khúc.") + '</p>'; return; }
    var toks = query.split(/\s+/);
    var hits = IDX.filter(function (e) { return toks.every(function (t) { return e.terms.indexOf(t) >= 0; }); });
    if (!hits.length) { out.innerHTML = '<p class="empty">' + bi("No matches.", "Không có kết quả.") + '</p>'; return; }
    var by = {}; hits.forEach(function (h) { (by[h.type] = by[h.type] || []).push(h); });
    var html = "";
    ORDER.forEach(function (type) {
      var g = by[type]; if (!g || !g.length) return;
      var tl = TYPES[type] || { en: type, vn: type };
      html += '<div class="grp"><div class="grp-h">' + bi(tl.en, tl.vn) +
        ' <span class="n">' + g.length + '</span></div>';
      g.slice(0, CAP).forEach(function (h) {
        html += '<div class="hit"><span class="badge">' + bi(tl.en, tl.vn) + '</span>' +
          '<a href="' + esc(h.url) + '">' + bi(h.label_en, h.label_vn) + '</a>' +
          '<span class="sub">' + bi(h.sub_en, h.sub_vn) + '</span></div>';
      });
      if (g.length > CAP) html += '<div class="hit"><span class="sub">+' + (g.length - CAP) + ' more</span></div>';
      html += '</div>';
    });
    out.innerHTML = html;
  }

  q.addEventListener("input", function () { render(q.value); syncURL(q.value); });

  fetch("out/search-index.json").then(function (r) { return r.json(); }).then(function (data) {
    IDX = data.entries; TYPES = data.types;
    var pre = new URLSearchParams(location.search).get("q");
    if (pre) { q.value = pre; }
    render(q.value);
  }).catch(function () {
    out.innerHTML = '<p class="empty">' + bi("Could not load the search index.", "Không tải được chỉ mục tìm kiếm.") + '</p>';
  });
})();
