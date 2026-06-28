---
type: data-note
title: "Bản đăng ký USR đọc thế nào: phạm vi, phương pháp và những ô để trống"
author: "Ban Dữ liệu USR"
human_author: null          # data-note thuần phương pháp, không luận điểm → AI-authorable
sample: false
date: 2026-06-24
entity_tags: []
figures:
  - { token: "total_uav", trace: "count(entity_type=uav)" }
  - { token: "total_company", trace: "count(entity_type=company)" }
  - { token: "total_country", trace: "distinct(country)" }
  - { token: "total_segment", trace: "distinct(segment)" }
  - { token: "spec_coverage", trace: "aggregates.spec_fill_rate" }
sources:
  - { claim: "toàn bộ số liệu", url: "USR Registry (nội bộ, đã kiểm)", tier: "A" }
---

# Bản đăng ký USR đọc thế nào: phạm vi, phương pháp và những ô để trống

Bản đăng ký Uncrewed Systems Review ghi nhận 302 hệ thống bay không người lái cùng 140 doanh nghiệp sản xuất, phân bố trên 28 quốc gia và 13 nhóm ứng dụng. Trước khi diễn giải bất kỳ con số nào trong tập dữ liệu này, người đọc cần nắm ba điều, gồm phạm vi của mẫu, nguyên tắc ghi nhận từng giá trị và cách hệ thống đánh dấu phần thông tin còn thiếu.

Tập dữ liệu là một bản đăng ký được tuyển chọn, không phải một cuộc điều tra thị trường. Mỗi bản ghi tương ứng với một mẫu thiết bị đã công bố công khai, kèm thông số mà nhóm biên tập kiểm chứng được. Vì mẫu do nhóm chủ động thu thập, các tỷ lệ tính trên tập này phản ánh cấu trúc của chính bản đăng ký chứ không suy ra được thị phần của một quốc gia hay một hãng trên thị trường thực.

Mỗi thuộc tính chỉ được điền khi có nguồn xác định. Khi thiếu nguồn, ô dữ liệu để trống thay vì điền một giá trị phỏng đoán. Cách xử lý này, gọi là honest-null, cho phép người đọc phân biệt giữa thông tin chưa thu thập được và thông tin đã xác nhận là không có.

Mỗi giá trị có nguồn đi kèm một mức tin cậy. Mức A dành cho kênh chính thức của nhà sản xuất hoặc tên miền của hãng. Mức B dành cho nguồn thứ cấp uy tín đã được đối chiếu, ví dụ hồ sơ doanh nghiệp công khai. Mức C dành cho các trang tổng hợp chưa kiểm chứng chéo. Người đọc nhìn vào mức này để tự cân nhắc độ chắc chắn của từng dữ kiện.

Khi các nguồn ghi khác nhau về cùng một thuộc tính, hệ thống giữ lại toàn bộ phiên bản kèm xuất xứ thay vì chọn một bên. Địa chỉ trụ sở của DJI là một trường hợp như vậy, khi ba nguồn ghi ba địa chỉ khác nhau và cả ba cùng hiển thị để người đọc thấy rõ điểm chưa thống nhất.

Trên toàn tập, các trường thông số kỹ thuật mới được điền khoảng 30 phần trăm. Trang tổng quan hiển thị tỷ lệ này theo từng trường, cho thấy rõ phần còn trống. Một bản đăng ký trung thực về giới hạn của mình có ích hơn một bảng số trông đầy đủ nhưng che giấu khoảng trống.

Vì những lý do trên, mọi biểu đồ phân bố trong USR nên được đọc kèm bối cảnh mẫu. Câu "Hoa Kỳ chiếm 108 trên 302 hệ thống" mô tả đúng bản đăng ký, song không đồng nghĩa với "Hoa Kỳ chiếm tỷ trọng tương ứng trên thị trường UAV toàn cầu". Khoảng cách giữa hai cách đọc này là điều người dùng cần giữ trong đầu suốt quá trình tra cứu.
