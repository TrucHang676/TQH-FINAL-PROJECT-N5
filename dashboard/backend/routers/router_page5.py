import os
import json
import uuid
import datetime
import traceback
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import google.generativeai as genai

# ai_config.py tự nạp dashboard/backend/.env khi import (GEMINI_API_KEY(S),...),
# file .env nằm trong .gitignore nên không bị commit lên git.
import base64
from backend.ai_config import (
    GEMINI_MODEL_NAME, TITLE_MODEL_NAME, ROUTING_MODEL_NAME,
    SYSTEM_PROMPT, VISION_PROMPT, ROUTING_PROMPT_TEMPLATE, COMMENT_PROMPT_TEMPLATE,
    ASK_FORCED_PROMPT, CODE_FORCED_SUFFIX, EXPLAIN_FORCED_PROMPT,
    GEMINI_API_KEYS,
)
from backend.chart_catalog import CHART_CATALOG, get_catalog_prompt_listing, get_catalog_item, get_suggestions

router = APIRouter()

# Lấy thư mục gốc (Final/)
root_dir = Path(__file__).parent.parent.parent.parent.resolve()
data_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"
history_file = root_dir / "dashboard" / "backend" / "ai_history.json"

gemini_api_key = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""


def generate_with_key_fallback(prompt: str, model_name: str = None):
    """Gọi Gemini bằng key đầu tiên; nếu key đó hết quota (429) thì tự chuyển
    sang key kế tiếp trong GEMINI_API_KEYS. Trả về response của lần gọi thành công.
    model_name: để None thì dùng GEMINI_MODEL_NAME (model chính)."""
    last_error = None
    chosen_model = model_name or GEMINI_MODEL_NAME
    for key in GEMINI_API_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(chosen_model)
            return model.generate_content(prompt)
        except Exception as e:
            last_error = e
            is_quota_error = "429" in str(e) or "quota" in str(e).lower() or "ResourceExhausted" in str(e)
            if is_quota_error:
                continue  # thử key tiếp theo
            raise  # lỗi khác (VD: model không tồn tại, prompt bị chặn) thì báo ngay
    raise last_error if last_error else RuntimeError("Không có GEMINI_API_KEYS nào được cấu hình.")

def stream_text_from_prompt(prompt_or_content, model_name: str = None):
    """Generator sinh dần từng đoạn văn bản từ Gemini theo thời gian thực (dùng
    stream=True có sẵn trong SDK google-generativeai), có cùng cơ chế fallback
    nhiều key khi hết quota như generate_with_key_fallback. Dùng được cho cả luồng
    có thể ra CODE (Mẫu 6): gọi hàm này để stream thô cho người dùng xem dẫn nhập +
    code đổ dần theo thời gian thực, nhưng việc TÁCH code khỏi văn bản chỉ được làm
    SAU KHI vòng lặp for kết thúc (tức đã nhận đủ toàn văn) — không bao giờ tách
    giữa chừng trên một chunk riêng lẻ, nên vẫn an toàn như cách tách cũ."""
    last_error = None
    chosen_model = model_name or GEMINI_MODEL_NAME
    for key in GEMINI_API_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(chosen_model)
            response = model.generate_content(prompt_or_content, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            last_error = e
            is_quota_error = "429" in str(e) or "quota" in str(e).lower() or "ResourceExhausted" in str(e)
            if is_quota_error:
                continue
            raise
    raise last_error if last_error else RuntimeError("Không có GEMINI_API_KEYS nào được cấu hình.")

def sse_event(data: dict) -> str:
    """Định dạng 1 sự kiện Server-Sent Events (SSE): mỗi sự kiện là 1 dòng JSON,
    kết thúc bằng 2 dấu xuống dòng theo đúng chuẩn SSE."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def generate_title(prompt: str):
    """Tự đặt tiêu đề ngắn (vài từ) cho cuộc hội thoại dựa trên câu hỏi đầu tiên.
    Dùng model Flash cho nhanh/rẻ. Lỗi thì trả None (không làm hỏng luồng chính)."""
    if not gemini_api_key:
        return None
    try:
        tp = (
            "Đặt một tiêu đề RẤT NGẮN (tối đa 6 từ, tiếng Việt có dấu, KHÔNG dùng dấu "
            "ngoặc kép, KHÔNG có dấu chấm cuối) tóm tắt chủ đề của câu hỏi sau. "
            "Chỉ trả về đúng dòng tiêu đề, không thêm gì khác:\n" + prompt
        )
        resp = generate_with_key_fallback(tp, model_name=TITLE_MODEL_NAME)
        title = (resp.text or "").strip().strip('"').strip()
        title = title.splitlines()[0].strip() if title else ""
        return title[:80] or None
    except Exception:
        return None

def route_question_to_catalog(question: str):
    """Đối chiếu câu hỏi với danh mục biểu đồ có sẵn (chart_catalog.py). Trả về mã
    (VD 'P2-02') nếu khớp Ý NGHĨA với 1 biểu đồ đã có, hoặc None nếu không khớp/lỗi
    (khi đó gọi nơi khác sẽ tự quay về luồng sinh code như bình thường)."""
    if not gemini_api_key:
        return None
    try:
        prompt = ROUTING_PROMPT_TEMPLATE.format(
            catalog_listing=get_catalog_prompt_listing(),
            question=question,
        )
        resp = generate_with_key_fallback(prompt, model_name=ROUTING_MODEL_NAME)
        raw = (resp.text or "").strip()
        first_line = raw.splitlines()[0].strip().strip('"').strip("'") if raw else ""
        if not first_line or first_line.upper() == "NONE":
            return None
        item = get_catalog_item(first_line)
        return item["id"] if item else None
    except Exception:
        return None

def get_catalog_chart_data(catalog_id: str):
    """Gọi đúng hàm vẽ biểu đồ thật (build_fn) trên TOÀN BỘ dữ liệu (không lọc),
    rồi rút bảng số liệu long-format từ figure đó. Trả về dict {item, fig, fig_json, csv}
    hoặc None nếu mã không tồn tại/không rút được số liệu. fig_json là dict đã
    json.loads(fig.to_json()) — sẵn sàng gửi qua SSE hoặc lưu vào history, tránh
    phải serialize lại figure Plotly nhiều lần."""
    item = get_catalog_item(catalog_id)
    if not item:
        return None
    if not data_path.exists():
        return None
    df = pd.read_csv(data_path)
    fig = item["build_fn"](df)
    csv_text = extract_csv_from_figure(fig)
    if not csv_text:
        return None
    fig_json = json.loads(fig.to_json())
    return {"item": item, "fig": fig, "fig_json": fig_json, "csv": csv_text}

def generate_catalog_comment(question: str, csv_text: str):
    """Viết nhận xét trả lời câu hỏi dựa trên bảng số liệu thật (đã rút từ 1 biểu đồ
    có sẵn). Dùng model chính (Pro) vì đây là nội dung phân tích chất lượng cao,
    không phải tác vụ phân loại đơn giản như routing/title. Trả None nếu lỗi."""
    if not gemini_api_key:
        return None
    try:
        prompt = COMMENT_PROMPT_TEMPLATE.format(question=question, csv_data=csv_text)
        resp = generate_with_key_fallback(prompt)
        return (resp.text or "").strip() or None
    except Exception:
        return None

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
    # ID của cuộc hội thoại — nhiều câu hỏi cùng 1 phiên chat sẽ chia sẻ cùng
    # conversationId để gom nhóm trong lịch sử. Frontend sinh sẵn; nếu rỗng thì
    # backend tự lấy chính requestId làm conversationId (cuộc hội thoại 1 câu).
    conversationId: str | None = None
    # Ảnh người dùng tải lên (data URL base64, VD "data:image/png;base64,....") để
    # AI phân tích biểu đồ/số liệu trong ảnh. Rỗng nếu chỉ hỏi bằng chữ.
    image: str | None = None


def parse_data_url_image(image_str: str):
    """Tách data URL base64 thành (mime_type, bytes). Hỗ trợ cả chuỗi base64 thuần."""
    if image_str.startswith("data:"):
        header, b64 = image_str.split(",", 1)
        mime = header.split(";")[0].replace("data:", "").strip() or "image/png"
    else:
        b64, mime = image_str, "image/png"
    return mime, base64.b64decode(b64)

class AiExecuteParams(BaseModel):
    requestId: str
    editedCode: str

def get_system_prompt():
    return SYSTEM_PROMPT

# Số lượt hội thoại gần nhất tối đa đưa vào ngữ cảnh (giới hạn để prompt không quá dài).
MAX_CONTEXT_TURNS = 8

def build_conversation_context(history, conversation_id, max_turns=MAX_CONTEXT_TURNS):
    """Dựng lại các lượt hỏi–đáp TRƯỚC ĐÓ của cùng một cuộc hội thoại thành đoạn
    văn bản ngữ cảnh, để model hiểu câu hỏi tiếp theo (VD "còn vùng miền thì sao?",
    "đổi thành top 10"). Trả về chuỗi rỗng nếu là câu hỏi đầu tiên của cuộc."""
    if not conversation_id:
        return ""
    turns = [x for x in history if (x.get("conversationId") or x.get("id")) == conversation_id]
    if not turns:
        return ""
    turns.sort(key=lambda x: x.get("timestamp", ""))
    turns = turns[-max_turns:]

    lines = [
        "\n\n--- LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ (chỉ để hiểu ngữ cảnh câu hỏi mới bên dưới; "
        "nếu câu mới có ý nối tiếp như \"còn ...\", \"tương tự\", \"đổi thành ...\", "
        "\"vẫn biểu đồ đó nhưng ...\" thì hãy dựa vào các lượt này) ---"
    ]
    for t in turns:
        lines.append(f"\n[Người dùng]: {t.get('prompt', '')}")
        if t.get("type") == "text" and t.get("answer"):
            lines.append(f"[Trợ lý — đã trả lời bằng văn bản]: {t['answer']}")
        elif t.get("code"):
            lines.append("[Trợ lý — đã sinh code phân tích]:\n```python\n" + t["code"] + "\n```")
    lines.append("\n--- HẾT LỊCH SỬ ---")
    return "\n".join(lines)

@router.post("/api/ai/request")
def ai_request(req: AiRequestParams):
    # Nạp lịch sử 1 lần: vừa để dựng ngữ cảnh hội thoại, vừa để ghi item mới ở cuối.
    history = load_history()
    context = build_conversation_context(history, req.conversationId)

    # Mã biểu đồ trong danh mục (chart_catalog.py) nếu câu trả lời dùng số liệu từ
    # biểu đồ có sẵn — chỉ lưu nội bộ vào lịch sử để debug, KHÔNG hiển thị cho người
    # dùng (đã chốt: câu trả lời chỉ là văn bản tự nhiên, không cần nêu nguồn).
    catalog_id = None

    if not gemini_api_key:
        # Nếu chưa có API KEY, trả về dummy code cho mục đích demo/phát triển
        resp_type = "code"
        code = f"""# Phân tích theo yêu cầu: {req.prompt}
# Bước 1: Nhóm dữ liệu theo cấp độ kinh nghiệm
exp_counts = dff['cap_do_kinh_nghiem'].value_counts().reset_index()
exp_counts.columns = ['Cấp độ', 'Số lượng']

# Bước 2: Vẽ biểu đồ cột bằng Plotly Express
import plotly.express as px
fig = px.bar(exp_counts, x='Cấp độ', y='Số lượng', title='Số lượng tin theo cấp độ kinh nghiệm', color='Cấp độ')
"""
        answer = None
    elif req.image:
        # CÓ ẢNH => luồng phân tích hình ảnh (vision): AI đọc số liệu/biểu đồ trong
        # ảnh do người dùng cung cấp và trả về nhận xét dạng văn bản. Không sinh code.
        try:
            mime, img_bytes = parse_data_url_image(req.image)
            user_ask = req.prompt.strip() if req.prompt and req.prompt.strip() else "Hãy phân tích hình ảnh này."
            vision_content = [
                VISION_PROMPT + context + f"\n\nYÊU CẦU CỦA NGƯỜI DÙNG:\n{user_ask}",
                {"mime_type": mime, "data": img_bytes},
            ]
            response = generate_with_key_fallback(vision_content)
            resp_type = "text"
            code = None
            answer = (response.text or "").strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Bước 1: thử đối chiếu câu hỏi với danh mục biểu đồ đã có sẵn trên dashboard
        # (chart_catalog.py). Nếu khớp, dùng NGAY số liệu thật từ biểu đồ đó để viết
        # nhận xét — không sinh code mới, đảm bảo số liệu luôn khớp dashboard.
        # Nếu không khớp (catalog_id=None) hoặc có lỗi ở bước này, rơi về luồng sinh
        # code/tư vấn (Chế độ A/B) như bình thường — không làm hỏng trải nghiệm.
        catalog_id = None
        try:
            catalog_id = route_question_to_catalog(req.prompt)
        except Exception:
            catalog_id = None

        catalog_answer = None
        if catalog_id:
            try:
                chart_data = get_catalog_chart_data(catalog_id)
                if chart_data:
                    catalog_answer = generate_catalog_comment(req.prompt, chart_data["csv"])
            except Exception:
                catalog_answer = None

        if catalog_answer:
            resp_type = "text"
            code = None
            answer = catalog_answer
        else:
            catalog_id = None  # không dùng được kết quả catalog -> không ghi nhận nguồn
            try:
                full_prompt = (
                    get_system_prompt()
                    + context
                    + f"\n\nYÊU CẦU MỚI CỦA NGƯỜI DÙNG:\n{req.prompt}"
                )
                response = generate_with_key_fallback(full_prompt)
                text = response.text
                # Có ```python``` (Chế độ B) => tách code. Không có (Chế độ A) => coi cả
                # câu trả lời là văn bản tư vấn/ý tưởng, không thực thi được.
                if "```python" in text:
                    resp_type = "code"
                    code = text.split("```python")[1].split("```")[0].strip()
                    answer = None
                elif "```" in text:
                    resp_type = "code"
                    code = text.split("```")[1].split("```")[0].strip()
                    answer = None
                else:
                    resp_type = "text"
                    code = None
                    answer = text.strip()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    # Tạo history item
    req_id = str(uuid.uuid4())
    conversation_id = req.conversationId or req_id
    # context rỗng => đây là câu hỏi ĐẦU TIÊN của cuộc => tự đặt tiêu đề ngắn cho cuộc.
    if context == "":
        title = generate_title(req.prompt) if (req.prompt and req.prompt.strip()) else "Phân tích hình ảnh"
    else:
        title = None
    item = {
        "id": req_id,
        "conversationId": conversation_id,
        "title": title,
        "prompt": req.prompt,
        "image": req.image,  # lưu data URL để hiện lại ảnh khi mở từ lịch sử
        "catalogId": catalog_id,  # nội bộ/debug: mã biểu đồ đã dùng để nhận xét (nếu có)
        "type": resp_type,
        "code": code,
        "answer": answer,
        "status": "pending_approval" if resp_type == "code" else "answered",
        "timestamp": datetime.datetime.now().isoformat(),
        "result": None,
        "logs": None
    }

    # history đã được nạp ở đầu hàm để dựng ngữ cảnh — tái sử dụng, không đọc lại.
    history.insert(0, item)
    save_history(history)

    if resp_type == "text":
        return {
            "requestId": req_id,
            "conversationId": conversation_id,
            "type": "text",
            "answer": answer
        }

    return {
        "requestId": req_id,
        "conversationId": conversation_id,
        "type": "code",
        "code": code,
        "explanation": "Giải thích đã được nhúng trực tiếp bằng comment trong code theo quy định."
    }

class AiStreamParams(BaseModel):
    prompt: str
    conversationId: str | None = None
    image: str | None = None
    # Chế độ tường minh do người dùng chọn qua lệnh gõ (/hoi, /code, /giaithich,
    # /nhanxet) — bỏ qua bước AI tự đoán, đảm bảo đúng hành vi lệnh yêu cầu.
    # None/"auto" = để hệ thống tự quyết định như trước (định tuyến danh mục rồi
    # mới quyết Chế độ A/B).
    mode: str | None = None

def find_last_chart_result(history, conversation_id):
    """Tìm item GẦN NHẤT trong 1 cuộc hội thoại có kết quả biểu đồ đã chạy thành
    công (result.csv tồn tại) — dùng cho lệnh /nhanxet và tự động nhận xét ngay
    sau khi thực thi code. Trả về None nếu cuộc hội thoại chưa có biểu đồ nào."""
    turns = [x for x in history if (x.get("conversationId") or x.get("id")) == conversation_id]
    turns.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    for t in turns:
        csv_text = (t.get("result") or {}).get("csv")
        if csv_text:
            return t
    return None

@router.post("/api/ai/request/stream")
def ai_request_stream(req: AiStreamParams):
    """Biến thể streaming của /api/ai/request: trả lời theo thời gian thực (SSE).

    MỌI nhánh (kể cả nhánh có thể ra CODE — /code hoặc auto rơi vào Chế độ B) đều
    stream từng chữ ngay từ "start" với type="text": Chế độ B giờ luôn viết dẫn
    nhập + '**Hướng phân tích**' TRƯỚC code (Mẫu 6), nên phần đầu luôn là văn bản
    thuần — frontend hiển thị dần như bong bóng văn bản bình thường, và tự nhận ra
    lúc nào gặp dấu ``` để chuyển sang xem trước khung code. Việc TÁCH code khỏi
    văn bản chỉ làm SAU KHI đã nhận đủ toàn văn (sau vòng for), nên vẫn an toàn.
    Ở "done", type mới phản ánh kết quả THẬT (text hoặc code) để frontend quyết
    định giữ nguyên bong bóng văn bản hay chuyển thành bong bóng code chờ duyệt.

    Mỗi sự kiện SSE là 1 dòng JSON:
    - {"phase": "start", "type": "text", "catalogId"?, "figure"?} — luôn stream văn bản trước
    - {"phase": "delta", "text": "..."}           — 1 đoạn văn bản/code thô mới
    - {"phase": "done", "requestId":..., "conversationId":..., "type": "text"|"code",
       "code"?, "preamble"?, "catalogId"?, "suggestions"?}
    - {"phase": "error", "message": "..."}
    """
    def event_generator():
        history = load_history()
        context = build_conversation_context(history, req.conversationId)
        req_id = str(uuid.uuid4())
        conversation_id = req.conversationId or req_id
        catalog_id = None
        chart_data = None
        resp_type = "text"
        code = None
        preamble = ""
        may_be_code = False  # True khi nhánh này CÓ THỂ kết thúc bằng code (Mẫu 6)
        full_text = ""

        try:
            if not gemini_api_key:
                dummy = "Chưa cấu hình GEMINI_API_KEY nên chưa thể trả lời thật. Vui lòng cấu hình khóa API trong dashboard/backend/.env."
                yield sse_event({"phase": "start", "type": "text"})
                yield sse_event({"phase": "delta", "text": dummy})
                full_text = dummy

            elif req.image:
                yield sse_event({"phase": "start", "type": "text"})
                mime, img_bytes = parse_data_url_image(req.image)
                user_ask = req.prompt.strip() if req.prompt and req.prompt.strip() else "Hãy phân tích hình ảnh này."
                vision_content = [
                    VISION_PROMPT + context + f"\n\nYÊU CẦU CỦA NGƯỜI DÙNG:\n{user_ask}",
                    {"mime_type": mime, "data": img_bytes},
                ]
                for chunk in stream_text_from_prompt(vision_content):
                    full_text += chunk
                    yield sse_event({"phase": "delta", "text": chunk})

            elif req.mode == "explain":
                yield sse_event({"phase": "start", "type": "text"})
                ask = req.prompt.strip() if req.prompt and req.prompt.strip() else "Giải thích chi tiết đoạn code/kết quả gần nhất trong cuộc hội thoại này."
                prompt = EXPLAIN_FORCED_PROMPT + context + f"\n\nYÊU CẦU: {ask}"
                for chunk in stream_text_from_prompt(prompt):
                    full_text += chunk
                    yield sse_event({"phase": "delta", "text": chunk})

            elif req.mode == "comment":
                last_item = find_last_chart_result(history, conversation_id)
                yield sse_event({"phase": "start", "type": "text"})
                if not last_item:
                    msg = "Chưa có biểu đồ nào được chạy trong cuộc hội thoại này để nhận xét — hãy hỏi một câu phân tích hoặc duyệt & chạy code trước."
                    yield sse_event({"phase": "delta", "text": msg})
                    full_text = msg
                else:
                    csv_text = last_item["result"]["csv"]
                    question_for_comment = req.prompt.strip() if req.prompt and req.prompt.strip() else last_item.get("prompt", "Nhận xét biểu đồ này")
                    prompt = COMMENT_PROMPT_TEMPLATE.format(question=question_for_comment, csv_data=csv_text)
                    for chunk in stream_text_from_prompt(prompt):
                        full_text += chunk
                        yield sse_event({"phase": "delta", "text": chunk})

            elif req.mode == "code":
                # Mẫu 6 pha 1: stream dẫn nhập + '**Hướng phân tích**' + code đổ dần
                # trong CÙNG 1 bong bóng — không còn chờ nhận trọn khối mới hiển thị.
                may_be_code = True
                yield sse_event({"phase": "start", "type": "text"})
                full_prompt = (
                    get_system_prompt() + CODE_FORCED_SUFFIX + context
                    + f"\n\nYÊU CẦU MỚI CỦA NGƯỜI DÙNG:\n{req.prompt}"
                )
                for chunk in stream_text_from_prompt(full_prompt):
                    full_text += chunk
                    yield sse_event({"phase": "delta", "text": chunk})

            elif req.mode == "ask":
                yield sse_event({"phase": "start", "type": "text"})
                prompt = ASK_FORCED_PROMPT + context + f"\n\nCÂU HỎI: {req.prompt}"
                for chunk in stream_text_from_prompt(prompt):
                    full_text += chunk
                    yield sse_event({"phase": "delta", "text": chunk})

            else:
                # AUTO (mặc định): thử định tuyến danh mục biểu đồ trước — xem
                # /api/ai/request để biết lý do thiết kế 2 bước này.
                try:
                    catalog_id = route_question_to_catalog(req.prompt)
                except Exception:
                    catalog_id = None

                chart_data = None
                if catalog_id:
                    try:
                        chart_data = get_catalog_chart_data(catalog_id)
                    except Exception:
                        chart_data = None
                    if not chart_data:
                        catalog_id = None

                if catalog_id and chart_data:
                    # Mẫu 5: gửi kèm figure THẬT ngay từ đầu (đã dựng sẵn để rút CSV,
                    # không tốn thêm chi phí) — frontend giữ trong state, chờ AI viết
                    # tới marker [[BIEU_DO]] trong văn bản là chèn biểu đồ vào đúng chỗ.
                    yield sse_event({
                        "phase": "start", "type": "text",
                        "catalogId": catalog_id, "figure": chart_data["fig_json"],
                    })
                    prompt = COMMENT_PROMPT_TEMPLATE.format(question=req.prompt, csv_data=chart_data["csv"])
                    for chunk in stream_text_from_prompt(prompt):
                        full_text += chunk
                        yield sse_event({"phase": "delta", "text": chunk})
                else:
                    # Không khớp danh mục -> Chế độ A/B: Chế độ B giờ luôn mở đầu
                    # bằng văn bản (dẫn nhập + Hướng phân tích) trước khi vào code
                    # (Mẫu 6), nên có thể stream ngay mà không cần biết trước kết quả
                    # cuối cùng là text hay code — quyết định sau khi nhận đủ toàn văn.
                    may_be_code = True
                    yield sse_event({"phase": "start", "type": "text"})
                    full_prompt = (
                        get_system_prompt() + context
                        + f"\n\nYÊU CẦU MỚI CỦA NGƯỜI DÙNG:\n{req.prompt}"
                    )
                    for chunk in stream_text_from_prompt(full_prompt):
                        full_text += chunk
                        yield sse_event({"phase": "delta", "text": chunk})
        except Exception as e:
            yield sse_event({"phase": "error", "message": str(e)})
            return

        # Tách preamble/code khỏi toàn văn NẾU nhánh này có thể ra code (Mẫu 6) và
        # AI thực sự có sinh code (xuất hiện dấu ```) — chỉ làm SAU KHI đã nhận đủ.
        if may_be_code:
            if "```python" in full_text:
                preamble = full_text.split("```python")[0].strip()
                code = full_text.split("```python")[1].split("```")[0].strip()
                resp_type = "code"
            elif "```" in full_text:
                preamble = full_text.split("```")[0].strip()
                code = full_text.split("```")[1].split("```")[0].strip()
                resp_type = "code"
            else:
                resp_type = "text"

        # Chuẩn hóa resp_type/answer theo mode tường minh (các mode text luôn ra text)
        if req.mode in ("ask", "explain", "comment") or req.image or not gemini_api_key:
            resp_type = "text"
        answer = full_text if resp_type == "text" else None

        if context == "":
            title = generate_title(req.prompt) if (req.prompt and req.prompt.strip()) else "Phân tích hình ảnh"
        else:
            title = None

        # Gợi ý câu hỏi tiếp theo (Mẫu 5/6) — thuần code (0 token AI). Áp dụng khi:
        # Áp dụng cho MỌI câu trả lời bằng văn bản mang tính "phân tích/tư vấn"
        # (route trúng catalog, /nhanxet, /hoi, hay Chế độ A tự nhiên ở chế độ auto)
        # — trừ /giaithich (đang giải thích lại code cũ, không phải gợi ý hướng mới),
        # ảnh (vision, khác chủ đề) và trường hợp chưa có API key. Khi không có
        # catalog_id neo (VD Chế độ A), get_suggestions(None, ...) tự lấy các mục
        # danh mục chưa hỏi làm gợi ý chung. Loại các mã đã hỏi trong CHÍNH cuộc
        # hội thoại này để không gợi ý lặp lại.
        suggestions = []
        if resp_type == "text" and req.mode != "explain" and not req.image and gemini_api_key:
            asked_ids = [
                x.get("catalogId") for x in history
                if (x.get("conversationId") or x.get("id")) == conversation_id and x.get("catalogId")
            ]
            suggestions = get_suggestions(catalog_id, exclude_ids=asked_ids)

        item = {
            "id": req_id,
            "conversationId": conversation_id,
            "title": title,
            "prompt": req.prompt,
            "image": req.image,
            "catalogId": catalog_id,
            "figure": chart_data["fig_json"] if catalog_id and chart_data else None,
            "suggestions": suggestions,
            "type": resp_type,
            "code": code,
            # Đoạn dẫn nhập + "Hướng phân tích" AI viết TRƯỚC code (Mẫu 6) — hiển
            # thị lại phía trên khung code khi xem/mở lại lịch sử.
            "preamble": preamble if resp_type == "code" else None,
            "answer": answer,
            "status": "pending_approval" if resp_type == "code" else "answered",
            "timestamp": datetime.datetime.now().isoformat(),
            "result": None,
            "logs": None,
        }
        history.insert(0, item)
        save_history(history)

        yield sse_event({
            "phase": "done",
            "requestId": req_id,
            "conversationId": conversation_id,
            "type": resp_type,
            "code": code,
            "preamble": preamble if resp_type == "code" else None,
            "catalogId": catalog_id,
            "suggestions": suggestions,
        })

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def extract_csv_from_figure(fig):
    """Dựng bảng CSV long-format từ các trace của figure Plotly. Chạy ở phía Python
    khi x/y/labels/values/z còn là mảng số thật (chưa bị mã hóa base64 khi to_json),
    nên đáng tin cậy hơn giải mã ở client. Trả về chuỗi CSV hoặc '' nếu không rút được.

    Xử lý riêng theo loại trace vì mỗi loại lưu dữ liệu ở chỗ khác nhau:
    - pie/treemap: 'labels' + 'values'
    - box: chỉ có mảng điểm thô ở 'y' (hoặc 'x' nếu nằm ngang) — rút thành THỐNG KÊ
      TÓM TẮT (count/min/q1/median/q3/max) thay vì hàng trăm điểm rời rạc gây nhiễu.
    - heatmap: ma trận 2D 'z' theo hàng 'y' và cột 'x' — làm phẳng thành từng ô.
    - choropleth/choroplethmap: 'locations' (mã định danh) + 'z' (giá trị); ưu tiên
      'hovertext' (tên tiếng Việt hiển thị) nếu có thay vì mã 'locations' thô.
    - còn lại (bar/scatter/histogram...): dùng 'x' + 'y' như cũ.

    Các trace 'scatter' chỉ mang tính trang trí (điểm jitter của box plot, trace ẩn
    để vẽ colorbar cho treemap, đường tham chiếu trung vị) bị bỏ qua khi trong cùng
    figure đã có trace 'box' hoặc 'treemap' — tránh trùng lặp/nhiễu dữ liệu.
    """
    import csv as _csv
    import io
    import numpy as np

    def clean_label(v):
        # Một số nhãn trên dashboard chèn '\n' để xuống dòng cho đẹp (VD "Software\nDev")
        # — phải thay bằng khoảng trắng, nếu không sẽ làm vỡ định dạng dòng CSV.
        return v.replace("\n", " ") if isinstance(v, str) else v

    trace_types = [getattr(tr, "type", "") for tr in fig.data]
    has_box = "box" in trace_types
    has_treemap = "treemap" in trace_types

    rows = []
    for tr in fig.data:
        ttype = getattr(tr, "type", "")
        name = getattr(tr, "name", None) or ttype or ""
        labels = getattr(tr, "labels", None)
        values = getattr(tr, "values", None)
        x = getattr(tr, "x", None)
        y = getattr(tr, "y", None)
        z = getattr(tr, "z", None)

        if labels is not None and values is not None:
            for lb, v in zip(list(labels), list(values)):
                rows.append([name, clean_label(lb), v])

        elif ttype == "box":
            raw = y if y is not None else x
            if raw is None:
                continue
            arr = pd.Series(list(raw), dtype="float64").dropna()
            if arr.empty:
                continue
            stats = {
                "so_luong": int(arr.count()),
                "nho_nhat": round(float(arr.min()), 2),
                "tu_phan_vi_1_Q1": round(float(arr.quantile(0.25)), 2),
                "trung_vi": round(float(arr.median()), 2),
                "tu_phan_vi_3_Q3": round(float(arr.quantile(0.75)), 2),
                "lon_nhat": round(float(arr.max()), 2),
                "trung_binh": round(float(arr.mean()), 2),
            }
            for stat_name, stat_val in stats.items():
                rows.append([name, stat_name, stat_val])

        elif ttype == "heatmap" and z is not None:
            z_arr = np.array(z, dtype="float64")
            x_labels = list(x) if x is not None else list(range(z_arr.shape[1]))
            y_labels = list(y) if y is not None else list(range(z_arr.shape[0]))
            for i, row_label in enumerate(y_labels):
                for j, col_label in enumerate(x_labels):
                    val = z_arr[i][j]
                    if not np.isnan(val):
                        combined = f"{clean_label(row_label)} × {clean_label(col_label)}"
                        rows.append([name, combined, round(float(val), 2)])

        elif ttype in ("choropleth", "choroplethmap", "choroplethmapbox") and z is not None:
            locations = getattr(tr, "locations", None)
            hovertext = getattr(tr, "hovertext", None)
            display_labels = list(hovertext) if hovertext is not None else list(locations or [])
            for lb, v in zip(display_labels, list(z)):
                rows.append([name, clean_label(lb), v])

        elif ttype == "scatter" and (has_box or has_treemap):
            continue  # trace trang trí (jitter/colorbar/đường tham chiếu), không phải dữ liệu chính

        elif x is not None and y is not None:
            for xv, yv in zip(list(x), list(y)):
                rows.append([name, clean_label(xv), yv])

    if not rows:
        return ""
    buf = io.StringIO()
    writer = _csv.writer(buf)
    writer.writerow(["trace", "nhan_x", "gia_tri_y"])
    writer.writerows(rows)
    return buf.getvalue()

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
        # Thực thi code do người dùng đã duyệt.
        # Lưu ý: phải truyền CÙNG 1 dict cho cả globals và locals. Nếu tách 2 dict
        # riêng (VD: exec(code, {}, local_env)), Python coi code như thân class —
        # mọi lambda/hàm def bên trong code sẽ không thấy được các biến/import ở
        # ngoài (lỗi "name 'x' is not defined"), dù biến đó có trong local_env.
        exec(req.editedCode, local_env)
        
        # Lấy kết quả từ biến fig hoặc html_result
        if "fig" in local_env:
            import json as json_lib
            fig = local_env["fig"]
            result_data = {"type": "plotly", "data": json_lib.loads(fig.to_json())}
            # Trích bảng dữ liệu long-format từ figure (khi mảng còn là số thật ở
            # phía Python) để người dùng tải CSV — chính xác hơn giải mã base64 ở client.
            result_data["csv"] = extract_csv_from_figure(fig)
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

@router.delete("/api/ai/history/{conversation_id}")
def delete_conversation(conversation_id: str):
    """Xóa toàn bộ các câu hỏi thuộc một cuộc hội thoại khỏi lịch sử.
    Với item cũ chưa có conversationId thì coi id chính là conversationId."""
    history = load_history()
    remaining = [x for x in history if (x.get("conversationId") or x["id"]) != conversation_id]
    deleted = len(history) - len(remaining)
    save_history(remaining)
    return {"deleted": deleted}

@router.post("/api/ai/history/{conversation_id}/pin")
def toggle_pin(conversation_id: str):
    """Bật/tắt ghim cho một cuộc hội thoại (đánh dấu 'pinned' lên mọi item của cuộc)."""
    history = load_history()
    items = [x for x in history if (x.get("conversationId") or x["id"]) == conversation_id]
    if not items:
        raise HTTPException(status_code=404, detail="Conversation not found")
    new_state = not bool(items[0].get("pinned"))
    for x in items:
        x["pinned"] = new_state
    save_history(history)
    return {"conversationId": conversation_id, "pinned": new_state}
