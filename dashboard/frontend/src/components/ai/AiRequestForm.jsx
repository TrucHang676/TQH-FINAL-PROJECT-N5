import React, { useState } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';

const AiRequestForm = ({ onSubmit, isSubmitting }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim() && !isSubmitting) {
      onSubmit(prompt.trim());
    }
  };

  const suggestPrompts = [
    "Vẽ biểu đồ cột thể hiện mức lương trung bình theo từng cấp độ kinh nghiệm.",
    "Thống kê số lượng tin tuyển dụng theo từng nhóm vị trí (Backend, Frontend,...)",
    "Vẽ biểu đồ tròn thể hiện tỷ lệ phần trăm các hình thức làm việc (Full-time, Part-time)."
  ];

  return (
    <div className="chart-card" style={{ marginBottom: '20px' }}>
      <div className="chart-header">
        <span className="chart-title">
          <Sparkles size={16} color="#B45309" />
          Yêu cầu AI Phân Tích
        </span>
      </div>
      <div className="chart-content" style={{ padding: '20px' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ví dụ: Vẽ biểu đồ cột thể hiện mức lương trung bình theo từng cấp độ kinh nghiệm..."
            disabled={isSubmitting}
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'vertical',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', flex: 1 }}>
              {suggestPrompts.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(s)}
                  disabled={isSubmitting}
                  style={{
                    backgroundColor: 'rgba(89, 178, 146, 0.1)',
                    color: 'var(--primary-color)',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '6px 10px',
                    fontSize: '12px',
                    cursor: isSubmitting ? 'not-allowed' : 'pointer',
                    textAlign: 'left'
                  }}
                >
                  {s.length > 50 ? s.substring(0, 50) + '...' : s}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={!prompt.trim() || isSubmitting}
              style={{
                backgroundColor: !prompt.trim() || isSubmitting ? '#9CA3AF' : 'var(--primary-color)',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: !prompt.trim() || isSubmitting ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'background-color 0.2s',
                marginLeft: '15px',
                whiteSpace: 'nowrap'
              }}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={16} className="lucide-spin" style={{ animation: 'spin 2s linear infinite' }} />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Send size={16} />
                  Gửi yêu cầu
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AiRequestForm;
