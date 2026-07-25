import React, { useState, useMemo } from 'react';
import { Clock, Search, Plus, Trash2, MessageSquare, Pin, AlertTriangle, Edit2, Check, X } from 'lucide-react';

// Xác định nhóm thời gian của một mốc timestamp
const timeBucket = (ts) => {
  const d = new Date(ts);
  const now = new Date();
  const startToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startYesterday = new Date(startToday); startYesterday.setDate(startToday.getDate() - 1);
  const start7 = new Date(startToday); start7.setDate(startToday.getDate() - 7);
  if (d >= startToday) return 'Hôm nay';
  if (d >= startYesterday) return 'Hôm qua';
  if (d >= start7) return '7 ngày qua';
  return 'Cũ hơn';
};

const BUCKET_ORDER = ['Hôm nay', 'Hôm qua', '7 ngày qua', 'Cũ hơn'];

const AiHistoryPanel = ({
  historyList,
  onSelectConversation,
  onDeleteConversation,
  onTogglePin,
  onRenameConversation,
  currentConversationId,
  onNewChat
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(null); // conversation đang chờ xác nhận xóa
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  // Gom các câu hỏi rời rạc thành từng cuộc hội thoại theo conversationId.
  const conversations = useMemo(() => {
    const map = new Map();
    historyList.forEach(item => {
      const cid = item.conversationId || item.id;
      if (!map.has(cid)) map.set(cid, []);
      map.get(cid).push(item);
    });
    return Array.from(map.entries())
      .map(([cid, items]) => {
        const sorted = [...items].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        return {
          conversationId: cid,
          title: sorted[0].title || sorted[0].prompt,
          pinned: !!sorted[0].pinned,
          items: sorted,
          lastTimestamp: sorted[sorted.length - 1].timestamp
        };
      })
      .filter(c => c.title.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => new Date(b.lastTimestamp) - new Date(a.lastTimestamp));
  }, [historyList, searchTerm]);

  // Chia thành: nhóm Đã ghim + các nhóm theo thời gian
  const sections = useMemo(() => {
    const pinned = conversations.filter(c => c.pinned);
    const rest = conversations.filter(c => !c.pinned);
    const result = [];
    if (pinned.length) result.push({ label: 'Đã ghim', pinnedSection: true, items: pinned });
    BUCKET_ORDER.forEach(bucket => {
      const inBucket = rest.filter(c => timeBucket(c.lastTimestamp) === bucket);
      if (inBucket.length) result.push({ label: bucket, items: inBucket });
    });
    return result;
  }, [conversations]);

  const formatDate = (isoString) => {
    const d = new Date(isoString);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')} ${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
  };

  const renderConversation = (conv) => {
    const isSelected = conv.conversationId === currentConversationId;
    const isEditing = editingId === conv.conversationId;

    const handleSaveEdit = (e) => {
      if (e) e.stopPropagation();
      if (editTitle.trim()) {
        onRenameConversation(conv.conversationId, editTitle.trim());
      }
      setEditingId(null);
    };

    return (
      <div
        key={conv.conversationId}
        className="ai-history-item"
        onClick={() => { if (!isEditing) onSelectConversation(conv); }}
        style={{
          padding: '10px 12px',
          borderRadius: '10px',
          cursor: isEditing ? 'default' : 'pointer',
          marginBottom: '4px',
          backgroundColor: isSelected ? 'rgba(89, 178, 146, 0.08)' : 'transparent',
          border: `1.5px solid ${isSelected ? 'rgba(89, 178, 146, 0.3)' : 'transparent'}`,
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => { if (!isSelected && !isEditing) e.currentTarget.style.backgroundColor = '#f9fafb'; }}
        onMouseLeave={(e) => { if (!isSelected && !isEditing) e.currentTarget.style.backgroundColor = isSelected ? 'rgba(89, 178, 146, 0.08)' : 'transparent'; }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
          <MessageSquare size={14} color="var(--primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            {isEditing ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }} onClick={(e) => e.stopPropagation()}>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveEdit(e);
                    else if (e.key === 'Escape') setEditingId(null);
                  }}
                  autoFocus
                  style={{
                    width: '100%',
                    fontSize: '12px',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    border: '1px solid var(--primary)',
                    outline: 'none',
                    backgroundColor: '#fff',
                    color: '#111'
                  }}
                />
              </div>
            ) : (
              <div style={{ fontSize: '12px', fontWeight: isSelected ? '600' : '500', color: 'var(--text-primary)', marginBottom: '4px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.4 }}>
                {conv.title}
              </div>
            )}
            <div style={{ fontSize: '10px', color: '#9CA3AF' }}>
              {formatDate(conv.lastTimestamp)}
            </div>
          </div>
          <div className="ai-history-actions">
            {isEditing ? (
              <>
                <button
                  className="ai-history-action-btn"
                  title="Lưu đổi tên"
                  style={{ color: '#10B981' }}
                  onClick={handleSaveEdit}
                >
                  <Check size={13} />
                </button>
                <button
                  className="ai-history-action-btn"
                  title="Hủy"
                  style={{ color: '#EF4444' }}
                  onClick={(e) => { e.stopPropagation(); setEditingId(null); }}
                >
                  <X size={13} />
                </button>
              </>
            ) : (
              <>
                <button
                  className="ai-history-action-btn"
                  title="Đổi tên cuộc hội thoại"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingId(conv.conversationId);
                    setEditTitle(conv.title);
                  }}
                >
                  <Edit2 size={13} />
                </button>
                <button
                  className={`ai-history-action-btn ${conv.pinned ? 'pinned' : ''}`}
                  title={conv.pinned ? 'Bỏ ghim' : 'Ghim cuộc hội thoại'}
                  onClick={(e) => { e.stopPropagation(); onTogglePin(conv.conversationId); }}
                >
                  <Pin size={13} fill={conv.pinned ? 'currentColor' : 'none'} />
                </button>
                <button
                  className="ai-history-action-btn danger"
                  title="Xóa cuộc hội thoại"
                  onClick={(e) => { e.stopPropagation(); setConfirmDelete(conv); }}
                >
                  <Trash2 size={13} />
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
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
        {sections.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#9CA3AF', fontSize: '12px', marginTop: '30px', lineHeight: 1.5 }}>
            Chưa có cuộc hội thoại nào.
          </div>
        ) : (
          sections.map(section => (
            <div key={section.label} style={{ marginBottom: '10px' }}>
              <div className="ai-history-section-label">
                {section.pinnedSection && <Pin size={11} fill="currentColor" />}
                {section.label}
              </div>
              {section.items.map(renderConversation)}
            </div>
          ))
        )}
      </div>

      {/* Modal xác nhận xóa */}
      {confirmDelete && (
        <div className="ai-confirm-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="ai-confirm-box" onClick={(e) => e.stopPropagation()}>
            <div className="ai-confirm-icon"><AlertTriangle size={22} /></div>
            <div className="ai-confirm-title">Xóa cuộc hội thoại?</div>
            <div className="ai-confirm-desc">
              Cuộc hội thoại “{confirmDelete.title}” sẽ bị xóa vĩnh viễn. Hành động này không thể hoàn tác.
            </div>
            <div className="ai-confirm-actions">
              <button className="ai-mini-btn" onClick={() => setConfirmDelete(null)} type="button">
                Hủy
              </button>
              <button
                className="ai-confirm-delete-btn"
                onClick={() => { onDeleteConversation(confirmDelete.conversationId); setConfirmDelete(null); }}
                type="button"
              >
                <Trash2 size={14} /> Xóa
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AiHistoryPanel;
