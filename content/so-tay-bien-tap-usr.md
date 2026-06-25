# SỔ TAY BIÊN TẬP — VIETNAM UAV INTELLIGENCE PLATFORM (USR Newsroom)

> Tài liệu lưu hành nội bộ · Hợp nhất từ ba nguồn: *Quy tắc biên tập Vietnam UAV Intelligence Platform* (bản gốc),
> kỷ luật dữ liệu của nền tảng (`newsroom-authoring.md`) và giọng văn rút từ bốn bài chuẩn vàng (`bai-01`…`bai-04`).
> Phiên bản 1.0 · Áp dụng thống nhất cho mọi người viết, con người hoặc AI.

---

## 0 · Tài liệu này dùng thế nào

Đây là chuẩn biên tập cho toàn bộ tin, bài xuất bản trên nền tảng, mục News, Knowledge, Analysis và các hồ sơ thực thể.

Tài liệu phục vụ ba đối tượng. Người viết dùng nó để soạn đúng cấu trúc, đúng giọng. Biên tập viên dùng nó để rà soát trước khi đăng. Người cấu hình linter dùng phần "gate cứng" để quy chiếu khi máy chặn bài.

Một nguyên tắc nền: **sự thật là của bản đăng ký, luận điểm là của người ký tên.** Số liệu truy được về nguồn; cây cầu suy luận từ số liệu sang nhận định là việc của một tác giả con người đứng tên, không phải của hệ thống.

Lưu ý: các quy tắc cấm bullet và cấm danh sách dưới đây áp cho **tin, bài xuất bản**. Bản thân sổ tay này là tài liệu tra cứu nên được phép dùng bảng và danh sách.

---

## 1 · Ranh giới tác giả — ai được viết gì

Đây là quy tắc quan trọng nhất, đặt trước mọi quy tắc văn phong.

### 1.1 · Bốn loại bài một AI được tự viết

Một người viết AI **chỉ** được tự đứng tên bốn loại sau, vì chúng trình bày sự thật có nguồn mà không bắc cầu luận điểm:

| Loại | Nội dung | Điều kiện |
|---|---|---|
| `data-note` | Phương pháp, phạm vi, cách lập tập dữ liệu, honest-null | Thuần phương pháp |
| `explainer` / `knowledge` | Giải thích khái niệm kỹ thuật có nguồn: Blue UAS, NDAA, RTK, BVLOS, GNSS | Mỗi khẳng định có nguồn |
| `company-profile` / `uav-profile` | Hồ sơ thực thể từ dữ liệu có nguồn | Disputed giữ cả claim |
| `data-report` | Mô tả phân bố trong bản đăng ký | Bắt buộc kèm câu disclosure mẫu tuyển chọn |

### 1.2 · Loại bài bắt buộc có tác giả con người đứng tên

Các loại sau phải có tên người thật trong trường `human_author`. AI không được là tác giả ẩn danh của một luận điểm.

Thuộc nhóm này: `opinion`, `analysis`, `editorial`, `forecast`, mọi bài dự báo, khuyến nghị hay chiến lược. Cũng thuộc nhóm này bất kỳ bài nào lập một luận điểm (argue a position) dù số liệu trong bài là thật. Thuộc nhóm này luôn cả bất kỳ câu nào có lợi hoặc bất lợi cho một doanh nghiệp cụ thể, đặc biệt Real-time Robotics, đơn vị vận hành nền tảng.

### 1.3 · Quy tắc kiểm chứng

Nếu bản nháp chứa một luận điểm mà `human_author` rỗng thì **báo cáo cho phụ trách biên tập, không đăng**. Số thật không miễn trừ khung sai. Hệ thống chứng được "36% tính đúng từ bản đăng ký", hệ thống không chứng được "36% trong bản đăng ký tự tuyển bằng cơ cấu thị trường Việt Nam". Khi người viết thấy mình đang diễn đạt lại một câu cho "an toàn hơn" thay vì cho đúng hơn, đó là tín hiệu dừng và báo cáo.

---

## 2 · Cấu trúc tin, bài

Tin, bài trình bày theo nguyên tắc hình tam giác ngược: thông tin quan trọng nhất lên đầu, thông tin ít quan trọng hơn đặt sau, đồng thời bảo đảm trả lời đủ 5W + 1H, gồm Who, What, When, Where, Why, How.

### 2.1 · Title (tiêu đề)

Tiêu đề ngắn gọn, nêu thẳng vấn đề, đủ sức kéo người đọc. Độ dài khoảng 8 đến 10 chữ, tối đa 15 chữ.

Quy ước dấu trên tiêu đề:

- Dấu ngoặc kép “…” trên tiêu đề viết thành ‘…’. Ví dụ: ‘Lòng tôi vẫn vang lời ca chiến thắng Điện Biên Phủ’.
- Hạn chế tiêu đề dạng trích dẫn, chỉ ưu tiên cho bài phỏng vấn nhân vật. Khi trích dẫn dùng dấu ‘…’.
- Sau dấu hai chấm viết hoa. Sau dấu gạch ngang không viết hoa. Hạn chế tối đa dấu hai chấm trên tiêu đề.
- Không dùng dấu chấm cảm hoặc dấu ba chấm. Hạn chế tối đa dấu hỏi. Không dùng dấu ngoặc đơn trên tiêu đề, trừ bài viết theo loạt kỳ dài.

### 2.2 · Lead (mở đầu)

Lead trích dẫn hoặc tóm tắt nội dung chính, đáng chú ý nhất của bài. Tối đa 40 chữ, tương đương một câu. Lead nêu cái gì, bao nhiêu, ở đâu.

### 2.3 · Body (nội dung)

Body trình bày thông tin chi tiết kèm trích dẫn và phần bối cảnh liên quan. Nêu rõ nguồn tin, hạn chế tối đa nguồn giấu tên kiểu "một người dân cho biết" hay "một quan chức cho rằng". Trích dẫn ngắn gọn, chọn ý đắt giá nhất, không trích quá dài. Các tiêu đề phụ trong bài in đậm.

---

## 3 · Văn phong — quy phạm báo chí khách quan

Người viết tường thuật, không bình luận. Văn phong khách quan dựa trên năm trụ sau.

**Hình tam giác ngược.** Dữ kiện quan trọng nhất nằm ở câu đầu.

**Ngôi thứ ba.** Không dùng "tôi". Byline là một ban biên tập, ví dụ Ban Dữ liệu USR, hoặc tên một người thật.

**Dẫn nguồn mọi dữ kiện.** Mỗi con số, mỗi khẳng định đi kèm xuất xứ, ví dụ "theo trang chính thức", "dữ liệu USR cho thấy", "ghi nhận trên PitchBook".

**Mô tả, không thuyết phục.** Tránh tính từ khen chê. Không dùng "vượt trội", "đáng tiếc", "ấn tượng".

**Không bắc cầu suy luận.** Không suy phân bố trong bản đăng ký thành khẳng định thị trường. Khi nêu phân bố luôn kèm câu nhắc đây là mẫu tuyển chọn.

### 3.1 · Câu và nhịp

Câu ngắn, chủ vị rõ, một ý một câu. Văn xuôi liền mạch. So sánh nhịp văn với bài chuẩn vàng `bai-01`: mỗi đoạn mở bằng một mệnh đề khẳng định, các câu sau bồi thêm bối cảnh, không câu nào để lửng một suy đoán.

### 3.2 · Luân phiên từ vựng

Không lặp một danh từ chính trong hai câu liền nếu thay được. Bộ từ luân phiên gợi ý:

- Thiết bị: UAV / drone / thiết bị bay không người lái / hệ thống.
- Doanh nghiệp: doanh nghiệp / hãng / nhà sản xuất / công ty.
- Dữ liệu: bản đăng ký / tập dữ liệu / registry.
- Động từ ghi nhận: ghi nhận / ghi / nêu / cho thấy.

### 3.3 · Thuật ngữ tiếng Anh

Giữ inline, không dịch ép: Blue UAS, NDAA, payload, endurance, honest-null, BVLOS, RTK, GNSS.

---

## 4 · Kỷ luật dữ liệu (zero-fabrication)

Phần này là khác biệt cốt lõi của nền tảng so với một tòa soạn thường.

**Không bịa.** Khi thiếu dữ kiện thì để trống hoặc bỏ câu, không phỏng đoán. Một ô trống là giá trị honest-null, đã xác nhận là vắng mặt, không phải chỗ để điền số ước.

**Figure truy nguồn sống.** Mỗi con số trong bài là một token tham chiếu tới bản đăng ký, không gõ cứng. Hệ thống tính lại từ dữ liệu gốc mỗi lần dựng, lệch là chặn.

**Một chiều E sang D.** Bài tham chiếu thực thể trong dữ liệu. Dữ liệu không bao giờ suy ngược từ câu chữ của bài. Sửa hoặc xóa một bài không được đổi một byte dữ liệu nền.

**Provenance.** Mọi dữ kiện có nguồn kèm mức tin cậy A, B hoặc C. Mức A là kênh chính thức của nhà sản xuất. Mức B là nguồn thứ cấp uy tín đã đối chiếu. Mức C là trang tổng hợp chưa kiểm chứng chéo. Thiếu nguồn thì bỏ câu hoặc honest-null.

**Disputed giữ cả hai.** Khi các nguồn ghi khác nhau về cùng một thuộc tính, trình bày mọi phiên bản kèm xuất xứ, không chọn bên. Địa chỉ trụ sở DJI trong `bai-03` là một ví dụ, ba nguồn ghi ba địa chỉ và cả ba cùng hiển thị.

**Câu disclosure mẫu.** Bài chứa phân bố phải có câu nhắc bản đăng ký là mẫu tuyển chọn, không phải thống kê thị trường. Mẫu câu: "Câu *Hoa Kỳ chiếm 108 trên 302 hệ thống* mô tả đúng bản đăng ký, song không đồng nghĩa với một tỷ trọng tương ứng trên thị trường UAV toàn cầu".

**Không gán quote cho người thật** trừ khi có nguồn trích dẫn. Pull-quote nội bộ phải ghi rõ "Quan điểm biên tập" và chỉ dùng trong bài có `human_author`.

---

## 5 · Quy tắc hình thức (gate cứng, linter chặn)

Những lỗi sau khiến `verify_content` dừng ở exit 2. Người viết tự lint trước khi nộp.

- **Không em-dash (—)** dùng làm dấu chen ngang. Thay bằng dấu phẩy, dấu chấm hoặc ngoặc đơn. Lưu ý phân biệt với dấu gạch nối ở mục 9, vốn dùng để nối từ ghép, nối hai từ đơn hay nối hai số.
- **Không dấu phẩy trước "và".**
- **Không mở danh sách bằng dấu hai chấm** trong đoạn văn của tin, bài.
- **Không bullet trong tin, bài.** Bài là văn xuôi liền mạch.
- **Không lặp từ gần nhau**, áp dụng bộ luân phiên ở mục 3.2.
- **Thuật ngữ tiếng Anh giữ inline**, không dịch ép.

---

## 6 · Chính tả — những từ không dùng

| Sai | Đúng |
|---|---|
| vạn | chục nghìn |
| thầy | thày |
| giầy | giày |
| tầu hỏa | tàu hỏa |
| ngàn | nghìn |
| tỉ | tỷ |
| sỹ | sĩ (trong nghệ sĩ, bác sĩ) |
| hằng ngày | hàng ngày |
| Liên hiệp quốc | Liên Hợp Quốc |
| che dấu | che giấu |
| giấu diếm | giấu giếm |

---

## 7 · Chính tả — những từ, cụm từ hay dùng sai

| Sai | Đúng |
|---|---|
| g (giờ) | h |
| khuyếch đại | khuếch đại |
| chuẩn đoán | chẩn đoán |
| chất độc màu da cam | chất độc da cam |
| khủy tay | khuỷu tay |
| khiếu giác | khứu giác |
| ngoằn nghèo | ngoằn ngoèo |
| sát nhập | sáp nhập |
| từ chối không | từ chối |
| cấm không | cấm |
| tất cả mọi | tất cả / mọi |
| tần xuất | tần suất |

---

## 8 · Viết tắt và viết hoa

### 8.1 · Viết tắt

Các cụm như "ủy ban nhân dân", "công nghệ thông tin" viết đầy đủ một lần ở đầu bài, sau đó mở ngoặc nêu cách viết tắt, ví dụ UBND, HĐXX, VKS, CNTT.

- Thành phố Hồ Chí Minh viết tắt là TP.HCM.
- Thành phố Hà Nội viết là TP Hà Nội.
- Quận 1, quận Tân Bình, quận Hoàn Kiếm không viết tắt là "Q.". Nếu không đứng đầu câu thì không viết hoa.
- Tên hai, ba chữ viết tắt thì viết liền nhau, ví dụ T.P., M.P.
- Tên viết tắt theo chữ đầu thì cách ra, ví dụ T. Phúc, B. Hạnh.

### 8.2 · Viết hoa

- "Internet" luôn viết hoa chữ cái đầu. "website" không viết hoa.
- Đơn vị tiền tệ viết tắt thì viết hoa toàn bộ, ví dụ USD, EUR. Viết đầy đủ thì không viết hoa, ví dụ ringgit, yen, baht.
- Thứ trong tuần và tên tháng không viết hoa, ví dụ thứ hai, chủ nhật, tháng ba, tháng giêng.
- Tên cơ quan, đoàn thể, đơn vị kinh tế xã hội gồm nhiều bộ phận viết hoa chữ cái đầu của mỗi danh từ chỉ bộ phận, ví dụ Bộ Khoa học và Công nghệ, Tổng cục Tiêu chuẩn Đo lường Chất lượng.
- Tên riêng cơ quan viết đầy đủ một lần trong bài rồi viết tắt, ví dụ Bộ KH-ĐT, Bộ KH&CN, NHNN, NHTM.
- Viết Bộ trưởng Khoa học và Công nghệ (không thêm "Bộ"), nhưng Thứ trưởng Bộ Khoa học và Công nghệ, Thứ trưởng Bộ Công Thương.

---

## 9 · Dấu gạch ngang, đơn vị, số, ngày tháng

### 9.1 · Dấu gạch ngang

- Nối trong một từ ghép thì viết liền, không cách, ví dụ big-bang, non-proxy.
- Nối hai từ đơn thì cách trước và sau, ví dụ Việt Nam - Campuchia.
- Nối hai số thì viết liền, không cách, ví dụ 300-400 m², trẻ em 1-5 tuổi, giai đoạn 2001-2002.

### 9.2 · Đơn vị và một số dấu đặc biệt

- Từ chỉ đơn vị, trừ "h" và "%", viết cách con số, ví dụ 60 km, 200 ha, 70.000 USD, 25.000 đồng/m³. Riêng 12h, 80% viết liền.
- Đơn vị dùng dấu "/" thì không cách trước và sau, ví dụ đồng/ha, m³/ngày, lít/người.
- Không dùng số quá lẻ, ví dụ tránh viết 95,76% hoặc 236.427.000 đồng.
- Tên sách, báo dẫn trong bài in nghiêng, viết hoa chữ đầu, ví dụ báo Tuổi Trẻ, tờ The Economist.

### 9.3 · Ngày tháng

- Dùng dấu "/" để phân cách ngày, tháng, năm, ghi rõ năm, không viết tắt "01", "02", ví dụ 14/3/2005.
- Không ghi năm hiện tại, ví dụ chỉ cần viết 14/3 khi mặc định là năm nay.
- Viết quý 1, quý 2, quý 3, không dùng số La Mã.

---

## 10 · Frontmatter bắt buộc

Mỗi bài mở đầu bằng khối frontmatter sau. Trường `human_author` để rỗng chỉ khi bài thuộc bốn loại AI được tự viết ở mục 1.1, ngược lại bắt buộc tên thật.

```yaml
type:           # data-note | explainer | company-profile | uav-profile | data-report | (opinion/analysis CẦN human_author)
title:
author:         # byline ban biên tập hoặc tên người
human_author:   # null nếu thuộc 4 loại ở mục 1.1; bắt buộc tên thật nếu bài có luận điểm
sample: false
date:
entity_tags: []         # chỉ trỏ thực thể thật trong graph
figures: []             # mỗi figure {token, trace}, trace tính lại được
sources: []             # mỗi nguồn {claim, url, tier: A|B|C}
```

Entity-tag chỉ trỏ thực thể thật. Tag treo sẽ bị chặn. Thuật ngữ Knowledge xuất hiện trong body tự động liên kết về trang giải nghĩa. Bài tự xuất hiện trên trang thực thể đã tag, không gắn link thủ công.

---

## 11 · Bộ kiểm tự động phải chứng (teeth)

| Teeth | Bắt gì |
|---|---|
| `CONTENT_FIGURE_DRIFT` | Figure trong bài khác số tính lại từ bản đăng ký |
| `OPINION_REQUIRES_HUMAN_AUTHOR` | Bài opinion/analysis hoặc body có luận điểm mà `human_author` rỗng |
| `DANGLING_TAG` | `entity_tag` trỏ thực thể không tồn tại |
| `FORMAT_VIOLATION` | Có em-dash, phẩy trước "và", colon-list hoặc bullet trong văn xuôi bài |
| `SAMPLE_DISCLOSURE_MISSING` | `data-report` nêu phân bố mà thiếu câu disclosure mẫu |
| `SOURCE_MISSING` | Dữ kiện không nằm trong `sources` |

---

## 12 · Checklist trước khi đăng

Quy trình: soạn nháp, tự lint theo mục 5, chạy `verify_content`, gửi báo cáo hoàn thành cho phụ trách biên tập kiểm. Trước khi đăng, rà soát lần cuối:

- [ ] Lead trả lời cái gì, bao nhiêu, ở đâu trong tối đa 40 chữ.
- [ ] Tiêu đề 8 đến 15 chữ, đúng quy ước dấu ở mục 2.1.
- [ ] Mọi con số có figure-trace, mọi dữ kiện có nguồn kèm tier.
- [ ] Không câu nào lập luận điểm khi `human_author` rỗng.
- [ ] Bài phân bố có câu disclosure mẫu tuyển chọn.
- [ ] Disputed giữ đủ mọi phiên bản kèm xuất xứ.
- [ ] Không em-dash, không phẩy trước "và", không bullet, không colon-list trong văn xuôi.
- [ ] Đã quét bảng chính tả mục 6 và mục 7.
- [ ] Đơn vị, ngày tháng, viết hoa, viết tắt đúng mục 8 và mục 9.
- [ ] Từ vựng luân phiên, không lặp danh từ chính hai câu liền.

---

## 13 · Ví dụ trước và sau

**Tiêu đề.** Trước: "Thật ấn tượng! Trung Quốc đang vượt trội về số lượng drone…?". Sau: ‘Trung Quốc đứng thứ hai về số mẫu trong bản đăng ký USR’. Lý do: bỏ chấm cảm, bỏ dấu hỏi, bỏ tính từ khen, nêu thẳng dữ kiện.

**Bắc cầu suy luận.** Trước: "Với 96 hệ thống, Trung Quốc thống trị thị trường UAV khu vực". Sau: "Bản đăng ký ghi nhận 96 hệ thống của Trung Quốc trên tổng số 302. Tỷ lệ này phản ánh cấu trúc của mẫu tuyển chọn, không suy ra thị phần thực". Lý do: tách số thật khỏi nhận định thị trường.

**Em-dash.** Trước: "DJI — hãng lớn nhất theo số mẫu — đặt trụ sở tại Thâm Quyến". Sau: "DJI, hãng có nhiều mẫu nhất trong bản đăng ký, đặt trụ sở tại Thâm Quyến". Lý do: thay em-dash bằng cặp phẩy, thay "lớn nhất" bằng tiêu chí đo được.

**Honest-null.** Trước: "Tầm bay ước khoảng 30 km". Sau: "Bản đăng ký chưa ghi nhận tầm bay của mẫu này". Lý do: không điền số phỏng đoán, nêu rõ ô để trống.

---

*Hết. Mọi điều chỉnh, bổ sung cập nhật qua bộ phận biên tập phụ trách và đồng bộ lại với linter `verify_content`.*
