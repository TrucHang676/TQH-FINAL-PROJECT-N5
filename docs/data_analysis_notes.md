# LƯU Ý KỸ THUẬT KHI PHÂN TÍCH & TRỰC QUAN HÓA DỮ LIỆU
## Đồ án: Trực quan hóa dữ liệu tuyển dụng IT tại Việt Nam (Nhóm 05)

Tài liệu này tổng hợp các đặc thù dữ liệu, hạn chế kỹ thuật và mã code mẫu (Pandas) hướng dẫn các thành viên trong nhóm xử lý khi lập trình dashboard trực quan hóa dữ liệu từ file dữ liệu đã xử lý: [vietnam_it_jobs_processed.csv](file:///d:/BaiTapKi2Nam3/TQHDL/Final/data/processed/vietnam_it_jobs_processed.csv).

---

## I. TỔNG QUAN BỘ DỮ LIỆU
* **Tổng số dòng**: `8,452` dòng (bản ghi job IT sạch).
* **Tổng số cột**: `18` cột.
* **Cột kiểu số (`float64`)**: `luong_min`, `luong_max`, `luong_tb` (Đơn vị: **Triệu VND/tháng**).
* **Cột kiểu chuỗi (`object`)**: Các cột còn lại.

---

## II. 7 LƯU Ý QUAN TRỌNG KÈM CODE MẪU

### 1. Phân tích Mức lương (Salary Analysis)
> [!IMPORTANT]
> **Chỉ phân tích trên tập con (~49.2% dữ liệu)**
> * Khoảng **50.8%** số dòng trong dữ liệu là lương thỏa thuận (`loai_luong == 'negotiable'`), dẫn đến các cột lương số (`luong_tb`, `luong_min`, `luong_max`) đều bị khuyết (`NaN`).
> * **Hướng xử lý (Pandas):** Bắt buộc phải lọc bỏ các dòng có giá trị lương bị khuyết trước khi vẽ các biểu đồ về lương (như Box Plot, Bar Chart lương trung bình).

```python
# Code mẫu lọc dữ liệu lương
df_salary = df[df['luong_tb'].notna() & (df['luong_tb'] > 0)]

# Tính lương trung bình theo nhóm vị trí
salary_by_role = df_salary.groupby('nhom_vi_tri')['luong_tb'].mean().reset_index()
```

---

### 2. Phân tích Xu hướng theo Thời gian (Time-series Analysis)
> [!WARNING]
> **Nguồn dữ liệu VietJobs không có ngày đăng**
> * Nguồn dữ liệu VietJobs (chiếm **16.28%** tổng dữ liệu) hoàn toàn không có thông tin ngày đăng (`ngay_dang` và `thang_dang` bị `NaN`).
> * **Hướng xử lý (Pandas):** Khi vẽ biểu đồ xu hướng tuyển dụng theo các tháng (`thang_dang`), bạn phải lọc bỏ các dòng `NaN` này. Hãy ghi chú dưới biểu đồ: *"Biểu đồ đường xu hướng thời gian không bao gồm nguồn VietJobs"*.

```python
# Code mẫu lọc dữ liệu thời gian
df_time = df[df['thang_dang'].notna() & (df['thang_dang'] != '')]

# Thống kê số lượng job tuyển dụng theo tháng đăng
jobs_by_month = df_time.groupby('thang_dang').size().reset_index(name='so_luong_job')
```

---

### 3. Thiên lệch Địa lý (Geography Bias) & Cảnh báo cỡ mẫu nhỏ
> [!CAUTION]
> **Cẩn thận khi tính lương trung bình ở các tỉnh thành nhỏ**
> * Dữ liệu tập trung cực kỳ lớn ở **TP.HCM (4,454 dòng)** và **Hà Nội (3,187 dòng)**.
> * Các tỉnh thành khác có cỡ mẫu rất nhỏ (ví dụ: Đà Nẵng chỉ có 66 dòng, Hải Phòng 40 dòng, Bình Dương 9 dòng). Một vài job có lương quá cao hoặc quá thấp ở các khu vực này sẽ làm sai lệch hoàn toàn giá trị trung bình (`mean`).
> * **Hướng xử lý (Pandas):** Đối với các tỉnh thành nhỏ ngoài HN và HCM, khuyến khích sử dụng cột `vung_mien` (Bắc/Trung/Nam) để vẽ biểu đồ tổng quát thay vì vẽ chi tiết từng tỉnh để đảm bảo ý nghĩa thống kê.

```python
# Ví dụ phân tích theo Vùng miền thay vì tỉnh lẻ
jobs_by_region = df.groupby('vung_mien').size().reset_index(name='so_luong')
```

---

### 4. Thiên lệch Nguồn dữ liệu (Source Bias)
> [!NOTE]
> **Phân khúc ứng viên khác nhau giữa các trang web tuyển dụng**
> * **ITviec** và **TopDev** (Chuyên IT, nhiều job tiếng Anh/yêu cầu cao) $\rightarrow$ Lương trung bình cao hơn.
> * **Vieclam24h** (Tuyển dụng phổ thông, nhiều job Support/Vận hành máy tính) $\rightarrow$ Yêu cầu thấp hơn và lương trung bình thấp hơn.
> * **Hướng xử lý:** Khi so sánh lương hoặc kỹ năng giữa các nguồn (`nguon`), cần ghi chú rõ đặc thù phân khúc của từng trang để tránh người đọc hiểu lầm là các doanh nghiệp trả lương bất công giữa các trang.

---

### 5. Tỷ lệ "Không rõ" ở cột Cấp độ kinh nghiệm
> [!NOTE]
> **Nhóm "Không rõ" chiếm tỷ trọng lớn**
> * Có tới **62.3%** số dòng có cấp độ kinh nghiệm là `"Không rõ"` (do tin tuyển dụng gốc không ghi số năm kinh nghiệm yêu cầu).
> * **Hướng xử lý (Pandas):** 
>   - *Cách 1:* Vẽ cả nhóm `"Không rõ"` vào biểu đồ tròn (Pie Chart) cơ cấu kinh nghiệm để phản ánh đúng thực tế tin đăng.
>   - *Cách 2:* Loại bỏ nhóm `"Không rõ"` khi phân tích chi tiết kỹ năng/lương theo kinh nghiệm.

```python
# Lọc bỏ nhóm Không rõ để phân tích mối tương quan giữa kinh nghiệm và mức lương
df_exp = df[df['cap_do_kinh_nghiem'] != 'Không rõ']
```

---

### 6. Nhóm vị trí "Other" chiếm tỷ trọng lớn
> [!WARNING]
> * Nhóm vị trí `Other` chiếm tới **11.6%** (982 dòng). Đây là nhóm các công việc IT đặc thù không khớp với các từ khóa của 10 nhóm chính (ví dụ: kỹ sư mạng viễn thông, kỹ sư phần cứng, giảng viên IT...).
> * **Hướng xử lý:** Trong dashboard, tại phần chú thích biểu đồ cơ cấu công việc, cần ghi rõ nhóm `Other` đại diện cho các công việc phần cứng, mạng hoặc giảng dạy IT để người đọc nắm thông tin.

---

### 7. Phân tích cột Kỹ năng (`ky_nang`) để vẽ Word Cloud / Bar Chart
> [!IMPORTANT]
> **Kỹ năng là một chuỗi phân cách bởi dấu phẩy**
> * Cột `ky_nang` chứa chuỗi các kỹ năng (ví dụ: `Python, SQL, Machine Learning`). Khi phân tích top kỹ năng, ta cần dùng Pandas tách nhỏ (explode) chuỗi này ra thành từng hàng độc lập.
> * Đồng thời, cột này chứa cả kỹ năng bổ trợ (English, Agile, Scrum) bên cạnh các công nghệ (Java, ReactJS). Nên cung cấp bộ lọc hoặc ghi chú để phân loại.

```python
# Code mẫu phân tách chuỗi kỹ năng để vẽ biểu đồ cột Top 10 Kỹ năng
df_skills = df[df['ky_nang'].notna()].copy()
# Tách các kỹ năng thành danh sách
df_skills['ky_nang_list'] = df_skills['ky_nang'].str.split(', ')
# Explode danh sách thành các dòng riêng biệt
exploded_skills = df_skills.explode('ky_nang_list')

# Thống kê Top 10 kỹ năng phổ biến nhất
top_skills = exploded_skills['ky_nang_list'].value_counts().head(10).reset_index()
top_skills.columns = ['ky_nang', 'so_lan_xuat_hien']
```
