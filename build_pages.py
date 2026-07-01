#!/usr/bin/env python3
"""Trust and legal pages (Giai doan 0). Five static, bilingual editorial pages at the site root:
about / methodology / contact / terms / privacy. Content is the approved draft
(USR-noi-dung-trang-tin-cay.md), VN + an EN mirror so check_i18n stays balanced. Entity, address,
email and effective-date fields are being finalised and show a placeholder ("(cho bo sung)" / "(to
be added)"); swap them for real values in the CONTENT block below. Reuses the global header, footer,
nav and seo. No fabricated facts: nothing here asserts a figure or a source."""
import pathlib
from footer import footer, bilingual, esc
from header import header
from seo import meta

ROOT = pathlib.Path(__file__).resolve().parent

# EN placeholder mirrors the VN "(cho bo sung)"; both get swapped when the owner confirms real values.
PH_EN, PH_VN = "(to be added)", "(chờ bổ sung)"

LEGAL_CSS = """
  .legal{max-width:var(--w-read);margin:0 auto;padding:2.4rem 1.4rem 4rem}
  .lg-head{border-bottom:1px solid var(--hair);padding-bottom:1.2rem;margin-bottom:1.6rem}
  .lg-head .eyebrow{font-family:var(--font-mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--brass)}
  .lg-head h1{margin:.4rem 0 0;font-family:var(--font-head);font-size:2rem;line-height:1.12}
  .lg-eff{font-family:var(--font-mono);font-size:.72rem;color:var(--muted);margin:.6rem 0 0}
  .legal p{font-size:1rem;line-height:1.72;color:var(--ink);margin:0 0 1.15rem;max-width:64ch}
  .legal .lg-lead{color:var(--ink);font-weight:600}
  .legal p a{color:var(--brass);text-decoration:none;border-bottom:1px solid var(--hair-strong)}
  .legal p a:hover{border-bottom-color:var(--brass)}
  .legal h2{font-family:var(--font-head);font-size:1.28rem;margin:2.2rem 0 1rem;padding-top:1.4rem;border-top:1px solid var(--hair)}
  .lg-foot{font-size:.74rem;color:var(--muted);margin-top:2rem;border-top:1px solid var(--hair);padding-top:1.1rem}
"""


def _p(en, vn):
    return f"<p>{bilingual(en, vn)}</p>"


def _lead(le, lv, be, bv):
    return f'<p><b class="lg-lead">{bilingual(le, lv)}</b> {bilingual(be, bv)}</p>'


def _h(en, vn):
    return f"<h2>{bilingual(en, vn)}</h2>"


def _seg(*parts):
    """A run of bilingual text with inline cross-links. Each part is (en, vn) text, or
    (en, vn, href) a link. Every piece is a paired en/vn span so check_i18n stays balanced."""
    out = []
    for p in parts:
        if len(p) == 3:
            out.append(f'<a href="{p[2]}">{bilingual(p[0], p[1])}</a>')
        else:
            out.append(bilingual(p[0], p[1]))
    return "".join(out)


def _pseg(*parts):
    return f"<p>{_seg(*parts)}</p>"


def _leadseg(le, lv, *parts):
    return f'<p><b class="lg-lead">{bilingual(le, lv)}</b> {_seg(*parts)}</p>'


# ---- content (each block renders paired en/vn spans -> check_i18n stays balanced) ----
def about():
    return [
        _p("Uncrewed Systems Review (USR) is an independent data publication on uncrewed aerial systems and the low-altitude economy. We bring the technical specifications, manufacturer profiles, news and background knowledge of this field into a single place to look things up, where every figure traces back to its source.",
           "Uncrewed Systems Review (USR) là một ấn phẩm dữ liệu độc lập về hệ thống bay không người lái và nền kinh tế tầm thấp. Chúng tôi tập hợp thông số kỹ thuật, hồ sơ nhà sản xuất, tin tức và kiến thức nền của lĩnh vực này vào một nơi tra cứu duy nhất, nơi mỗi con số đều truy được về nguồn của nó."),
        _p("USR aims to make a fast-moving field legible: operators, regulators, investors and interested readers can look up a system, compare a few models, or follow a policy without having to piece it together from dozens of scattered sources.",
           "Mục tiêu của USR là làm cho một lĩnh vực đang thay đổi nhanh trở nên dễ đọc: người vận hành, cơ quan quản lý, nhà đầu tư và người quan tâm có thể tra một hệ thống, so sánh vài mẫu, hoặc theo dõi một chính sách mà không phải tự đi ghép từ hàng chục nguồn rời rạc."),
        _p("The registry currently covers hundreds of systems from many countries, linked company profiles, a sourced news stream and a base of reference terms. All of it is presented bilingually in Vietnamese and English, with an emphasis on the Vietnamese market and policy within a regional and global context.",
           "Bản đăng ký hiện bao gồm hàng trăm hệ thống từ nhiều quốc gia, hồ sơ doanh nghiệp liên kết, một dòng tin tức có dẫn nguồn và một kho thuật ngữ nền. Tất cả được trình bày song ngữ Việt và Anh, với trọng tâm đặt vào thị trường và chính sách Việt Nam trong bối cảnh khu vực và toàn cầu."),
        _pseg(("What sets USR apart from an ordinary aggregator is data discipline. Every attribute is stored with its source and a confidence tier; anything unverified is left visibly blank rather than guessed; conflicting figures are kept on both sides rather than quietly resolved to one. How we work is described in full on the ",
               "Điều làm USR khác với một bảng tổng hợp thông thường nằm ở kỷ luật dữ liệu. Mỗi thuộc tính được lưu kèm nguồn và mức tin cậy; phần chưa kiểm chứng được để trống một cách công khai thay vì suy đoán; số liệu mâu thuẫn được giữ nguyên cả hai phía thay vì âm thầm chọn một. Cách chúng tôi làm việc được mô tả đầy đủ trong "),
              ("Methodology and sources page", "trang Phương pháp và nguồn", "methodology.html"),
              (".", ".")),
        _p("USR keeps editorial independence. The registry applies the same sourcing standard to every manufacturer, with no favour to any party, including those connected to the publisher. USR is not a product marketing channel and does not accept sponsored content disguised as data.",
           "USR giữ độc lập biên tập. Bản đăng ký áp cùng một chuẩn dẫn nguồn cho mọi nhà sản xuất, không dành ưu ái cho bất kỳ bên nào, kể cả các bên có liên quan tới đơn vị xuất bản. USR không phải kênh tiếp thị sản phẩm và không nhận nội dung tài trợ trá hình thành dữ liệu."),
        _pseg((f"USR is published and operated by {PH_EN}. Questions, corrections or source suggestions are welcome through the ",
               f"USR được xuất bản và vận hành bởi {PH_VN}. Mọi câu hỏi, đính chính hoặc đề xuất nguồn xin gửi qua "),
              ("Contact page", "trang Liên hệ", "contact.html"),
              (".", ".")),
    ]


def methodology():
    return [
        _p("The founding principle of USR is that data provenance is the product. A figure without a source is worth no more than a rumour, so we do not present any figure that way.",
           "Nguyên tắc nền của USR là: lý lịch dữ liệu chính là sản phẩm. Một con số không kèm nguồn không có giá trị hơn một tin đồn, nên chúng tôi không trưng con số nào theo cách đó."),
        _lead("Every data cell carries its own provenance.", "Mỗi ô dữ liệu mang lý lịch riêng.",
              "Every technical attribute of a system is stored together with its value, status, cited source, confidence tier and the date it was last checked. A reader can trace a specification back to the original document.",
              "Mọi thuộc tính kỹ thuật của một hệ thống được lưu cùng giá trị, trạng thái, nguồn dẫn, mức tin cậy và lần kiểm gần nhất. Người đọc có thể truy ngược một thông số về tài liệu gốc."),
        _lead("Three source tiers.", "Ba mức tin cậy của nguồn.",
              "We classify sources in three tiers. Tier A is original or official: manufacturer documents, certification records, regulatory texts. Tier B is a reputable secondary source: trade press, edited research publications. Tier C is a weaker source that needs further corroboration. The tier is shown next to the data so readers can weigh it themselves.",
              "Chúng tôi phân loại nguồn theo ba bậc. Bậc A là nguồn gốc hoặc chính thức: tài liệu của nhà sản xuất, hồ sơ chứng nhận, văn bản cơ quan quản lý. Bậc B là nguồn thứ cấp uy tín: báo chí chuyên ngành, ấn phẩm nghiên cứu đã biên tập. Bậc C là nguồn yếu hơn, cần đối chiếu thêm. Mức tin cậy được hiển thị cạnh dữ liệu để người đọc tự cân nhắc."),
        _lead("Blank is blank, not filled.", "Trống là trống, không lấp.",
              "When a specification has no trustworthy source, we leave it blank and mark it as not recorded, rather than estimating or filling it in. The registry's data coverage is therefore shown honestly. A blank cell is a signal of honesty, not a gap to hide.",
              "Khi một thông số chưa có nguồn đáng tin, chúng tôi để trống và ghi rõ là chưa ghi nhận, thay vì ước lượng hay điền cho đầy. Độ phủ dữ liệu của bản đăng ký vì thế được phơi bày trung thực. Một ô trống là một tín hiệu thành thật, không phải một thiếu sót cần che."),
        _lead("Conflicts are kept whole.", "Mâu thuẫn được giữ nguyên.",
              "When sources give different numbers for the same specification, we keep the recorded versions rather than choosing one and deleting the rest. Readers see the real uncertainty in the data.",
              "Khi các nguồn đưa số khác nhau cho cùng một thông số, chúng tôi giữ lại các cách ghi nhận thay vì tự chọn một con số và xóa phần còn lại. Người đọc thấy được sự bất định thật của dữ liệu."),
        _lead("Counting units and derivation.", "Đơn vị đếm và suy dẫn.",
              "We distinguish a base product line from its variants, and state which unit is being counted. Some entities, such as company profiles, are derived from existing data and marked as derived rather than a new source.",
              "Chúng tôi phân biệt dòng thiết bị gốc với các biến thể của nó, và nêu rõ đơn vị đang đếm. Một số thực thể, ví dụ hồ sơ doanh nghiệp, được suy ra từ dữ liệu đã có và được đánh dấu là suy dẫn, không phải nguồn mới."),
        _lead("Live figures.", "Con số sống.",
              "Every total and statistic on the site is recomputed directly from the source data on each update, so charts and tables always match the registry rather than being hand-copied numbers that can fall out of date.",
              "Mọi tổng hợp và thống kê trên trang được tính lại trực tiếp từ dữ liệu gốc mỗi lần cập nhật, nên các biểu đồ và bảng luôn khớp với bản đăng ký, không phải số chép tay có thể lạc hậu."),
        _lead("What we do not do.", "Chúng tôi không làm gì.",
              "USR does not create specifications by guesswork, does not use tool-generated numbers that lack a source, and does not present estimates as facts.",
              "USR không tạo ra thông số bằng suy đoán, không dùng số do công cụ tự sinh mà thiếu nguồn, và không trình bày ước lượng như dữ kiện."),
        _lead("Scope and limits.", "Phạm vi và giới hạn.",
              "The registry is a curated set, not a full census of the industry. It does not include every system in existence, and coverage varies by specification. We state this limit openly rather than implying a completeness that does not exist.",
              "Bản đăng ký là một tập tuyển chọn, không phải một cuộc tổng điều tra toàn ngành. Nó không bao gồm mọi hệ thống đang tồn tại, và độ phủ theo từng thông số là khác nhau. Chúng tôi công khai giới hạn này thay vì ngụ ý một sự hoàn chỉnh không có thật."),
        _leadseg("Corrections and source contributions.", "Đính chính và đóng góp nguồn.",
                 ("Good data improves under scrutiny. If you find an error or have a better source, please send it to us through the ",
                  "Dữ liệu tốt lên nhờ được soi. Nếu bạn thấy một sai sót hoặc có một nguồn tốt hơn, xin gửi cho chúng tôi qua "),
                 ("Contact page", "trang Liên hệ", "contact.html"),
                 ("; we review and update it with the source recorded.",
                  "; chúng tôi rà soát và cập nhật kèm ghi nhận nguồn.")),
    ]


def contact():
    return [
        _p("USR welcomes corrections, source material and collaboration proposals. Please choose the right channel so we can respond as quickly as possible.",
           "USR hoan nghênh đính chính, nguồn tư liệu và đề nghị hợp tác. Xin chọn đúng kênh để chúng tôi phản hồi nhanh nhất."),
        _lead("Editorial and corrections.", "Biên tập và đính chính.",
              f"Report a data error, suggest a source, or give feedback on content: {PH_EN}. When reporting an error, please name the specific page and, if possible, a source we can check against.",
              f"Báo lỗi dữ liệu, đề xuất nguồn, phản hồi nội dung: {PH_VN}. Khi báo lỗi, xin nêu trang cụ thể và, nếu có thể, nguồn dẫn để chúng tôi đối chiếu."),
        _lead("Data and collaboration.", "Dữ liệu và hợp tác.",
              f"Propose adding a system or company, data collaboration, or questions about methodology: {PH_EN}.",
              f"Đề nghị bổ sung hệ thống hoặc doanh nghiệp, hợp tác dữ liệu, câu hỏi về phương pháp: {PH_VN}."),
        _lead("Legal and copyright.", "Pháp lý và bản quyền.",
              f"Matters of terms, privacy or image attribution: {PH_EN}.",
              f"Vấn đề về điều khoản, quyền riêng tư hoặc ghi nguồn hình ảnh: {PH_VN}."),
        _p(f"Publisher: {PH_EN}, {PH_EN}.", f"Đơn vị xuất bản: {PH_VN}, {PH_VN}."),
        _p("We aim to reply within a few business days. Every valid correction is updated with the source recorded.",
           "Chúng tôi cố gắng phản hồi trong vài ngày làm việc. Mọi đính chính hợp lệ được cập nhật kèm ghi nhận."),
    ]


def terms():
    return [
        _lead("Informational purpose.", "Mục đích thông tin.",
              "The content on USR is provided for reference and look-up. It is a curated registry based on public sources, not an official document of a regulator or manufacturer, and it does not substitute for professional technical, legal or investment advice.",
              "Nội dung trên USR được cung cấp cho mục đích tham khảo và tra cứu. Đây là một bản đăng ký tuyển chọn dựa trên nguồn công khai, không phải tài liệu chính thức của cơ quan quản lý hay của nhà sản xuất, và không thay thế cho tư vấn kỹ thuật, pháp lý hay đầu tư chuyên môn."),
        _lead("No warranty.", "Không bảo đảm.",
              "We make an effort to cite and verify, but we do not guarantee that the data is complete, absolutely current or free of error. Users are responsible for their own decisions based on the content here, and should check against original sources for important purposes.",
              "Chúng tôi nỗ lực dẫn nguồn và kiểm chứng, nhưng không bảo đảm dữ liệu đầy đủ, cập nhật tuyệt đối hay không có sai sót. Người dùng tự chịu trách nhiệm khi ra quyết định dựa trên nội dung tại đây, và nên đối chiếu với nguồn gốc cho các mục đích quan trọng."),
        _lead("Intellectual property.", "Sở hữu trí tuệ.",
              "The presentation, data structure and editorial content of USR belong to the publisher. You may quote with attribution and a link back to the source page. Large-scale copying or systematic republication requires prior written permission.",
              "Cách trình bày, cấu trúc dữ liệu và nội dung biên tập của USR thuộc về đơn vị xuất bản. Bạn có thể trích dẫn kèm ghi nguồn và liên kết về trang gốc. Sao chép quy mô lớn hoặc tái xuất bản có hệ thống cần được cho phép trước bằng văn bản."),
        _lead("Sources and external links.", "Nguồn và liên kết ngoài.",
              "USR links to third-party sources so readers can verify. We do not control and are not responsible for the content of those external sites.",
              "USR dẫn tới các nguồn bên thứ ba để người đọc kiểm chứng. Chúng tôi không kiểm soát và không chịu trách nhiệm về nội dung của các trang ngoài đó."),
        _lead("Changes.", "Thay đổi.",
              "These terms may be updated; the current version is always shown on this page with its effective date.",
              "Điều khoản này có thể được cập nhật; phiên bản hiện hành luôn hiển thị tại trang này kèm ngày hiệu lực."),
        _lead("Responsible party.", "Đơn vị chịu trách nhiệm.",
              f"{PH_EN}, {PH_EN}. Legal contact: {PH_EN}.",
              f"{PH_VN}, {PH_VN}. Liên hệ pháp lý: {PH_VN}."),
    ]


def privacy():
    return [
        _h("Privacy", "Quyền riêng tư"),
        _lead("We collect the minimum.", "Chúng tôi thu thập tối thiểu.",
              "USR is a reference site. To operate and improve it, we use anonymous traffic analytics that record aggregate figures such as page views and referral sources, not intended to identify individuals.",
              "USR là một trang tra cứu. Để hoạt động và cải thiện, chúng tôi dùng công cụ phân tích lượng truy cập ẩn danh, ghi nhận số liệu tổng hợp như lượt xem trang và nguồn truy cập, không nhằm nhận dạng cá nhân."),
        _lead("Newsletter sign-up.", "Đăng ký nhận tin.",
              "If you choose to leave an email to receive a newsletter, we use that email only to send the content you signed up for, and you can unsubscribe at any time.",
              "Nếu bạn chủ động để lại email để nhận bản tin, chúng tôi chỉ dùng email đó để gửi nội dung bạn đăng ký, và bạn có thể hủy bất kỳ lúc nào."),
        _lead("Third parties.", "Bên thứ ba.",
              "The analytics tool may set cookies per industry standard. We do not sell, rent or trade user data.",
              "Công cụ phân tích có thể đặt cookie theo tiêu chuẩn ngành. Chúng tôi không bán, không cho thuê và không trao đổi dữ liệu người dùng."),
        _lead("Your rights.", "Quyền của bạn.",
              f"You can ask what data we hold about you, request deletion, or withdraw a sign-up, through {PH_EN}.",
              f"Bạn có thể yêu cầu biết dữ liệu chúng tôi giữ về mình, yêu cầu xóa, hoặc rút đăng ký, qua {PH_VN}."),
        _h("Image attribution", "Ghi nguồn hình ảnh"),
        _p("Illustrative images on USR use only openly licensed images, public domain images, or images we own. Each image carries its attribution and license, and we track the copyright status of every asset.",
           "Hình ảnh minh họa trên USR chỉ dùng ảnh có giấy phép mở, ảnh thuộc phạm vi công cộng, hoặc ảnh do chúng tôi sở hữu. Mỗi ảnh mang thông tin ghi nguồn và giấy phép của nó, và chúng tôi theo dõi tình trạng bản quyền cho từng tư liệu."),
        _p(f"Illustrative images are clearly marked as illustrative and are not intended to depict a specific device or event unless captioned. If you believe an asset is used incorrectly, please report it through {PH_EN}; we review and address it promptly.",
           f"Ảnh minh họa được đánh dấu rõ là minh họa, không nhằm mô tả chính xác thiết bị hay sự kiện cụ thể trừ khi có chú thích. Nếu bạn cho rằng một tư liệu được dùng chưa đúng, xin báo qua {PH_VN}; chúng tôi rà soát và xử lý kịp thời."),
    ]


# (file, title_en, title_vn, eyebrow_en, eyebrow_vn, desc_en, effective_date?, blocks_fn)
PAGES = [
    ("about.html", "About Uncrewed Systems Review", "Về Uncrewed Systems Review", "About", "Về USR",
     "An independent data publication on uncrewed aerial systems and the low-altitude economy.", False, about),
    ("methodology.html", "Methodology and sources", "Phương pháp và nguồn", "Methodology", "Phương pháp",
     "How USR sources, tiers and verifies every figure in the registry.", False, methodology),
    ("contact.html", "Contact", "Liên hệ", "Contact", "Liên hệ",
     "How to reach USR for corrections, sources and collaboration.", False, contact),
    ("terms.html", "Terms of use", "Điều khoản sử dụng", "Terms", "Điều khoản",
     "Terms of use for the USR data publication.", True, terms),
    ("privacy.html", "Privacy and attribution", "Quyền riêng tư và ghi nguồn", "Privacy", "Quyền riêng tư",
     "How USR handles visitor data and image attribution.", True, privacy),
]

FOOT_NOTE = ('The entity, address, email and effective-date fields are being finalised and show a '
             'placeholder until confirmed.')
FOOT_NOTE_VN = ('Các mục pháp nhân, địa chỉ, email và ngày hiệu lực đang được chốt, tạm hiển thị '
                'chỗ trống cho tới khi xác nhận.')


def render(fname, title_en, title_vn, eye_en, eye_vn, desc, effective, blocks_fn):
    eff = (f'<p class="lg-eff">{bilingual(f"Effective date: {PH_EN}", f"Ngày hiệu lực: {PH_VN}")}</p>'
           if effective else "")
    body = "\n  ".join(blocks_fn())
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light" data-lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_en)} — USR</title>
{meta(f"{esc(title_en)} — USR", desc, fname)}
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="base/design-system.css">
<style>{LEGAL_CSS}</style>
</head>
<body>
{header("")}
<main>
  <article class="legal">
  <header class="lg-head"><span class="eyebrow">{bilingual(eye_en, eye_vn)}</span><h1>{bilingual(title_en, title_vn)}</h1>{eff}</header>
  {body}
  <p class="lg-foot">{bilingual(FOOT_NOTE, FOOT_NOTE_VN)}</p>
  </article>
</main>
{footer("")}
<script src="base/base.js"></script>
<script>USRBase.initTheme(document.getElementById("theme"));USRBase.initI18n(document.getElementById("lang"));</script>
</body>
</html>
"""


def main():
    for fname, t_en, t_vn, e_en, e_vn, desc, eff, fn in PAGES:
        (ROOT / fname).write_text(render(fname, t_en, t_vn, e_en, e_vn, desc, eff, fn))
    print(f"pages/: {len(PAGES)} trust+legal pages ({', '.join(p[0] for p in PAGES)})")


if __name__ == "__main__":
    main()
