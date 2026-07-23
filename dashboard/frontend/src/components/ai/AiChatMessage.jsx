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
  Info,
  Maximize2,
  Copy,
  Check,
  Download,
  FileDown,
  Pencil,
  RefreshCw,
  Send,
  Wand2,
  ChevronLeft,
  ChevronRight,
  Archive
} from 'lucide-react';

const formatTime = (ts) => {
  if (!ts) return '';
  const d = new Date(ts);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

// Đã bỏ hàm getStatusBadge — không hiện badge trạng thái nào nữa theo yêu cầu.
// Logic trạng thái (pending_approval/error/success/...) vẫn dùng bên trong để
// quyết định hiện nút Duyệt & Chạy, readonly editor, v.v.

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

const AiChatMessage = ({ message, onApprove, onReject, onResend, onRegenerate, onRegenerateText, onRetry, isExecuting, isSubmitting, compact }) => {
  // Mã nguồn MỞ mặc định để người dùng thấy ngay, có thể thu gọn lại
  const [isOpen, setIsOpen] = useState(true);
  const [editedCode, setEditedCode] = useState(message.code || '');
  const [zoomed, setZoomed] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(message.content || '');
  const graphDivRef = useRef(null);
  // A2b: ô nhập chỉ dẫn tinh chỉnh (thay cho "Tạo lại" mù) + chỉ số phiên bản đang
  // xem (mặc định = phiên bản MỚI NHẤT/hiện hành, tức sau các phiên bản lưu trữ).
  const [refining, setRefining] = useState(false);
  const [refineText, setRefineText] = useState('');
  const priorVersions = message.priorVersions || [];
  const [viewIndex, setViewIndex] = useState(priorVersions.length);
  useEffect(() => {
    // Khi có thêm phiên bản mới (regenerate xong), tự nhảy về xem bản mới nhất.
    setViewIndex(priorVersions.length);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [priorVersions.length]);
  const isViewingArchived = viewIndex < priorVersions.length;
  const archivedVersion = isViewingArchived ? priorVersions[viewIndex] : null;

  useEffect(() => {
    // A2b: đang xem 1 phiên bản LƯU TRỮ (không phải mới nhất) thì hiện code của
    // đúng phiên bản đó (chỉ đọc); ngược lại đồng bộ theo phiên bản hiện hành.
    if (isViewingArchived) {
      setEditedCode(archivedVersion?.code || '');
    } else if (message.code) {
      setEditedCode(message.code);
    }
  }, [message.code, isViewingArchived, archivedVersion]);

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
                onClick={() => { onResend && onResend(editText, null, message.id); setEditing(false); }}
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
    const firstLine = editedCode ? editedCode.split('\n')[0] : '';
    const isGenerating = message.status === 'generating';
    // A2b: khi xem 1 phiên bản LƯU TRỮ, hiện dẫn nhập của đúng phiên bản đó.
    const displayedPreamble = isViewingArchived ? (archivedVersion?.preamble || '') : message.preamble;
    const canRegenerate = onRegenerate && !isSubmitting && !isGenerating && message.prompt;

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          {/* Header: avatar + "AI Assistant" + giờ — bỏ hết badge trạng thái */}
          <div className="ai-msg-header">
            {!compact && (
              <>
                <div className="ai-msg-avatar">
                  <Sparkles size={16} color="#fff" />
                </div>
                <span className="ai-msg-label">AI Assistant</span>
              </>
            )}
            {!compact && (
              <span className="ai-msg-time-ai">{formatTime(message.timestamp)}</span>
            )}
          </div>

          {/* A2b: ô nhập chỉ dẫn tinh chỉnh — gửi kèm code hiện tại để AI CHỈNH SỬA
              thay vì viết lại mù từ đầu (VD "đổi sang biểu đồ ngang", "chỉ lấy top 10"). */}
          {refining && (
            <div className="ai-user-edit ai-refine-box">
              <textarea
                className="ai-user-edit-input"
                value={refineText}
                onChange={(e) => setRefineText(e.target.value)}
                placeholder='VD: "đổi sang biểu đồ cột ngang", "chỉ lấy top 10", "sắp xếp giảm dần"...'
                rows={2}
                autoFocus
              />
              <div className="ai-user-edit-actions">
                <button className="ai-mini-btn" onClick={() => setRefining(false)} type="button">
                  <X size={13} /> Hủy
                </button>
                <button
                  className="ai-mini-btn ai-mini-btn-primary"
                  onClick={() => { onRegenerate(message, refineText); setRefining(false); }}
                  disabled={!refineText.trim()}
                  type="button"
                >
                  <Send size={13} /> Gửi yêu cầu tinh chỉnh
                </button>
              </div>
            </div>
          )}

          {/* Mẫu 6: dẫn nhập + "Hướng phân tích" AI viết TRƯỚC code, hiển thị lại
              phía trên khung code để câu trả lời vẫn liền mạch như 1 khối. */}
          {displayedPreamble && (
            <div className="ai-text-bubble ai-markdown ai-code-preamble">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {displayedPreamble}
              </ReactMarkdown>
            </div>
          )}

          {/* A2b: đang xem phiên bản lưu trữ — chỉ đọc, không thể duyệt/chạy từ đây */}
          {isViewingArchived && (
            <div className="ai-archived-note">
              <Archive size={13} /> Đang xem phiên bản cũ (đã lưu trữ, chỉ đọc) — bấm ‹›  để quay lại phiên bản mới nhất.
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
              {isGenerating ? (
                <div className="ai-loading-dots" style={{ margin: '20px' }}>
                  <span /><span /><span />
                </div>
              ) : (
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
                      isViewingArchived ||
                      (message.status !== 'pending_approval' &&
                        message.status !== 'error')
                  }}
                />
              )}
            </div>
            {!isViewingArchived && (message.status === 'pending_approval' ||
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

          {/* Hàng nút Tạo lại/Tinh chỉnh/điều hướng phiên bản — ở CUỐI bong bóng
              code (kiểu Gemini): nhóm hành động bên TRÁI, điều hướng phiên bản
              "‹ i/N ›" bên PHẢI. */}
          {(priorVersions.length > 0 || canRegenerate) && (
            <div className="ai-code-footer-actions">
              <span className="ai-footer-left">
                {canRegenerate && (
                  <>
                    <button
                      className="ai-mini-btn"
                      onClick={() => onRegenerate(message, '')}
                      data-tooltip="Tạo lại"
                      type="button"
                    >
                      <RefreshCw size={13} />
                    </button>
                    <button
                      className="ai-mini-btn"
                      onClick={() => { setRefineText(''); setRefining(true); }}
                      data-tooltip="Tinh chỉnh"
                      type="button"
                    >
                      <Wand2 size={13} />
                    </button>
                  </>
                )}
              </span>
              {priorVersions.length > 0 && (
                <span className="ai-version-nav">
                  <button
                    className="ai-mini-btn"
                    onClick={() => setViewIndex(i => Math.max(0, i - 1))}
                    disabled={viewIndex <= 0}
                    data-tooltip="Phiên bản trước"
                    type="button"
                  >
                    <ChevronLeft size={13} />
                  </button>
                  <span className="ai-version-nav-label">{viewIndex + 1}/{priorVersions.length + 1}</span>
                  <button
                    className="ai-mini-btn"
                    onClick={() => setViewIndex(i => Math.min(priorVersions.length, i + 1))}
                    disabled={viewIndex >= priorVersions.length}
                    data-tooltip="Phiên bản mới hơn"
                    type="button"
                  >
                    <ChevronRight size={13} />
                  </button>
                </span>
              )}
            </div>
          )}
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
    // Điều kiện message.streaming: bong bóng bị DỪNG giữa chừng (A2a) chứa ``` dở
    // dang phải rơi xuống nhánh văn bản thường bên dưới (kèm ghi chú đã dừng),
    // không được kẹt vĩnh viễn ở giao diện "đang soạn mã nguồn".
    const rawContent = message.content || '';
    if (message.streaming && rawContent.includes('```')) {
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

    // A2b (mở rộng sang văn bản): đang xem 1 phiên bản LƯU TRỮ — hiện đúng nội
    // dung/biểu đồ/gợi ý của phiên bản đó (chỉ đọc), không phải bản mới nhất.
    const displayedSuggestions = isViewingArchived ? (archivedVersion?.suggestions || []) : (message.suggestions || []);
    const displayedFigure = isViewingArchived ? (archivedVersion?.figure || null) : message.figure;
    const canRegenerateText = onRegenerateText && !isSubmitting && !message.streaming &&
      !isViewingArchived && (message.prompt || message.isComment);

    // Mẫu 5: AI đặt marker [[BIEU_DO]] tại vị trí muốn chèn biểu đồ THẬT (chỉ có
    // khi câu hỏi trúng 1 mục trong danh mục — message.figure sẽ có giá trị).
    // Nếu marker xuất hiện nhưng KHÔNG có figure (VD nhánh /nhanxet sau khi chạy
    // code, biểu đồ đã hiện ở bong bóng phía trên) thì chỉ lặng lẽ bỏ marker đi.
    const MARKER = '[[BIEU_DO]]';
    const content = isViewingArchived ? (archivedVersion?.content || '') : (message.content || '');
    const hasMarker = content.includes(MARKER);
    let beforeChart = content;
    let afterChart = '';
    if (hasMarker) {
      const idx = content.indexOf(MARKER);
      beforeChart = content.slice(0, idx);
      afterChart = content.slice(idx + MARKER.length);
    } else if (displayedFigure && !message.streaming) {
      // AI quên đặt marker — không bao giờ mất biểu đồ, tự chèn vào cuối bài.
      afterChart = '';
    }
    const showChart = displayedFigure && (hasMarker || !message.streaming);

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          {/* compact: phần nhận xét tự động sau khi chạy code — nằm trong CÙNG 1
              khung với code/kết quả phía trên (.ai-turn-card), không lặp lại
              avatar + "AI Assistant" nữa. */}
          <div className="ai-msg-header">
            {!compact && (
              <>
                <div className="ai-msg-avatar">
                  <Sparkles size={16} color="#fff" />
                </div>
                <span className="ai-msg-label">
                  {!message.streaming ? 'AI Assistant' : content ? 'AI đang trả lời...' : 'AI đang suy nghĩ...'}
                </span>
                <span className="ai-msg-time-ai">{formatTime(message.timestamp)}</span>
              </>
            )}
          </div>

          {/* A2b: đang xem phiên bản văn bản lưu trữ — chỉ đọc */}
          {isViewingArchived && (
            <div className="ai-archived-note">
              <Archive size={13} /> Đang xem phiên bản cũ (đã lưu trữ, chỉ đọc) — bấm ‹›  để quay lại phiên bản mới nhất.
            </div>
          )}

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
                <PlotlyChart figure={displayedFigure} onGraphReady={(gd) => { graphDivRef.current = gd; }} />
              </div>
            )}
            {afterChart && (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {afterChart}
              </ReactMarkdown>
            )}
            {message.streaming && (
              content
                ? <span className="ai-streaming-cursor" />
                : (
                  <div className="ai-loading-dots ai-loading-dots-inline">
                    <span /><span /><span />
                  </div>
                )
            )}
            {/* A2a: người dùng bấm Dừng giữa chừng — giữ phần đã nhận, ghi chú rõ */}
            {message.stopped && (
              <div className="ai-stopped-note">Bạn đã dừng câu trả lời.</div>
            )}
          </div>
          {!message.streaming && displayedSuggestions.length > 0 && (
            <div className="ai-suggestions">
              <div className="ai-suggestions-label">Bạn muốn tìm hiểu sâu hơn khía cạnh nào?</div>
              <div className="ai-suggestions-chips">
                {displayedSuggestions.map((s) => (
                  <button
                    key={s.id}
                    className="ai-suggestion-chip-follow"
                    onClick={() => onResend && onResend(s.cau_hoi, s.id)}
                    type="button"
                  >
                    {s.cau_hoi}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Hàng hành động cuối bong bóng (kiểu Gemini): Sao chép/Tạo lại bên
              TRÁI, điều hướng phiên bản "‹ i/N ›" bên PHẢI. Tạo lại giờ CHỈNH
              SỬA TẠI CHỖ bong bóng này (giữ phiên bản cũ để xem lại), không tạo
              thêm cặp câu hỏi/trả lời mới. */}
          {!message.streaming && (
            <div className="ai-code-footer-actions">
              <span className="ai-footer-left">
                <CopyButton text={content} />
                {canRegenerateText && (
                  <button className="ai-mini-btn" onClick={() => onRegenerateText(message)} data-tooltip="Tạo lại" type="button">
                    <RefreshCw size={13} />
                  </button>
                )}
              </span>
              {priorVersions.length > 0 && (
                <span className="ai-version-nav">
                  <button
                    className="ai-mini-btn"
                    onClick={() => setViewIndex(i => Math.max(0, i - 1))}
                    disabled={viewIndex <= 0}
                    data-tooltip="Phiên bản trước"
                    type="button"
                  >
                    <ChevronLeft size={13} />
                  </button>
                  <span className="ai-version-nav-label">{viewIndex + 1}/{priorVersions.length + 1}</span>
                  <button
                    className="ai-mini-btn"
                    onClick={() => setViewIndex(i => Math.min(priorVersions.length, i + 1))}
                    disabled={viewIndex >= priorVersions.length}
                    data-tooltip="Phiên bản mới hơn"
                    type="button"
                  >
                    <ChevronRight size={13} />
                  </button>
                </span>
              )}
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
                <PlotlyChart figure={displayedFigure} />
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
              {/* A5c: lỗi HẾT QUOTA/gọi API thất bại — thông báo thân thiện + nút Thử
                  lại, thay vì hiện thẳng chuỗi lỗi thô của Google API cho người dùng. */}
              {resultData.type === 'error' && resultData.kind === 'quota' && (
                <div className="ai-result-error ai-result-error-quota">
                  <div className="error-title">
                    <AlertTriangle size={15} /> Tạm thời chưa gọi được AI
                  </div>
                  <p className="ai-quota-error-desc">
                    Hệ thống đã hết lượt gọi API cho phần này (giới hạn quota), có thể do
                    dùng nhiều trong thời gian ngắn. Vui lòng đợi một chút rồi thử lại.
                  </p>
                  {resultData.retry && onRetry && (
                    <button
                      className="ai-mini-btn ai-mini-btn-primary ai-retry-btn"
                      onClick={() => onRetry(resultData.retry)}
                      type="button"
                    >
                      <RefreshCw size={13} /> Thử lại
                    </button>
                  )}
                </div>
              )}
              {/* Lỗi THỰC THI code (traceback Python thật) — giữ nguyên chi tiết kỹ
                  thuật vì hữu ích để debug/sửa code, khác hẳn lỗi gọi API ở trên. */}
              {resultData.type === 'error' && resultData.kind !== 'quota' && (
                <div className="ai-result-error">
                  <div className="error-title">
                    <AlertTriangle size={15} /> Lỗi thực thi:
                  </div>
                  <pre>{resultData.data}</pre>
                </div>
              )}
            </div>
            {resultData.type !== 'error' && (
              <div className="ai-result-caption">
                <Info size={13} /> Kết quả dựa trên dữ liệu thật
                (vietnam_it_jobs_processed.csv)
              </div>
            )}
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
