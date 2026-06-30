---
type: data-report
title: "Phân bố nhà sản xuất trong bản đăng ký USR"
author: "Ban Dữ liệu USR"
human_author: null          # mô tả phân bố có nguồn, không luận điểm → AI-authorable
sample: false
date: 2026-06-24
entity_tags:
  - company:dji
  - company:autel-robotics
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

Trong 444 hệ thống bay không người lái mà bản đăng ký USR theo dõi, số lượng mẫu tập trung mạnh ở một nhóm nhỏ nhà sản xuất, còn phần lớn doanh nghiệp chỉ đóng góp một hoặc hai mẫu. DJI dẫn đầu với 38 hệ thống. Các con số dưới đây mô tả cấu trúc của tập dữ liệu, không phải thị phần trên thị trường thực.

Theo số liệu tính trực tiếp từ bản đăng ký, DJI ghi nhận 38 hệ thống, đứng đầu theo số mẫu. AeroVironment theo sau với 18 thiết bị. Kế đó Autel Robotics và Israel Aerospace Industries, viết tắt IAI, cùng đạt 13 mẫu, riêng IAI là con số sau khi gộp các biến thể tên gọi cùng một pháp nhân về một hồ sơ duy nhất.

Đặc điểm rõ nhất của phân bố là phần đuôi dài. Sau khoảng mười hãng đầu, đa số trong 183 doanh nghiệp còn lại chỉ xuất hiện với một tới hai mẫu. Cấu trúc này thường gặp ở các bản đăng ký ngành, nơi một số ít công ty lớn chiếm phần lớn sản lượng được ghi nhận, trong khi số đông nhà sản xuất nhỏ tạo nên một dải dài phía sau.

Trên 183 doanh nghiệp, cả 183 hồ sơ giờ đều mang ít nhất một thuộc tính kèm nguồn: trụ sở (thành phố cùng quốc gia) đã được tra cứu và dẫn nguồn cho toàn bộ nhà sản xuất trong bản đăng ký, từ các hãng lớn nhất theo số mẫu như DJI, AeroVironment, Autel Robotics, IAI, Anduril và CASC cho tới phần đuôi dài chỉ một mẫu. Honest-null ở tầng định danh doanh nghiệp do đó đã đóng lại; phần thiếu còn lại nằm ở tầng thông số kỹ thuật của từng hệ thống, nơi độ phủ trung bình vẫn quanh một phần ba. Sự dịch chuyển này cho thấy trọng tâm thu thập đã chuyển từ định danh sang chiều sâu spec.

Vì tập dữ liệu là mẫu tuyển chọn, thứ hạng theo số mẫu phản ánh mức độ thu thập của nhóm biên tập, không trực tiếp đo quy mô doanh nghiệp hay doanh số. Một hãng có nhiều mẫu trong USR không nhất thiết lớn hơn một công ty có ít mẫu hơn. Người đọc nên xem bảng xếp hạng này là bản đồ của chính bản đăng ký, không phải bản đồ của thị trường.
