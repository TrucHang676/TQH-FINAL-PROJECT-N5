import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/ai';

const AiService = {
  /**
   * Gửi prompt để AI trả lời (văn bản ý tưởng, code phân tích, hoặc phân tích ảnh)
   * @param {string} prompt Câu hỏi của người dùng
   * @param {string} [conversationId] ID cuộc hội thoại để gom nhóm lịch sử
   * @param {string} [image] Ảnh dạng data URL base64 (nếu người dùng tải ảnh lên)
   * @returns {Promise<{requestId: string, conversationId: string, type: string, code?: string, answer?: string}>}
   */
  sendRequest: async (prompt, conversationId, image) => {
    try {
      const response = await axios.post(`${BASE_URL}/request`, { prompt, conversationId, image });
      return response.data;
    } catch (error) {
      console.error('Error in AiService.sendRequest:', error);
      throw error;
    }
  },

  /**
   * Gửi yêu cầu và nhận câu trả lời theo thời gian thực (streaming, SSE) qua
   * /api/ai/request/stream. Dùng fetch + ReadableStream vì axios không hỗ trợ đọc
   * dần response body trên trình duyệt.
   * @param {object} params {prompt, conversationId, image, mode, catalogHint}
   *   catalogHint (A3): mã danh mục ĐÃ BIẾT TRƯỚC khi người dùng bấm 1 chip gợi ý
   *   (chip đó vốn sinh ra từ danh mục nên chắc chắn hợp lệ) — cho phép backend bỏ
   *   hẳn 1 lượt gọi định tuyến, giảm độ trễ trước chữ đầu tiên.
   * @param {(text: string) => void} onDelta gọi mỗi khi có thêm 1 đoạn văn bản mới
   * @param {(meta: object) => void} onStart gọi ngay khi biết loại kết quả (text/code)
   * @param {(meta: object) => void} onDone gọi khi hoàn tất, kèm requestId/type/code
   * @param {(message: string) => void} onError gọi khi có lỗi
   * @param {() => void} onAbort gọi khi người dùng chủ động bấm Dừng (A2a) — tách
   *   khỏi onError để không hiện bong bóng lỗi cho một hành động cố ý
   * @param {AbortSignal} [signal] A2a: signal từ AbortController để hủy stream giữa
   *   chừng; hủy fetch cũng khiến backend (StreamingResponse) ngừng generator, nên
   *   không tốn thêm quota cho phần chưa sinh
   */
  streamRequest: async ({ prompt, conversationId, image, mode, catalogHint, signal }, { onStart, onDelta, onDone, onError, onAbort }) => {
    try {
      const response = await fetch(`${BASE_URL}/request/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, conversationId, image, mode, catalogHint }),
        signal
      });
      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // Mỗi sự kiện SSE cách nhau bởi 1 dòng trống ("\n\n")
        const parts = buffer.split('\n\n');
        buffer = parts.pop(); // phần cuối có thể chưa đầy đủ, giữ lại chờ chunk sau

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;
          let data;
          try {
            data = JSON.parse(jsonStr);
          } catch {
            continue;
          }
          if (data.phase === 'start') onStart && onStart(data);
          else if (data.phase === 'delta') onDelta && onDelta(data.text);
          else if (data.phase === 'done') onDone && onDone(data);
          else if (data.phase === 'error') onError && onError(data.message);
        }
      }
    } catch (error) {
      // A2a: người dùng bấm Dừng — không phải lỗi, không hiện bong bóng lỗi.
      if (error.name === 'AbortError') {
        onAbort && onAbort();
        return;
      }
      console.error('Error in AiService.streamRequest:', error);
      onError && onError(error.message || 'Lỗi kết nối');
    }
  },

  /**
   * Xóa toàn bộ lịch sử của một cuộc hội thoại
   * @param {string} conversationId ID cuộc hội thoại cần xóa
   * @returns {Promise<{deleted: number}>}
   */
  deleteConversation: async (conversationId) => {
    try {
      const response = await axios.delete(`${BASE_URL}/history/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error in AiService.deleteConversation:', error);
      throw error;
    }
  },

  /**
   * Yêu cầu backend thực thi đoạn code Python đã được duyệt
   * @param {string} requestId ID của request trước đó
   * @param {string} editedCode Đoạn code (có thể đã chỉnh sửa) để chạy
   * @returns {Promise<{status: string, result: any, logs: string}>}
   */
  executeCode: async (requestId, editedCode) => {
    try {
      const response = await axios.post(`${BASE_URL}/execute`, { requestId, editedCode });
      return response.data;
    } catch (error) {
      console.error('Error in AiService.executeCode:', error);
      throw error;
    }
  },

  /**
   * Bật/tắt ghim một cuộc hội thoại
   * @param {string} conversationId
   * @returns {Promise<{conversationId: string, pinned: boolean}>}
   */
  togglePin: async (conversationId) => {
    try {
      const response = await axios.post(`${BASE_URL}/history/${conversationId}/pin`);
      return response.data;
    } catch (error) {
      console.error('Error in AiService.togglePin:', error);
      throw error;
    }
  },

  /**
   * Đổi tên cuộc hội thoại
   * @param {string} conversationId
   * @param {string} title
   * @returns {Promise<{conversationId: string, title: string}>}
   */
  renameConversation: async (conversationId, title) => {
    try {
      const response = await axios.put(`${BASE_URL}/history/${conversationId}/title`, { title });
      return response.data;
    } catch (error) {
      console.error('Error in AiService.renameConversation:', error);
      throw error;
    }
  },

  /**
   * Lấy danh sách lịch sử tương tác AI
   * @returns {Promise<Array>}
   */
  getHistory: async () => {
    try {
      const response = await axios.get(`${BASE_URL}/history`);
      return response.data;
    } catch (error) {
      console.error('Error in AiService.getHistory:', error);
      throw error;
    }
  }
};

export default AiService;
