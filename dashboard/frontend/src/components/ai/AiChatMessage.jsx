import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
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
  Info
} from 'lucide-react';

const formatTime = (ts) => {
  if (!ts) return '';
  const d = new Date(ts);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
};

const getStatusBadge = (status) => {
  switch (status) {
    case 'pending_approval':
      return {
        statusClass: 'pending',
        statusIcon: <AlertTriangle size={13} />,
        statusText: 'Chờ duyệt'
      };
    case 'executing':
      return {
        statusClass: 'executing',
        statusIcon: <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />,
        statusText: 'Đang chạy...'
      };
    case 'success':
      return {
        statusClass: 'success',
        statusIcon: <CheckCircle2 size={13} />,
        statusText: 'Thành công'
      };
    case 'error':
      return {
        statusClass: 'error',
        statusIcon: <XCircle size={13} />,
        statusText: 'Lỗi'
      };
    case 'rejected':
      return {
        statusClass: 'rejected',
        statusIcon: <X size={13} />,
        statusText: 'Đã từ chối'
      };
    default:
      return {
        statusClass: '',
        statusIcon: null,
        statusText: ''
      };
  }
};

const AiChatMessage = ({ message, onApprove, onReject, isExecuting }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editedCode, setEditedCode] = useState(message.code || '');

  useEffect(() => {
    if (message.code) {
      setEditedCode(message.code);
    }
  }, [message.code]);

  // --- role: user ---
  if (message.role === 'user') {
    return (
      <div className="ai-msg-row user">
        <div className="ai-msg-user">
          <div>{message.content}</div>
          <div className="ai-msg-time">{formatTime(message.timestamp)}</div>
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
          </div>

          {/* Code Accordion */}
          <div className="ai-code-accordion">
            <div
              className="ai-code-accordion-header"
              onClick={() => setIsOpen(!isOpen)}
            >
              <div className="ai-code-accordion-title">
                <Code2 size={15} /> Mã nguồn Python
                {!isOpen && (
                  <span className="ai-code-preview">{firstLine}</span>
                )}
              </div>
              <ChevronDown
                className={`ai-code-accordion-chevron ${isOpen ? 'open' : ''}`}
              />
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
                    <Loader2
                      size={15}
                      style={{ animation: 'spin 1s linear infinite' }}
                    />
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

  // --- role: ai_result ---
  if (message.role === 'ai_result') {
    const resultData = message.resultData || {};

    return (
      <div className="ai-msg-row ai">
        <div className="ai-msg-ai">
          <div className="ai-result-bubble">
            <div className={`ai-result-content ${resultData.type === 'plotly' ? 'chart-mode' : ''}`}>
              {resultData.type === 'plotly' && (
                <PlotlyChart figure={resultData.data} />
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
