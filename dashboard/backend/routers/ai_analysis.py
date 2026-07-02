import os
import json
import uuid
import datetime
import traceback
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import google.generativeai as genai

router = APIRouter()

# Lấy thư mục gốc (Final/)
root_dir = Path(__file__).parent.parent.parent.parent.resolve()
data_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"
history_file = root_dir / "dashboard" / "backend" / "ai_history.json"

# Cấu hình Gemini API (Sử dụng dummy key hoặc biến môi trường)
# Trong môi trường thực tế, set GEMINI_API_KEY trong .env
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Lịch sử dạng local JSON file
def load_history():
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

class AiRequestParams(BaseModel):
    prompt: str

class AiExecuteParams(BaseModel):
    requestId: str
    editedCode: str

def get_system_prompt():
    return """Bạn là một chuyên gia phân tích dữ liệu Data Analyst bằng Python.
Nhiệm vụ của bạn là viết code Python (sử dụng thư viện pandas và plotly.graph_objects hoặc plotly.express) để phân tích tập dữ liệu.
Người dùng có một DataFrame tên là `dff`.
Cấu trúc cột của DataFrame `dff` như sau:
- 'ten_cong_viec': Tên chức danh công việc
- 'ten_cong_ty': Tên công ty
- 'nhom_vi_tri': Nhóm vị trí (Frontend, Backend, AI, Data,...)
- 'cap_do_kinh_nghiem': Cấp độ (Intern, Fresher, Junior, Senior,...)
- 'tinh_thanh': Tỉnh/thành phố
- 'vung_mien': Vùng miền (Bắc, Trung, Nam, Từ xa, Khác)
- 'luong_tb': Lương trung bình (triệu VNĐ)
- 'hinh_thuc_lam_viec': Hình thức (Full-time, Part-time,...)
- 'ngay_dang': Ngày đăng tin
- 'thang_dang': Tháng đăng tin
- 'nguon': Nguồn dữ liệu (ITviec, TopCV,...)

YÊU CẦU BẮT BUỘC:
1. Bạn CHỈ được trả về duy nhất 1 đoạn code Python nằm trong cặp dấu ```python ... ```, KHÔNG kèm theo bất kỳ văn bản trò chuyện nào bên ngoài.
2. Code phải tự chứa lời giải thích (comments) bằng ngôn ngữ tự nhiên tiếng Việt cho mỗi bước xử lý.
3. Code KHÔNG được gọi `fig.show()`.
4. Nếu kết quả là biểu đồ Plotly, bạn phải gán nó vào biến có tên là `fig`. Ví dụ: `fig = px.bar(...)`.
5. Nếu kết quả là một bảng dữ liệu hoặc kết quả dạng text, bạn phải tạo một chuỗi văn bản (HTML) hoặc JSON string và gán vào biến có tên là `html_result`.
"""

@router.post("/api/ai/request")
def ai_request(req: AiRequestParams):
    if not gemini_api_key:
        # Nếu chưa có API KEY, trả về dummy code cho mục đích demo/phát triển
        dummy_code = f"""# Phân tích theo yêu cầu: {req.prompt}
# Bước 1: Nhóm dữ liệu theo cấp độ kinh nghiệm
exp_counts = dff['cap_do_kinh_nghiem'].value_counts().reset_index()
exp_counts.columns = ['Cấp độ', 'Số lượng']

# Bước 2: Vẽ biểu đồ cột bằng Plotly Express
import plotly.express as px
fig = px.bar(exp_counts, x='Cấp độ', y='Số lượng', title='Số lượng tin theo cấp độ kinh nghiệm', color='Cấp độ')
"""
        code = dummy_code
    else:
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            full_prompt = get_system_prompt() + f"\n\nYÊU CẦU CỦA NGƯỜI DÙNG:\n{req.prompt}"
            response = model.generate_content(full_prompt)
            # Tách lấy phần code trong ```python ... ```
            text = response.text
            if "```python" in text:
                code = text.split("```python")[1].split("```")[0].strip()
            elif "```" in text:
                code = text.split("```")[1].split("```")[0].strip()
            else:
                code = text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Tạo history item
    req_id = str(uuid.uuid4())
    item = {
        "id": req_id,
        "prompt": req.prompt,
        "code": code,
        "status": "pending_approval",
        "timestamp": datetime.datetime.now().isoformat(),
        "result": None,
        "logs": None
    }
    
    history = load_history()
    history.insert(0, item)
    save_history(history)
    
    return {
        "requestId": req_id,
        "code": code,
        "explanation": "Giải thích đã được nhúng trực tiếp bằng comment trong code theo quy định."
    }

@router.post("/api/ai/execute")
def ai_execute(req: AiExecuteParams):
    history = load_history()
    item = next((x for x in history if x["id"] == req.requestId), None)
    if not item:
        raise HTTPException(status_code=404, detail="Request ID not found")
    
    # Load dataset
    if data_path.exists():
        dff = pd.read_csv(data_path)
    else:
        dff = pd.DataFrame()
        
    # Môi trường thực thi
    local_env = {
        "dff": dff,
        "pd": pd,
    }
    
    status = "success"
    result_data = None
    logs = ""
    
    try:
        # Thực thi code do người dùng đã duyệt
        exec(req.editedCode, {}, local_env)
        
        # Lấy kết quả từ biến fig hoặc html_result
        if "fig" in local_env:
            import json as json_lib
            fig = local_env["fig"]
            result_data = {"type": "plotly", "data": json_lib.loads(fig.to_json())}
            logs = "Vẽ biểu đồ Plotly thành công."
        elif "html_result" in local_env:
            result_data = {"type": "html", "data": local_env["html_result"]}
            logs = "Phân tích dữ liệu thành công."
        else:
            result_data = {"type": "text", "data": "Code chạy thành công nhưng không tìm thấy biến 'fig' hoặc 'html_result' để hiển thị."}
            logs = "Không có output đồ thị/HTML."
    except Exception as e:
        status = "error"
        logs = traceback.format_exc()
        result_data = {"type": "error", "data": str(e)}
        
    # Update lịch sử
    item["code"] = req.editedCode # Cập nhật lại code mới nhất (sau khi user edit)
    item["status"] = "success" if status == "success" else "error"
    item["result"] = result_data
    item["logs"] = logs
    save_history(history)
    
    return {
        "status": status,
        "result": result_data,
        "logs": logs
    }

@router.get("/api/ai/history")
def get_ai_history():
    return load_history()
