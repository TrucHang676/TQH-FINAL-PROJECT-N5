import React, { useState } from 'react';
import { Clock, Search, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

const AiHistoryPanel = ({ historyList, onSelectItem, currentRequestId }) => {
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
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')} ${d.getDate()}/${d.getMonth()+1}/${d.getFullYear()}`;
  };

  return (
    <div className="ai-history-panel" style={{
      width: '300px', 
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#fff',
      height: '100%'
    }}>
      <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={18} color="var(--primary-color)" />
          Lịch sử phân tích
        </h3>
        
        <div style={{ position: 'relative' }}>
          <Search size={16} color="#9CA3AF" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input 
            type="text" 
            placeholder="Tìm kiếm câu hỏi..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 36px',
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
              fontSize: '13px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
        {filteredHistory.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#9CA3AF', fontSize: '13px', marginTop: '30px' }}>
            Không tìm thấy lịch sử nào.
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
                  padding: '12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  marginBottom: '8px',
                  backgroundColor: isSelected ? 'rgba(89, 178, 146, 0.08)' : 'transparent',
                  border: `1px solid ${isSelected ? 'var(--primary-color)' : 'transparent'}`,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = '#f9fafb' }}
                onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = 'transparent' }}
              >
                <div style={{ fontSize: '13px', fontWeight: isSelected ? '600' : '500', color: 'var(--text-primary)', marginBottom: '6px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {item.prompt}
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px' }}>
                  <div style={{ color: '#6B7280' }}>
                    {formatDate(item.timestamp)}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: statusConfig.color, fontWeight: '500' }}>
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
