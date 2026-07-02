import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

const suggestPrompts = [
  "Biểu đồ cột: lương TB theo cấp độ kinh nghiệm",
  "Thống kê số lượng tin tuyển dụng theo nhóm vị trí",
  "Biểu đồ tròn: tỷ lệ hình thức làm việc"
];

const AiRequestForm = ({ onSubmit, isSubmitting }) => {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 100) + 'px';
    }
  }, [prompt]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (prompt.trim() && !isSubmitting) {
      onSubmit(prompt.trim());
      setPrompt('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="ai-chat-input-bar">
      <div className="ai-chat-input-inner">
        <div className="ai-suggestion-chips">
          {suggestPrompts.map((s, idx) => (
            <button
              key={idx}
              className="ai-suggestion-chip"
              onClick={() => { setPrompt(s); textareaRef.current?.focus(); }}
              disabled={isSubmitting}
              type="button"
            >
              {s}
            </button>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="ai-chat-input-wrapper">
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập yêu cầu phân tích dữ liệu..."
            disabled={isSubmitting}
            rows={1}
          />
          <button
            type="submit"
            className="ai-chat-send-btn"
            disabled={!prompt.trim() || isSubmitting}
          >
            {isSubmitting ? (
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AiRequestForm;
