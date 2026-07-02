import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Code2, Play, X, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react';

const AiCodeCard = ({ code, status, onApprove, onReject, isExecuting }) => {
  const [editedCode, setEditedCode] = useState(code);

  useEffect(() => {
    setEditedCode(code);
  }, [code]);

  if (!code && status !== 'pending_approval' && status !== 'error') return null;

  const renderBadge = () => {
    switch (status) {
      case 'pending_approval':
        return <span style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: '#FEF3C7', color: '#D97706', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}><AlertTriangle size={14}/> Chờ duyệt</span>;
      case 'executing':
        return <span style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: '#DBEAFE', color: '#2563EB', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}><Loader2 size={14} className="lucide-spin" style={{ animation: 'spin 2s linear infinite' }} /> Đang chạy...</span>;
      case 'success':
        return <span style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: '#D1FAE5', color: '#059669', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}><CheckCircle2 size={14}/> Đã duyệt & Chạy thành công</span>;
      case 'error':
        return <span style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: '#FEE2E2', color: '#DC2626', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}><X size={14}/> Lỗi thực thi</span>;
      case 'rejected':
        return <span style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: '#F3F4F6', color: '#6B7280', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}><X size={14}/> Đã từ chối</span>;
      default:
        return null;
    }
  };

  return (
    <div className="chart-card" style={{ marginBottom: '20px' }}>
      <div className="chart-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="chart-title">
          <Code2 size={16} color="#B45309" />
          Mã nguồn do AI đề xuất
        </span>
        {renderBadge()}
      </div>
      
      <div className="chart-content" style={{ padding: '0', borderBottom: '1px solid var(--border-color)' }}>
        <Editor
          height="300px"
          language="python"
          theme="vs-dark"
          value={editedCode}
          onChange={(value) => setEditedCode(value)}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            wordWrap: 'on',
            readOnly: status === 'executing' || status === 'success' || status === 'rejected'
          }}
        />
      </div>

      {(status === 'pending_approval' || status === 'error') && (
        <div style={{ padding: '15px 20px', display: 'flex', justifyContent: 'flex-end', gap: '15px', backgroundColor: '#F9FAFB', borderBottomLeftRadius: '12px', borderBottomRightRadius: '12px' }}>
          <button
            onClick={onReject}
            disabled={isExecuting}
            style={{
              backgroundColor: '#fff',
              color: '#4B5563',
              border: '1px solid #D1D5DB',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: isExecuting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s'
            }}
          >
            <X size={16} /> Từ chối
          </button>
          <button
            onClick={() => onApprove(editedCode)}
            disabled={isExecuting}
            style={{
              backgroundColor: 'var(--primary-color)',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: isExecuting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(89, 178, 146, 0.3)'
            }}
          >
            {isExecuting ? <Loader2 size={16} className="lucide-spin" style={{ animation: 'spin 2s linear infinite' }} /> : <Play size={16} />}
            Chấp thuận & Chạy
          </button>
        </div>
      )}
    </div>
  );
};

export default AiCodeCard;
