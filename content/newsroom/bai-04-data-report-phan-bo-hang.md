---
type: data-report
title: "Phân bố nhà sản xuất trong bản đăng ký USR"
author: "Ban Dữ liệu USR"
human_author: null          # mô tả phân bố có nguồn, không luận điểm → AI-authorable
sample: false
date: 2026-06-24
entity_tags:
  - company:dji
  - company:autel
  - company:aerovironment
  - company:iai
figures:
  - { token: "maker_top", trace: "rank(count(uav) group by manufacturer)" }
  - { token: "total_company", trace: "count(entity_type=company)" }
  - { token: "sourced_company", trace: "count(company with >=1 sourced field)" }
sources:
  - { claim: "toàn bộ phân bố", url: "USR Registry (tính sống)", tier: "A" }
---

# Phân bố nhà sản xuất trong bản đăng ký USR

Trong 302 hệ thống bay không người lái mà bản đăng ký USR theo dõi, số lượng mẫu tập trung mạnh ở một nhóm nhỏ nhà sản xuất, còn phần lớn doanh nghiệp chỉ đóng góp một hoặc hai mẫu. DJI dẫn đầu với 38 hệ thống. Các con số dưới đây mô tả cấu trúc của tập dữ liệu, không phải thị phần trên thị trường thực.

Theo số liệu tính trực tiếp từ bản đăng ký, DJI ghi nhận 38 hệ thống, đứng đầu theo số mẫu. Autel Robotics theo sau với 13 thiết bị, rồi AeroVironment với 11. Israel Aerospace Industries, viết tắt IAI, có 10 mẫu sau khi gộp các biến thể tên gọi cùng một pháp nhân về một hồ sơ duy nhất.

Đặc điểm rõ nhất của phân bố là phần đuôi dài. Sau khoảng mười hãng đầu, đa số trong 140 doanh nghiệp còn lại chỉ xuất hiện với một tới hai mẫu. Cấu trúc này thường gặp ở các bản đăng ký ngành, nơi một số ít công ty lớn chiếm phần lớn sản lượng được ghi nhận, trong khi số đông nhà sản xuất nhỏ tạo nên một dải dài phía sau.

Trên 140 doanh nghiệp, mới 4 hồ sơ có ít nhất một thuộc tính kèm nguồn, gồm DJI, Autel, AeroVironment và Real-time Robotics. 136 trường hợp còn lại hiện ở trạng thái honest-null cho các trường định danh, do dữ liệu được suy ra từ quan hệ với sản phẩm chứ chưa được bổ sung xuất xứ riêng. Tỷ lệ này cho thấy rõ phần việc thu thập còn lại của bản đăng ký.

Vì tập dữ liệu là mẫu tuyển chọn, thứ hạng theo số mẫu phản ánh mức độ thu thập của nhóm biên tập, không trực tiếp đo quy mô doanh nghiệp hay doanh số. Một hãng có nhiều mẫu trong USR không nhất thiết lớn hơn một công ty có ít mẫu hơn. Người đọc nên xem bảng xếp hạng này là bản đồ của chính bản đăng ký, không phải bản đồ của thị trường.
