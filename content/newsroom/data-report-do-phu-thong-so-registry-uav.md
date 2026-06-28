---
type: data-report
title: "Bản đăng ký USR điền tới đâu: độ phủ thông số và mức tin cậy nguồn"
author: "Ban Dữ liệu USR"
human_author: null          # data-report mô tả phân bố trong registry, có disclosure mẫu → AI-authorable
sample: false
date: 2026-06-28
entity_tags: []
figures:                    # figure-trace THẬT, recompute sống từ registry UAV (khác loại fact-cào)
  - { token: "total_uav", trace: "count(entity_type=uav)" }
  - { token: "fill_mtow", trace: "aggregates.spec_fill_rate.mtow_kg" }
  - { token: "fill_ndaa", trace: "aggregates.spec_fill_rate.ndaa_compliant" }
  - { token: "fill_encryption", trace: "aggregates.spec_fill_rate.encryption" }
  - { token: "tier_a", trace: "aggregates.source_tier_counts.A" }
sources:
  - { claim: "Toàn bộ con số tính sống từ bản đăng ký", url: "USR Registry (nội bộ, đã kiểm)", tier: "A" }
---

# Bản đăng ký USR điền tới đâu: độ phủ thông số và mức tin cậy nguồn

Trên 302 hệ thống bay không người lái trong bản đăng ký USR, độ phủ thông số kỹ thuật chênh lệch lớn giữa các trường; phần lớn dữ kiện có nguồn ở mức tin cậy cao nhất.

Một bản đăng ký trung thực về giới hạn của mình cần cho thấy phần để trống, không chỉ phần đã điền. Vì các con số dưới đây tính trên một tập tuyển chọn gồm những mẫu thiết bị đã công bố công khai, chúng mô tả độ đầy của chính bản đăng ký, không phải mức độ minh bạch của ngành.

Khoảng cách giữa các trường là điều rõ nhất. Trọng lượng cất cánh tối đa được điền cho 185 trên 302 thiết bị, trong khi khả năng mã hoá chỉ có ở 3 trên 302. Giữa hai cực đó, các trường như tầm bay, tải trọng và trần bay được điền ở mức trung bình. Mỗi ô để trống là một giá trị honest-null, tức đã xác nhận là chưa thu thập được, chứ không phải một con số phỏng đoán điền cho đầy.

Mức tuân thủ là một trường mỏng có chủ đích. Thuộc tính NDAA chỉ được điền cho 35 trên 302 thiết bị, phản ánh việc thông tin tuân thủ hiếm khi được nhà sản xuất công bố dưới dạng kiểm chứng được. Bản đăng ký giữ trống phần còn lại thay vì suy ra, để người đọc không nhầm một ô trống thành một khẳng định.

Bù lại cho độ phủ không đều là chất lượng nguồn. Trong toàn bộ ô đã điền, có 1.799 giá trị đến từ nguồn mức A, tức kênh chính thức của nhà sản xuất, cao hơn hẳn số đến từ nguồn thứ cấp hay trang tổng hợp. Cách đọc đúng vì vậy là sàn tin cậy đứng cao trong khi độ đầy còn thấp, một trạng thái mà bản đăng ký chọn phơi ra thay vì che.

Vì những lý do trên, mọi tỷ lệ độ phủ trong bài cần được giữ trong khung mẫu tuyển chọn. Con số như 185 trên 302 mô tả đúng bản đăng ký tại thời điểm dựng, song không nói lên mức công bố thông số của toàn ngành UAV; mỗi giá trị đều truy được về nguồn để người dùng tự kiểm.
