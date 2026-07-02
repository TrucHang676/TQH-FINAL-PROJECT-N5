import React, { useState } from 'react';
import { Clock, Search, CheckCircle2, AlertCircle, XCircle, Plus } from 'lucide-react';

const AiHistoryPanel = ({ historyList, onSelectItem, currentRequestId, onNewChat }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = historyList.filter(item =>
    item.prompt.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusConfig = (status) => {
    switch (status) {
      case 'success': return { color: '#59B292', icon: <CheckCircle2 size={14} />, text: 'Thành công' };
      case 'error': return { color: '#EF4444', icon: <XCircle size={14} />, text: 'Lỗi' };
      case 'pending_approval': return { color: '#F59E0B', icon: <AlertCircle size={14} />, text: 'Chờ duyệt' };
      case 'rejected': return { color: '#9CA3AF', icon: <XCircle size={14} />, text: 'Đã hủy' };
      default: return { color: '#6B7280', icon: <Clock size={14} />, text: 'Không rõ' };
    }
  };

  const formatDate = (isoString) => {
    const d = new Date(isoString);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')} ${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
  };

  return (
    <div style={{
      width: '260px',
      minWidth: '260px',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#fff',
      height: '100%'
    }}>
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
          <Clock size={16} color="var(--primary)" />
          Lịch sử phân tích
        </h3>

        <button className="ai-new-chat-btn" onClick={onNewChat}>
          <Plus size={15} />
          Cuộc hội thoại mới
        </button>

        <div style={{ position: 'relative' }}>
          <Search size={14} color="#9CA3AF" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Tìm kiếm..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 10px 8px 32px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              fontSize: '12px',
              outline: 'none',
              boxSizing: 'border-box',
              transition: 'border-color 0.2s',
            }}
            onFocus={(e) => e.target.style.borderColor = '#59B292'}
            onBlur={(e) => e.target.style.borderColor = ''}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {filteredHistory.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#9CA3AF', fontSize: '12px', marginTop: '30px', lineHeight: 1.5 }}>
            Chưa có lịch sử phân tích nào.
          </div>
        ) : (
          filteredHistory.map(item => {
            const statusConfig = getStatusConfig(item.status);
            const isSelected = item.id === currentRequestId;

            return (
              <div
                key={item.id}
                onClick={() => onSelectItem(item)}
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  marginBottom: '4px',
                  backgroundColor: isSelected ? 'rgba(89, 178, 146, 0.08)' : 'transparent',
                  border: `1.5px solid ${isSelected ? 'rgba(89, 178, 146, 0.3)' : 'transparent'}`,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = '#f9fafb' }}
                onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = isSelected ? 'rgba(89, 178, 146, 0.08)' : 'transparent' }}
              >
                <div style={{ fontSize: '12px', fontWeight: isSelected ? '600' : '500', color: 'var(--text-primary)', marginBottom: '6px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.4 }}>
                  {item.prompt}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px' }}>
                  <div style={{ color: '#9CA3AF' }}>
                    {formatDate(item.timestamp)}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '3px', color: statusConfig.color, fontWeight: '500' }}>
                    {statusConfig.icon}
                    {statusConfig.text}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default AiHistoryPanel;
