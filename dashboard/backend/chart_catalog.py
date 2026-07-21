# Danh mục các biểu đồ THẬT đang hiển thị trên dashboard (trang 1-4), dùng cho
# tính năng "Nhận xét dựa trên biểu đồ có sẵn" của trang 5 (AI phân tích).
#
# Mục đích: khi câu hỏi của người dùng trùng với 1 trong các câu hỏi mục tiêu phân
# tích đã có sẵn biểu đồ, hệ thống KHÔNG bắt AI sinh code mới — mà gọi lại đúng hàm
# vẽ biểu đồ đã có, rút số liệu thật từ đó, rồi mới nhờ AI nhận xét trên đúng số đó.
# Điều này đảm bảo số liệu AI trích dẫn LUÔN khớp với con số đang hiển thị trên
# dashboard (không lệch do AI tự viết code lọc/gộp khác đi).
#
# CHỈ đăng ký các hàm mà router thực sự gọi tới (đã kiểm tra từng router_pageN.py).
# Cố tình BỎ QUA 4 hàm đã viết nhưng không router nào dùng tới (hàm "chết"):
# create_regional_vietnam_map, create_region_chart, create_provincial_bar_chart,
# create_salary_box_chart — vì nếu dùng nhầm sẽ cho ra số không khớp dashboard thật.

import backend.utils.charts_page1 as charts_page1
import backend.utils.charts_page2 as charts_page2
import backend.utils.charts_page3 as charts_page3
import backend.utils.charts_page4 as charts_page4
import backend.utils.charts_extra as charts_extra

# Mỗi mục gồm:
# - id: mã định danh duy nhất, dùng để AI trả về khi định tuyến câu hỏi
# - trang: trang dashboard đang hiển thị biểu đồ này (1-4)
# - cau_hoi: câu hỏi mục tiêu phân tích mà biểu đồ này trả lời (đúng văn phong báo cáo)
# - mo_ta: mô tả ngắn cho AI biết biểu đồ dùng cột nào, tính gì — giúp AI chọn đúng
#   mục khi câu hỏi người dùng diễn đạt khác đi (không cần trùng chữ với cau_hoi)
# - build_fn: hàm vẽ biểu đồ thật, nhận (df) là DataFrame đầy đủ chưa lọc, trả về
#   1 đối tượng Figure của Plotly — GIỐNG HỆT hàm mà router_pageN.py đang gọi.
CHART_CATALOG = [
    {
        "id": "P1-01",
        "trang": 1,
        "cau_hoi": "Nhu cầu tuyển dụng IT tại Việt Nam biến động như thế nào qua các tháng và năm?",
        "mo_ta": "Xu hướng số lượng tin tuyển dụng theo thời gian, dùng cột 'thang_dang' để đếm số tin theo từng tháng.",
        "build_fn": charts_page1.create_time_trend_chart,
    },
    {
        "id": "P1-02a",
        "trang": 1,
        "cau_hoi": "Nhu cầu tuyển dụng IT phân bố như thế nào giữa các TỈNH/THÀNH tại Việt Nam?",
        "mo_ta": "Số lượng tin tuyển dụng theo từng tỉnh/thành cụ thể (cột 'tinh_thanh'), hiển thị dạng bản đồ. Dùng khi câu hỏi hỏi về TỈNH/THÀNH PHỐ cụ thể (VD: Hà Nội, TP.HCM, Đà Nẵng).",
        "build_fn": charts_page1.create_vietnam_map,
    },
    {
        "id": "P1-02b",
        "trang": 1,
        "cau_hoi": "Nhu cầu tuyển dụng IT phân bố như thế nào giữa các VÙNG MIỀN tại Việt Nam?",
        "mo_ta": "Số lượng tin tuyển dụng theo từng vùng miền (cột 'vung_mien': Bắc/Trung/Nam/Khác). Dùng khi câu hỏi hỏi về VÙNG MIỀN chứ không phải tỉnh/thành cụ thể.",
        "build_fn": charts_page1.create_region_vertical_chart,
    },
    {
        "id": "P1-03",
        "trang": 1,
        "cau_hoi": "Hình thức làm việc nào (Full-time, Remote/Từ xa, Internship...) đang chiếm ưu thế trên thị trường?",
        "mo_ta": "Tỷ trọng các hình thức làm việc (cột 'hinh_thuc_lam_viec': Full-time, Part-time, Internship, Contract, Khác).",
        "build_fn": charts_page1.create_work_type_chart,
    },
    {
        "id": "P2-01",
        "trang": 2,
        "cau_hoi": "Top 15 kỹ năng công nghệ được săn đón nhiều nhất trong ngành IT là gì?",
        "mo_ta": "Top 15 kỹ năng xuất hiện nhiều nhất trong tất cả tin tuyển dụng, tách từ cột 'ky_nang' (danh sách cách nhau bởi dấu phẩy).",
        "build_fn": charts_page2.create_top_skills_chart,
    },
    {
        "id": "P2-02",
        "trang": 2,
        "cau_hoi": "Yêu cầu kỹ năng công nghệ có sự khác biệt như thế nào giữa các nhóm vị trí công việc chính?",
        "mo_ta": "Ma trận nhiệt (heatmap) thể hiện số lượng/tỷ lệ mỗi kỹ năng xuất hiện trong từng nhóm vị trí (cột 'nhom_vi_tri' × 'ky_nang'). Dùng khi câu hỏi so sánh kỹ năng GIỮA CÁC NHÓM VỊ TRÍ.",
        "build_fn": charts_page2.create_skills_heatmap,
    },
    {
        "id": "P2-03",
        "trang": 2,
        "cau_hoi": "Nhu cầu đối với các công nghệ mới (như AI, Machine Learning, Cloud) có xu hướng tăng trưởng theo thời gian không?",
        "mo_ta": "Xu hướng số lượng tin yêu cầu các nhóm công nghệ mới (AI/ML, Cloud, DevOps, Data Engineering) qua từng tháng (cột 'thang_dang' × 'ky_nang').",
        "build_fn": charts_page2.create_tech_trend_chart,
    },
    {
        "id": "P3-01",
        "trang": 3,
        "cau_hoi": "Mức lương trung bình của ngành IT Việt Nam phân bố như thế nào và tỷ lệ tin tuyển dụng sẵn sàng công khai khoảng lương là bao nhiêu?",
        "mo_ta": "Phân bố mức lương trung bình (cột 'luong_tb', đã dropna) và tỷ lệ tin theo 'loai_luong' (range/negotiable/to/from) — tỷ lệ công khai vs thỏa thuận.",
        "build_fn": charts_page3.create_salary_distribution_chart,
        "lien_quan": ["P4-03"],
    },
    {
        "id": "P3-02",
        "trang": 3,
        "cau_hoi": "Mức lương trung bình chênh lệch như thế nào giữa các nhóm vị trí công việc và cấp độ kinh nghiệm khác nhau?",
        "mo_ta": "Ma trận nhiệt (heatmap) mức lương trung bình theo 'nhom_vi_tri' × 'cap_do_kinh_nghiem'.",
        "build_fn": charts_page3.create_salary_by_position_experience_chart,
        "lien_quan": ["P2-02"],
    },
    {
        "id": "P3-03",
        "trang": 3,
        "cau_hoi": "Các trung tâm công nghệ (Hà Nội, TP.HCM, Đà Nẵng) và hình thức làm việc từ xa (Remote) có sự chênh lệch như thế nào về mức lương chi trả?",
        "mo_ta": "So sánh mức lương trung bình giữa các tỉnh/thành lớn (cột 'tinh_thanh') và nhóm làm việc từ xa (cột 'vung_mien' = 'Khác' hoặc 'hinh_thuc_lam_viec' liên quan Remote).",
        "build_fn": charts_page3.create_salary_by_location_chart,
        "lien_quan": ["P1-02a"],
    },
    {
        "id": "P4-01",
        "trang": 4,
        "cau_hoi": "Cơ hội việc làm dành cho nhóm ít kinh nghiệm (Intern, Fresher, Junior) chiếm tỷ trọng bao nhiêu trong số tin tuyển dụng có ghi rõ cấp bậc kinh nghiệm?",
        "mo_ta": "Cơ cấu phân bổ tin tuyển dụng theo từng cấp độ kinh nghiệm (cột 'cap_do_kinh_nghiem'), chỉ tính trên các tin đã ghi rõ cấp bậc (loại bỏ 'Không rõ').",
        "build_fn": charts_page4.create_experience_distribution_chart,
        "lien_quan": ["P4-02"],
    },
    {
        "id": "P4-02",
        "trang": 4,
        "cau_hoi": "Những nhóm vị trí công việc nào cởi mở nhất và có nhu cầu tuyển dụng đối tượng Intern, Fresher, Junior cao nhất?",
        "mo_ta": "Treemap thể hiện quy mô và tỷ lệ % tin dành cho Intern/Fresher/Junior trong từng nhóm vị trí (cột 'nhom_vi_tri' × 'cap_do_kinh_nghiem').",
        "build_fn": charts_page4.create_youth_opportunity_treemap,
        "lien_quan": ["P4-01"],
    },
    {
        "id": "P4-03",
        "trang": 4,
        "cau_hoi": "Mức lương khởi điểm thực tế (lương trung bình) dành cho đối tượng Intern và Fresher tại Việt Nam là bao nhiêu, và mức lương này chênh lệch như thế nào giữa các nhóm vị trí công việc?",
        "mo_ta": "Box plot phân bố mức lương trung bình ('luong_tb') của riêng Intern và Fresher, tách theo từng nhóm vị trí ('nhom_vi_tri').",
        "build_fn": charts_page4.create_youth_salary_boxplot,
        "lien_quan": ["P3-01"],
    },

    # --- Câu hỏi MỞ RỘNG (EX-1..EX-6): chuẩn bị trước cho buổi vấn đáp, nằm NGOÀI
    # 5 mục tiêu phân tích chính nên KHÔNG hiển thị ở trang dashboard 1-4 nào —
    # "trang": 0 đánh dấu điều này (get_catalog_prompt_listing hiển thị "mở rộng"
    # thay vì "trang 0"). Logic tính toán đã được kiểm chứng chạy đúng trên dữ liệu
    # thật trước khi đăng ký (xem dashboard/backend/ai_prepared_questions.json).
    {
        "id": "EX-1",
        "trang": 0,
        "cau_hoi": "Kỹ năng nào đặc trưng cho cấp Senior nhưng ít xuất hiện ở Junior/Fresher?",
        "mo_ta": "So sánh tỷ lệ % xuất hiện của từng kỹ năng công nghệ (cột 'ky_nang') giữa nhóm Senior và nhóm Junior/Fresher (cột 'cap_do_kinh_nghiem'), lấy top 15 kỹ năng có chênh lệch cao nhất nghiêng về Senior.",
        "build_fn": charts_extra.create_senior_signature_skills_chart,
        "lien_quan": ["P2-02"],
    },
    {
        "id": "EX-2",
        "trang": 0,
        "cau_hoi": "Nhóm vị trí nào có mức lương trung bình cao nhất và thấp nhất?",
        "mo_ta": "Lương trung bình ('luong_tb', đã dropna) tính theo từng nhóm vị trí ('nhom_vi_tri'), làm nổi bật nhóm cao nhất và thấp nhất.",
        "build_fn": charts_extra.create_salary_extremes_by_position_chart,
        "lien_quan": ["P3-02"],
    },
    {
        "id": "EX-3",
        "trang": 0,
        "cau_hoi": "Nếu tôi biết kỹ năng Python, nên ứng tuyển vào nhóm vị trí nào?",
        "mo_ta": "Lọc các tin tuyển dụng có yêu cầu kỹ năng Python (cột 'ky_nang'), thống kê số lượng tin và lương trung bình ('luong_tb') theo từng nhóm vị trí ('nhom_vi_tri').",
        "build_fn": charts_extra.create_python_position_recommendation_chart,
        "lien_quan": ["P2-01"],
    },
    {
        "id": "EX-4",
        "trang": 0,
        "cau_hoi": "Chức danh công việc nào xuất hiện phổ biến nhất trong các tin tuyển dụng IT?",
        "mo_ta": "Top 15 chức danh công việc (cột 'ten_cong_viec') xuất hiện nhiều nhất trong toàn bộ tin tuyển dụng.",
        "build_fn": charts_extra.create_top_job_titles_chart,
        "lien_quan": ["P1-01"],
    },
    {
        "id": "EX-5",
        "trang": 0,
        "cau_hoi": "Hình thức làm việc (Full-time/Part-time/Internship/Contract) phân bố khác nhau như thế nào giữa các nhóm vị trí công việc?",
        "mo_ta": "Số lượng tin tuyển dụng theo từng hình thức làm việc (cột 'hinh_thuc_lam_viec'), tách theo từng nhóm vị trí ('nhom_vi_tri'). Dùng khi câu hỏi so sánh hình thức làm việc GIỮA CÁC NHÓM VỊ TRÍ (khác P1-03 chỉ xem tổng thể toàn thị trường, không tách theo vị trí).",
        "build_fn": charts_extra.create_work_type_by_position_chart,
        "lien_quan": ["P1-03"],
    },
    {
        "id": "EX-6",
        "trang": 0,
        "cau_hoi": "Những kỹ năng nào thường xuất hiện cùng nhau nhiều nhất trong cùng một tin tuyển dụng?",
        "mo_ta": "Top 20 cặp kỹ năng công nghệ (cột 'ky_nang') xuất hiện chung trong cùng 1 tin tuyển dụng nhiều nhất.",
        "build_fn": charts_extra.create_top_skill_pairs_chart,
        "lien_quan": ["P2-01"],
    },
]


def get_catalog_prompt_listing():
    """Dựng đoạn văn bản liệt kê danh mục để đưa vào prompt định tuyến câu hỏi cho AI."""
    lines = []
    for item in CHART_CATALOG:
        # trang=0 (câu hỏi mở rộng EX-*) không thuộc trang dashboard nào cụ thể
        trang_label = f"trang {item['trang']}" if item['trang'] else "mở rộng"
        lines.append(f"- {item['id']} ({trang_label}): \"{item['cau_hoi']}\" — {item['mo_ta']}")
    return "\n".join(lines)


def get_catalog_item(chart_id: str):
    """Tìm 1 mục trong danh mục theo id. Trả về None nếu không tìm thấy."""
    for item in CHART_CATALOG:
        if item["id"] == chart_id:
            return item
    return None


def get_suggestions(current_id: str, exclude_ids=None, limit: int = 2):
    """Chọn tối đa `limit` câu hỏi gợi ý tiếp theo cho người dùng, THUẦN CODE (không
    gọi AI, không tốn token) — dùng sau khi trả lời 1 câu hỏi đã route vào
    `current_id`. Ưu tiên các mục khai báo trong 'lien_quan' của mục hiện tại,
    sau đó đến các mục cùng 'trang', cuối cùng mới lấy bất kỳ mục nào khác.
    Luôn loại bỏ current_id và các id trong exclude_ids (đã hỏi trong hội thoại này).
    Trả về list [{"id":..., "cau_hoi":...}, ...]."""
    exclude = set(exclude_ids or [])
    exclude.add(current_id)

    current = get_catalog_item(current_id)
    picked = []
    picked_ids = set()

    def try_add(item):
        if item["id"] not in exclude and item["id"] not in picked_ids:
            picked.append({"id": item["id"], "cau_hoi": item["cau_hoi"]})
            picked_ids.add(item["id"])

    if current:
        for rid in current.get("lien_quan", []):
            if len(picked) >= limit:
                break
            related = get_catalog_item(rid)
            if related:
                try_add(related)

        if len(picked) < limit:
            for item in CHART_CATALOG:
                if len(picked) >= limit:
                    break
                if item.get("trang") == current.get("trang"):
                    try_add(item)

    if len(picked) < limit:
        for item in CHART_CATALOG:
            if len(picked) >= limit:
                break
            try_add(item)

    return picked[:limit]
