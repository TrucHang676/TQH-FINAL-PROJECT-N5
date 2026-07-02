import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/ai';

const AiService = {
  /**
   * Gửi prompt để AI sinh code phân tích
   * @param {string} prompt Câu hỏi của người dùng
   * @returns {Promise<{requestId: string, code: string, explanation: string}>}
   */
  sendRequest: async (prompt) => {
    try {
      const response = await axios.post(`${BASE_URL}/request`, { prompt });
      return response.data;
    } catch (error) {
      console.error('Error in AiService.sendRequest:', error);
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
