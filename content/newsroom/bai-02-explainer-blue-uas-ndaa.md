---
type: explainer
title: "Blue UAS và NDAA Section 848: hai bộ quy chuẩn nguồn gốc trong ngành UAV phòng thủ"
author: "Ban Dữ liệu USR"
human_author: null          # explainer factual có nguồn → AI-authorable
sample: false
date: 2026-06-24
entity_tags:
  - knowledge:blue-uas
  - knowledge:ndaa
figures:
  - { token: "blue_count", trace: "count(blue_uas=true)" }
  - { token: "ndaa_count", trace: "count(ndaa=true)" }
  - { token: "total_uav", trace: "count(entity_type=uav)" }
sources:
  - { claim: "Blue UAS do DIU thẩm định", url: "diu.mil", tier: "B" }
  - { claim: "NDAA Section 848 hạn chế linh kiện", url: "congress.gov (NDAA FY2020)", tier: "B" }
  - { claim: "số liệu ghi nhận", url: "USR Registry", tier: "A" }
---

# Blue UAS và NDAA Section 848: hai bộ quy chuẩn nguồn gốc trong ngành UAV phòng thủ

Trong các thương vụ UAV phục vụ cơ quan công và quốc phòng tại Hoa Kỳ, hai cụm từ xuất hiện thường xuyên là Blue UAS và NDAA Section 848. Cả hai liên quan tới nguồn gốc linh kiện cùng chuỗi cung ứng, nhưng đảm nhận vai trò khác nhau. Bài viết giải thích từng quy chuẩn, điểm phân biệt giữa chúng và mức độ ghi nhận trong bản đăng ký USR.

Blue UAS là danh sách các nền tảng bay không người lái do Defense Innovation Unit, viết tắt DIU, một đơn vị thuộc Bộ Quốc phòng Hoa Kỳ, thẩm định và phê duyệt cho cơ quan liên bang sử dụng. Một thiết bị nằm trong danh sách nghĩa là nó đã qua đánh giá về an ninh mạng và chuỗi cung ứng theo tiêu chí của đơn vị này.

NDAA, viết tắt của National Defense Authorization Act, là đạo luật ngân sách quốc phòng thường niên của Hoa Kỳ. Điều khoản 848 trong phiên bản năm tài khóa 2020 hạn chế việc mua sắm thiết bị bay không người lái có linh kiện trọng yếu xuất xứ từ một số quốc gia nhất định. Một sản phẩm được mô tả là tuân thủ NDAA khi không sử dụng các linh kiện bị giới hạn đó.

Hai quy chuẩn không đồng nhất. Blue UAS là một danh sách phê duyệt chủ động, trong đó thiết bị phải nộp hồ sơ và vượt qua đánh giá. NDAA là một ngưỡng pháp lý, theo đó sản phẩm đạt điều kiện về linh kiện thì được coi là tuân thủ mà không cần nằm trong một danh mục cụ thể. Hệ quả là một mẫu drone có thể đáp ứng NDAA nhưng chưa xuất hiện trong danh sách của DIU.

Với nhà sản xuất hướng tới khách hàng chính phủ, hai bộ tiêu chí này quyết định khả năng tiếp cận hợp đồng. Chúng cũng mở ra một hướng cạnh tranh dựa trên chuỗi cung ứng truy xuất được, song song với cạnh tranh về giá bán hoặc tính năng kỹ thuật.

Trên 444 hệ thống mà USR theo dõi, 26 thiết bị được ghi nhận có trong danh sách Blue UAS và 28 thiết bị được mô tả tuân thủ NDAA. Phần còn lại chưa được kiểm chứng theo hai quy chuẩn này. Bản đăng ký đánh dấu nhóm chưa kiểm chứng là honest-null, nghĩa là hệ thống không suy diễn rằng chúng không đạt, mà chỉ ghi nhận rằng dữ liệu xác nhận hiện chưa có.
