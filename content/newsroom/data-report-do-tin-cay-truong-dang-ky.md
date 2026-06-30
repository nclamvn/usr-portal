---
type: data-report
title: "Độ tin cậy theo trạng thái trường trong bản đăng ký USR"
author: "Ban Dữ liệu USR"
human_author: null
sample: false
date: 2026-06-28
entity_tags: []
figures:
  - { token: "fs_verified", trace: "aggregates.field_status_counts.verified" }
  - { token: "fs_derived", trace: "aggregates.field_status_counts.derived" }
  - { token: "fs_unverified", trace: "aggregates.field_status_counts.unverified" }
  - { token: "fs_disputed", trace: "aggregates.field_status_counts.disputed" }
graphic:
  kind: count
  value: "2.905"
  label: "trường đã kiểm"
  status: "registry USR"
sources:
  - { claim: "Toàn bộ con số tính sống từ bản đăng ký", url: "USR Registry (nội bộ, đã kiểm)", tier: "A" }
---

# Độ tin cậy theo trạng thái trường trong bản đăng ký USR

Trong bản đăng ký USR, 2.905 trường dữ liệu đã được kiểm chứng trong khi chỉ 6 trường đang ở trạng thái tranh chấp.

Các con số dưới đây mô tả cấu trúc của tập dữ liệu tuyển chọn, không phải mức độ minh bạch của toàn ngành. Mỗi trạng thái là một nhãn nội bộ về độ chắc của từng ô, nên tỷ lệ giữa chúng phản ánh cách bản đăng ký ghi nhận chứ không phải chất lượng dữ liệu của thị trường UAV.

Phần lớn giá trị đã có nguồn xác định, với 2.905 trường mang trạng thái đã kiểm. Bên cạnh đó là 267 trường suy ra từ phân loại nội bộ và 37 trường chưa kiểm, hai nhóm được tách riêng để người đọc không nhầm với phần đã xác nhận.

Phần tranh chấp rất nhỏ nhưng được giữ nguyên thay vì xoá. Khi các nguồn ghi khác nhau về cùng một thuộc tính, hệ thống giữ cả các phiên bản và đánh dấu là tranh chấp, hiện có 6 trường như vậy. Cách phơi bày này cho thấy bản đăng ký chọn minh bạch về điểm chưa thống nhất hơn là ép một con số duy nhất.

Vì những lý do trên, các trạng thái này nên được đọc trong khung mẫu tuyển chọn. Mỗi con số đều tính sống từ bản đăng ký tại thời điểm dựng trang, nên khi dữ liệu thay đổi thì cổng kiểm sẽ bắt được sai lệch giữa văn bản và số thật.
