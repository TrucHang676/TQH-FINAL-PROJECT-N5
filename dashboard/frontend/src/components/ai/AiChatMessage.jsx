import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
// Dùng đúng bản dist mà react-plotly.js dùng (plotly.js/dist/plotly) — KHÔNG import
// 'plotly.js' (bản src) vì nó kéo theo module 'buffer/' làm hỏng bundle Vite/esbuild.
import Plotly from 'plotly.js/dist/plotly';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import PlotlyChart from '../PlotlyChart';
import {
  Sparkles,
  Code2,
  ChevronDown,
  Play,
  X,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Info,
  Maximize2,
  Copy,
  Check,
  Download,
  FileDown,
  Pencil,
  RefreshCw,
  Send
} from 'lucide-react';

const formatTime = (ts) => {
  if (!ts) return '';
  const d = new Date(ts);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

const getStatusBadge = (status) => {
  switch (status) {
    case 'pending_approval':
      return { statusClass: 'pending', statusIcon: <AlertTriangle size={13} />, statusText: 'Chờ duyệt' };
    case 'executing':
      return { statusClass: 'executing', statusIcon: <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />, statusText: 'Đang chạy...' };
    case 'success':
      return { statusClass: 'success', statusIcon: <CheckCircle2 size={13} />, statusText: 'Thành công' };
    case 'error':
      return { statusClass: 'error', statusIcon: <XCircle size={13} />, statusText: 'Lỗi' };
    case 'rejected':
      return { statusClass: 'rejected', statusIcon: <X size={13} />, statusText: 'Đã từ chối' };
    default:
      return { statusClass: '', statusIcon: null, statusText: '' };
  }
};

// Nút copy dùng chung: chỉ hiện icon, đổi sang dấu tích 1.5s sau khi copy.
// Chữ chú thích chỉ hiện khi hover (tooltip CSS qua data-tooltip).
const CopyButton = ({ text, className = '' }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text || '').then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };
  return (
    <button
      className={`ai-mini-btn ${className}`}
      onClick={handleCopy}
      data-tooltip={copied ? 'Đã chép' : 'Sao chép'}
      type="button"
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
};

const AiChatMessage = ({ message, onApprove, onReject, onResend, isExecuting }) => {
  // Mã nguồn MỞ mặc định để người dùng thấy ngay, có thể thu gọn lại
  const [isOpen, setIsOpen] = useState(true);
  const [editedCode, setEditedCode] = useState(message.code || '');
  const [zoomed, setZoomed] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(message.content || '');
  const graphDivRef = useRef(null);

  useEffect(() => {
    if (message.code) {
      setEditedCode(message.code);
    }
  }, [message.code]);

  const downloadPng = () => {
    if (!graphDivRef.current) return;
    Plotly.downloadImage(graphDivRef.current, {
      format: 'png',
      width: 1200,
      height: 700,
      filename: 'bieu_do_phan_tich'
    });
  };

  const downloadCsv = (csvText) => {
    const blob = new Blob(['﻿' + csvText], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'du_lieu_bieu_do.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // --- role: user ---
  if (message.role === 'user') {
    // Chế độ sửa & gửi lại câu hỏi
    if (editing) {
      return (
        <div className="ai-msg-row user">
          <div className="ai-user-edit">
            <textarea
              className="ai-user-edit-input"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              rows={2}
              autoFocus
            />
            <div className="ai-user-edit-actions">
              <button className="ai-mini-btn" onClick={() => { setEditing(false); setEditText(message.content); }} type="button">
                <X size={13} /> Hủy
              </button>
              <button
                className="ai-mini-btn ai-mini-btn-primary"
                onClick={() => { onResend && onResend(editText); setEditing(false); }}
                disabled={!editText.trim()}
                type="button"
              >
                <Send size={13} /> Gửi lại
              </button>
            </div>
          </div>
        </div>
      );
    }
    return (
      <div className="ai-msg-row user">
        <div className="ai-msg-user-wrap">
          {onResend && (
            <button
              className="ai-user-edit-btn ai-mini-btn"
              data-tooltip="Sửa & gửi lại"
              onClick={() => { setEditText(message.content); setEditing(true); }}
              type="button"
            >
              <Pencil size={13} />
            </button>
          )}
          <div className="ai-msg-user">
            {message.image && (
              <img src={message.image} alt="Ảnh đã gửi" className="ai-msg-user-image" />
            )}
            {message.content && <div>{message.content}</div>}
            <div className="ai-msg-time">{formatTime(message.timestamp)}</div>
          </div>
        </div>
      </div>
    );
  }

  // --- role: ai_code ---
  if (message.role === 'ai_code') {
    const { statusClass, statusIcon, statusText } = getStatusBadge(message.status);
    const firstLine = editedCode ? editedCode.split('\n')[0] : '';

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          <div className="ai-msg-header">
            <div className="ai-msg-avatar">
              <Sparkles size={16} color="#fff" />
            </div>
            <span className="ai-msg-label">AI Assistant</span>
            <span className={`ai-status-badge ${statusClass}`}>
              {statusIcon} {statusText}
            </span>
            <span className="ai-msg-time-ai">{formatTime(message.timestamp)}</span>
            {onResend && message.prompt && (
              <button className="ai-mini-btn ai-header-copy" onClick={() => onResend(message.prompt)} data-tooltip="Tạo lại" type="button">
                <RefreshCw size={13} />
              </button>
            )}
          </div>

          {/* Mẫu 6: dẫn nhập + "Hướng phân tích" AI viết TRƯỚC code, hiển thị lại
              phía trên khung code để câu trả lời vẫn liền mạch như 1 khối. */}
          {message.preamble && (
            <div className="ai-text-bubble ai-markdown ai-code-preamble">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.preamble}
              </ReactMarkdown>
            </div>
          )}

          {/* Code Accordion — mở mặc định, thu gọn được */}
          <div className="ai-code-accordion">
            <div className="ai-code-accordion-header">
              <div className="ai-code-accordion-title" onClick={() => setIsOpen(!isOpen)}>
                <Code2 size={15} /> Mã nguồn Python
                {!isOpen && (
                  <span className="ai-code-preview">{firstLine}</span>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CopyButton text={editedCode} />
                <ChevronDown
                  className={`ai-code-accordion-chevron ${isOpen ? 'open' : ''}`}
                  onClick={() => setIsOpen(!isOpen)}
                  style={{ cursor: 'pointer' }}
                />
              </div>
            </div>
            <div className={`ai-code-accordion-body ${isOpen ? 'open' : ''}`}>
              <Editor
                height="280px"
                language="python"
                theme="vs-dark"
                value={editedCode}
                onChange={(value) => setEditedCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: 'on',
                  readOnly:
                    message.status !== 'pending_approval' &&
                    message.status !== 'error'
                }}
              />
            </div>
            {(message.status === 'pending_approval' ||
              message.status === 'error') && (
              <div className="ai-code-actions">
                <button
                  className="ai-btn-reject"
                  onClick={() => onReject(message.requestId)}
                  disabled={isExecuting}
                >
                  <X size={15} /> Từ chối
                </button>
                <button
                  className="ai-btn-approve"
                  onClick={() => onApprove(message.requestId, editedCode)}
                  disabled={isExecuting}
                >
                  {isExecuting ? (
                    <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                  ) : (
                    <Play size={15} />
                  )}
                  Duyệt & Chạy
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // --- role: ai_text (Chế độ A: AI đề xuất ý tưởng/tư vấn bằng văn bản) ---
  if (message.role === 'ai_text') {
    // Mẫu 6 pha 1: đang stream và gặp dấu ``` — nghĩa là Chế độ B đã bắt đầu viết
    // code (dẫn nhập + "Hướng phân tích" đã stream xong ở phần trước dấu này).
    // Hiện dẫn nhập như bình thường + 1 khung xem trước code đang đổ dần; khi
    // stream xong, onDone sẽ thay hẳn bong bóng này bằng ai_code chính thức.
    const rawContent = message.content || '';
    if (rawContent.includes('```')) {
      const fenceIdx = rawContent.indexOf('```');
      const codePreamble = rawContent.slice(0, fenceIdx).trim();
      let afterOpen = rawContent.slice(fenceIdx + 3);
      if (afterOpen.startsWith('python')) afterOpen = afterOpen.slice(6);
      const closeIdx = afterOpen.indexOf('```');
      const codeSoFar = (closeIdx >= 0 ? afterOpen.slice(0, closeIdx) : afterOpen).replace(/^\n/, '');

      return (
        <div className="ai-msg-row ai">
          <div className="ai-msg-ai">
            <div className="ai-msg-header">
              <div className="ai-msg-avatar">
                <Sparkles size={16} color="#fff" />
              </div>
              <span className="ai-msg-label">AI đang soạn mã nguồn...</span>
              <span className="ai-msg-time-ai">{formatTime(message.timestamp)}</span>
            </div>
            <div className="ai-text-bubble ai-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{codePreamble}</ReactMarkdown>
              <div className="ai-code-preview-inline">
                <div className="ai-code-preview-inline-header">
                  <Code2 size={13} /> Đang soạn mã nguồn Python...
                </div>
                <pre><code>{codeSoFar}</code></pre>
              </div>
              <span className="ai-streaming-cursor" />
            </div>
          </div>
        </div>
      );
    }

    // Mẫu 5: AI đặt marker [[BIEU_DO]] tại vị trí muốn chèn biểu đồ THẬT (chỉ có
    // khi câu hỏi trúng 1 mục trong danh mục — message.figure sẽ có giá trị).
    // Nếu marker xuất hiện nhưng KHÔNG có figure (VD nhánh /nhanxet sau khi chạy
    // code, biểu đồ đã hiện ở bong bóng phía trên) thì chỉ lặng lẽ bỏ marker đi.
    const MARKER = '[[BIEU_DO]]';
    const content = message.content || '';
    const hasMarker = content.includes(MARKER);
    let beforeChart = content;
    let afterChart = '';
    if (hasMarker) {
      const idx = content.indexOf(MARKER);
      beforeChart = content.slice(0, idx);
      afterChart = content.slice(idx + MARKER.length);
    } else if (message.figure && !message.streaming) {
      // AI quên đặt marker — không bao giờ mất biểu đồ, tự chèn vào cuối bài.
      afterChart = '';
    }
    const showChart = message.figure && (hasMarker || !message.streaming);

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          <div className="ai-msg-header">
            <div className="ai-msg-avatar">
              <Sparkles size={16} color="#fff" />
            </div>
            <span className="ai-msg-label">
              {message.streaming ? 'AI đang trả lời...' : 'AI Assistant'}
            </span>
            <span className="ai-msg-time-ai">{formatTime(message.timestamp)}</span>
            {!message.streaming && (
              <div className="ai-header-copy" style={{ display: 'flex', gap: '4px' }}>
                {onResend && message.prompt && (
                  <button className="ai-mini-btn" onClick={() => onResend(message.prompt)} data-tooltip="Tạo lại" type="button">
                    <RefreshCw size={13} />
                  </button>
                )}
                <CopyButton text={message.content} />
              </div>
            )}
          </div>
          <div className="ai-text-bubble ai-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {beforeChart.replace(MARKER, '')}
            </ReactMarkdown>
            {showChart && (
              <div className="ai-embedded-chart">
                <div className="ai-result-toolbar">
                  <button className="ai-mini-btn" onClick={() => setZoomed(true)} data-tooltip="Phóng to biểu đồ" type="button">
                    <Maximize2 size={14} />
                  </button>
                  <button className="ai-mini-btn" onClick={downloadPng} data-tooltip="Tải ảnh PNG" type="button">
                    <Download size={14} />
                  </button>
                </div>
                <PlotlyChart figure={message.figure} onGraphReady={(gd) => { graphDivRef.current = gd; }} />
              </div>
            )}
            {afterChart && (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {afterChart}
              </ReactMarkdown>
            )}
            {message.streaming && <span className="ai-streaming-cursor" />}
          </div>
          {!message.streaming && message.suggestions && message.suggestions.length > 0 && (
            <div className="ai-suggestions">
              <div className="ai-suggestions-label">Bạn muốn tìm hiểu sâu hơn khía cạnh nào?</div>
              <div className="ai-suggestions-chips">
                {message.suggestions.map((s) => (
                  <button
                    key={s.id}
                    className="ai-suggestion-chip-follow"
                    onClick={() => onResend && onResend(s.cau_hoi)}
                    type="button"
                  >
                    {s.cau_hoi}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal phóng to biểu đồ nhúng trong câu trả lời */}
        {zoomed && showChart && (
          <div className="ai-chart-modal-overlay" onClick={() => setZoomed(false)}>
            <div className="ai-chart-modal" onClick={(e) => e.stopPropagation()}>
              <button className="ai-chart-modal-close" title="Đóng" onClick={() => setZoomed(false)}>
                <X size={20} />
              </button>
              <div className="ai-chart-modal-body">
                <PlotlyChart figure={message.figure} />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // --- role: ai_result ---
  if (message.role === 'ai_result') {
    const resultData = message.resultData || {};
    const isChart = resultData.type === 'plotly';

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          <div className="ai-result-bubble">
            {/* Thanh công cụ kết quả: phóng to / tải PNG / tải CSV (chỉ với biểu đồ) */}
            {isChart && (
              <div className="ai-result-toolbar">
                <button className="ai-mini-btn" onClick={() => setZoomed(true)} data-tooltip="Phóng to biểu đồ" type="button">
                  <Maximize2 size={14} />
                </button>
                <button className="ai-mini-btn" onClick={downloadPng} data-tooltip="Tải ảnh PNG" type="button">
                  <Download size={14} />
                </button>
                {resultData.csv && (
                  <button className="ai-mini-btn" onClick={() => downloadCsv(resultData.csv)} data-tooltip="Tải dữ liệu CSV" type="button">
                    <FileDown size={14} />
                  </button>
                )}
              </div>
            )}
            <div className={`ai-result-content ${isChart ? 'chart-mode' : ''}`}>
              {isChart && (
                <PlotlyChart figure={resultData.data} onGraphReady={(gd) => { graphDivRef.current = gd; }} />
              )}
              {resultData.type === 'html' && (
                <div
                  dangerouslySetInnerHTML={{ __html: resultData.data }}
                  style={{ overflowX: 'auto' }}
                />
              )}
              {resultData.type === 'text' && (
                <div
                  style={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace',
                    fontSize: '14px',
                    backgroundColor: '#F3F4F6',
                    padding: '15px',
                    borderRadius: '8px'
                  }}
                >
                  {resultData.data}
                </div>
              )}
              {resultData.type === 'error' && (
                <div className="ai-result-error">
                  <div className="error-title">
                    <AlertTriangle size={15} /> Lỗi thực thi:
                  </div>
                  <pre>{resultData.data}</pre>
                </div>
              )}
            </div>
            <div className="ai-result-caption">
              <Info size={13} /> Kết quả dựa trên dữ liệu thật
              (vietnam_it_jobs_processed.csv)
            </div>
          </div>
        </div>

        {/* Modal phóng to biểu đồ để xem đầy đủ, không bị cắt */}
        {zoomed && isChart && (
          <div className="ai-chart-modal-overlay" onClick={() => setZoomed(false)}>
            <div className="ai-chart-modal" onClick={(e) => e.stopPropagation()}>
              <button className="ai-chart-modal-close" title="Đóng" onClick={() => setZoomed(false)}>
                <X size={20} />
              </button>
              <div className="ai-chart-modal-body">
                <PlotlyChart figure={resultData.data} />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // --- role: loading ---
  if (message.role === 'loading') {
    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          <div className="ai-msg-header">
            <div className="ai-msg-avatar">
              <Sparkles size={16} color="#fff" />
            </div>
            <span className="ai-msg-label">AI đang suy nghĩ...</span>
          </div>
          <div className="ai-loading-dots">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default AiChatMessage;
