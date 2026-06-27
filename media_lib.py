#!/usr/bin/env python3
"""media_lib.py — TIP-MEDIA-UPGRADE Task 1 (loader).

Nạp content/media.json (lớp E thuần), trả asset đã-lọc-quyền cho builder render. KHÔNG render,
KHÔNG gate cứng (gate nằm ở verify_media.py). Loader chỉ nạp + lọc render-eligibility.

Mô-hình hai-tầng:
  - verify_media.py (gate): manifest phải sạch tuyệt-đối, lỗi authoring → exit 2.
  - media_lib (loader, render-time): trả asset render-eligible; surface không có asset → builder dựng fallback.

rights enum (Contract §2): rtr_owned · rtr_distributed · data_figure · external_article_share
                            (bật) · third_party_in_article (chặn) · wire_licensed (off tới khi có license).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEDIA_JSON = ROOT / "content" / "media.json"

ENUM = {"rtr_owned", "rtr_distributed", "data_figure", "open_licensed",
        "external_article_share", "third_party_in_article", "wire_licensed"}
# nhóm BẬT phase này. open_licensed = CC/public-domain/press-kit/gov (khai license+credit, gate canh).
# third_party_in_article = chặn; wire_licensed = chỉ khi license.active.
RENDER_RIGHTS = {"rtr_owned", "rtr_distributed", "data_figure", "open_licensed", "external_article_share"}


def load(path=None):
    p = Path(path) if path else MEDIA_JSON
    if not p.exists():
        return {"schema": "media/1", "assets": {}, "bindings": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def _wire_live(a):
    lic = a.get("license") or {}
    return bool(lic.get("token")) and lic.get("active") is True


def render_eligible(a):
    """Asset có được render ở phase này không. third_party = không; wire chỉ khi license.active+token."""
    r = a.get("rights")
    if r in RENDER_RIGHTS:
        return True
    if r == "wire_licensed":
        return _wire_live(a)
    return False                                    # third_party_in_article + enum-lạ → chặn


def _esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def img_html(asset, cls="", rel_prefix=""):
    """Render một asset rtr_owned/eligible thành <img> (ảnh) hoặc <video> (clip). rel_prefix cho trang
    nằm sâu (vd entity/ dùng '../'). Caption thành alt; ảnh lazy. KHÔNG render nếu asset rỗng."""
    if not asset:
        return ""
    src = _esc(rel_prefix + asset["src"].lstrip("/"))
    cap = _esc(asset.get("caption") or "")
    if asset.get("type") == "video":
        return (f'<video class="{cls}" src="{src}" muted loop playsinline autoplay '
                f'preload="metadata" aria-label="{cap}"></video>')
    return f'<img class="{cls}" src="{src}" alt="{cap}" loading="lazy" decoding="async">'


class Media:
    def __init__(self, doc=None):
        self.doc = doc if doc is not None else load()
        self.assets = self.doc.get("assets", {})
        self.bindings = self.doc.get("bindings", {})

    def get(self, media_id):
        return self.assets.get(media_id)

    def for_binding(self, key, eligible_only=True):
        """Trả list asset gắn vào một surface (vd 'entity:<slug>', 'hero:home'), giữ thứ-tự bindings."""
        out = []
        for mid in self.bindings.get(key, []):
            a = self.assets.get(mid)
            if a and (not eligible_only or render_eligible(a)):
                out.append({"id": mid, **a})
        return out

    def first(self, key):
        lst = self.for_binding(key)
        return lst[0] if lst else None


if __name__ == "__main__":
    m = Media()
    print(f"media/{m.doc.get('schema','?')} · assets={len(m.assets)} · bindings={len(m.bindings)}")
    for k in sorted(m.bindings):
        elig = m.for_binding(k)
        print(f"  {k:52s} → {len(elig)} render-eligible")
