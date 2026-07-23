import React, { useState, useRef, useEffect } from 'react';
import { Send, Square, ImagePlus, X, Terminal } from 'lucide-react';

const suggestPrompts = [
  "Biểu đồ cột: lương TB theo cấp độ kinh nghiệm",
  "Thống kê số lượng tin tuyển dụng theo nhóm vị trí",
  "Biểu đồ tròn: tỷ lệ hình thức làm việc"
];

// Hệ thống lệnh nâng cao (tùy chọn) — người dùng vẫn chat bình thường được, gõ lệnh
// chỉ để ép AI đi đúng hướng khi cần chắc chắn (bỏ qua bước AI tự đoán chế độ).
const COMMANDS = [
  { cmd: '/code', mode: 'code', desc: 'Bắt buộc sinh code Python minh họa, dù câu hỏi nghe như ý tưởng' },
  { cmd: '/hoi', mode: 'ask', desc: 'Bắt buộc trả lời bằng văn bản, không sinh code' },
  { cmd: '/giaithich', mode: 'explain', desc: 'Giải thích chi tiết đoạn code/kết quả gần nhất bằng lời' },
  { cmd: '/nhanxet', mode: 'comment', desc: 'Nhận xét biểu đồ vừa chạy trong cuộc hội thoại này' },
];

// Tách tiền tố lệnh (nếu có) khỏi nội dung gõ vào. Trả về {mode, text}.
export const parseCommand = (rawText) => {
  const trimmed = rawText.trimStart();
  for (const c of COMMANDS) {
    if (trimmed === c.cmd || trimmed.toLowerCase().startsWith(c.cmd + ' ')) {
      return { mode: c.mode, text: trimmed.slice(c.cmd.length).trim() };
    }
  }
  return { mode: null, text: rawText.trim() };
};

// onStop (A2a): gọi khi người dùng bấm nút Dừng lúc AI đang trả lời — nút Gửi biến
// thành nút Dừng trong suốt thời gian isSubmitting.
const AiRequestForm = ({ onSubmit, isSubmitting, onStop }) => {
  const [prompt, setPrompt] = useState('');
  const [image, setImage] = useState(null); // data URL của ảnh đã chọn
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 100) + 'px';
    }
  }, [prompt]);

  // Gợi ý lệnh: hiện khi người dùng bắt đầu gõ "/" và chưa gõ dấu cách (đang chọn lệnh)
  const trimmedStart = prompt.trimStart();
  const isTypingCommand = trimmedStart.startsWith('/') && !trimmedStart.includes(' ');
  const filteredCommands = isTypingCommand
    ? COMMANDS.filter(c => c.cmd.startsWith(trimmedStart))
    : [];
  const showCommandMenu = isTypingCommand && filteredCommands.length > 0;

  const applyCommand = (cmd) => {
    setPrompt(cmd + ' ');
    textareaRef.current?.focus();
  };

  // Đọc 1 File ảnh thành data URL base64 để gửi lên backend
  const readImageFile = (file) => {
    const reader = new FileReader();
    reader.onload = () => setImage(reader.result);
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Vui lòng chọn một tệp hình ảnh.');
      return;
    }
    readImageFile(file);
    e.target.value = ''; // cho phép chọn lại cùng file
  };

  // Dán ảnh trực tiếp từ clipboard (Ctrl+V) — nghe ở cấp window nên dán được kể cả
  // khi con trỏ không nằm trong ô nhập. Bỏ qua khi đang dán vào trình soạn thảo code.
  useEffect(() => {
    const handlePaste = (e) => {
      if (isSubmitting) return;
      const target = e.target;
      if (target && typeof target.closest === 'function' && target.closest('.ai-code-accordion')) {
        return; // đang dán vào editor Python, không can thiệp
      }
      const items = e.clipboardData?.items;
      if (!items) return;
      for (const item of items) {
        if (item.type && item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (file) {
            e.preventDefault();
            readImageFile(file);
          }
          return;
        }
      }
    };
    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, [isSubmitting]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    // Cho phép gửi nếu có chữ HOẶC có ảnh
    if ((prompt.trim() || image) && !isSubmitting) {
      const { mode, text } = parseCommand(prompt);
      onSubmit(text, image, mode);
      setPrompt('');
      setImage(null);
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
        {!showCommandMenu && (
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
        )}

        {/* Gợi ý lệnh nâng cao khi gõ "/" */}
        {showCommandMenu && (
          <div className="ai-command-menu">
            {filteredCommands.map((c) => (
              <button
                key={c.cmd}
                className="ai-command-menu-item"
                onClick={() => applyCommand(c.cmd)}
                type="button"
              >
                <Terminal size={14} />
                <span className="ai-command-menu-cmd">{c.cmd}</span>
                <span className="ai-command-menu-desc">{c.desc}</span>
              </button>
            ))}
          </div>
        )}

        {/* Xem trước ảnh đã chọn */}
        {image && (
          <div className="ai-image-preview">
            <img src={image} alt="Ảnh đã chọn" />
            <button
              className="ai-image-preview-remove"
              onClick={() => setImage(null)}
              title="Bỏ ảnh"
              type="button"
            >
              <X size={14} />
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="ai-chat-input-wrapper">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <button
            type="button"
            className="ai-chat-attach-btn"
            title="Tải ảnh biểu đồ lên (hoặc dán ảnh bằng Ctrl+V)"
            onClick={() => fileInputRef.current?.click()}
            disabled={isSubmitting}
          >
            <ImagePlus size={18} />
          </button>
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={image ? 'Mô tả yêu cầu (VD: phân tích biểu đồ này)...' : 'Nhập yêu cầu, dán ảnh (Ctrl+V), hoặc gõ "/" để xem lệnh nâng cao...'}
            disabled={isSubmitting}
            rows={1}
          />
          {isSubmitting ? (
            // A2a: đang stream — nút Gửi nhường chỗ cho nút Dừng (luôn bấm được)
            <button
              type="button"
              className="ai-chat-send-btn ai-chat-stop-btn"
              onClick={() => onStop && onStop()}
              title="Dừng tạo câu trả lời"
            >
              <Square size={16} fill="currentColor" />
            </button>
          ) : (
            <button
              type="submit"
              className="ai-chat-send-btn"
              disabled={!prompt.trim() && !image}
            >
              <Send size={18} />
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

export default AiRequestForm;
