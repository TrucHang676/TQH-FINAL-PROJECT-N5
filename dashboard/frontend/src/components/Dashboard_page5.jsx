import React, { useState, useEffect, useRef } from 'react';
import AiService from './ai/AiService';
import AiHistoryPanel from './ai/AiHistoryPanel';
import AiRequestForm from './ai/AiRequestForm';
import AiChatMessage from './ai/AiChatMessage';
import { Sparkles } from 'lucide-react';

// Sinh 1 ID cuộc hội thoại mới (ưu tiên crypto.randomUUID, fallback timestamp)
const newConversationId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : 'conv_' + Date.now();

export default function Dashboard_page5() {
  const [historyList, setHistoryList] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(() => newConversationId());
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [executingId, setExecutingId] = useState(null);
  // Tự động nhận xét sau khi 1 biểu đồ chạy thành công (tách 2 pha: biểu đồ hiện
  // ngay, nhận xét đến sau) — mặc định bật, người dùng có thể tắt để tiết kiệm quota.
  const [autoComment, setAutoComment] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    // Auto scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchHistory = async () => {
    try {
      const data = await AiService.getHistory();
      setHistoryList(data);
    } catch (error) {
      console.error('Failed to load history', error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentConversationId(newConversationId());
    setIsSubmitting(false);
    setExecutingId(null);
  };

  // Gửi 1 yêu cầu và nhận câu trả lời theo THỜI GIAN THỰC (streaming SSE).
  // mode: null/'auto' (mặc định) | 'ask' (/hoi) | 'code' (/code) | 'explain' (/giaithich) | 'comment' (/nhanxet)
  const handleSendRequest = (prompt, image, mode) => {
    const tempId = 'tmp_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);

    const userMsg = {
      id: tempId + '_user',
      role: 'user',
      content: prompt,
      image: image || null,
      timestamp: new Date().toISOString()
    };
    const loadingMsg = {
      id: tempId + '_loading',
      role: 'loading',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setIsSubmitting(true);

    let textStarted = false;

    AiService.streamRequest(
      { prompt, conversationId: currentConversationId, image, mode },
      {
        onStart: (meta) => {
          // Mẫu 6: MỌI nhánh giờ đều stream văn bản ngay từ đầu (kể cả nhánh có
          // thể ra code — Chế độ B luôn viết dẫn nhập + "Hướng phân tích" trước
          // code) nên luôn tạo bong bóng văn bản streaming; nếu cuối cùng ra code,
          // onDone sẽ chuyển bong bóng này thành ai_code (giữ lại phần dẫn nhập).
          textStarted = true;
          setMessages(prev => prev.filter(m => m.id !== tempId + '_loading').concat({
            id: tempId + '_text',
            role: 'ai_text',
            content: '',
            prompt,
            requestId: null,
            streaming: true,
            // Mẫu 5: nếu câu hỏi trúng 1 mục trong danh mục biểu đồ, backend gửi
            // kèm figure THẬT ngay từ đầu — AiChatMessage sẽ chèn nó vào đúng vị
            // trí marker [[BIEU_DO]] khi nội dung stream chảy tới đó.
            catalogId: meta.catalogId || null,
            figure: meta.figure || null,
            timestamp: new Date().toISOString()
          }));
        },
        onDelta: (text) => {
          if (!textStarted) return;
          setMessages(prev => prev.map(m =>
            m.id === tempId + '_text' ? { ...m, content: (m.content || '') + text } : m
          ));
        },
        onDone: (meta) => {
          setIsSubmitting(false);
          if (meta.type === 'text') {
            setMessages(prev => prev.map(m =>
              m.id === tempId + '_text'
                ? {
                    ...m, id: meta.requestId + '_text', requestId: meta.requestId,
                    streaming: false, suggestions: meta.suggestions || []
                  }
                : m
            ));
          } else {
            // type === 'code' (Mẫu 6): bong bóng văn bản đang stream (dẫn nhập +
            // Hướng phân tích + code thô) được thay bằng bong bóng ai_code chính
            // thức, giữ lại preamble để hiển thị phía trên khung code duyệt/chạy.
            setMessages(prev => prev
              .filter(m => m.id !== tempId + '_loading' && m.id !== tempId + '_text')
              .concat({
                id: meta.requestId + '_code',
                role: 'ai_code',
                code: meta.code,
                preamble: meta.preamble || '',
                prompt,
                status: 'pending_approval',
                requestId: meta.requestId,
                timestamp: new Date().toISOString()
              }));
          }
          fetchHistory();
        },
        onError: (message) => {
          setIsSubmitting(false);
          setMessages(prev => prev
            .filter(m => m.id !== tempId + '_loading' && m.id !== tempId + '_text')
            .concat({
              id: tempId + '_error',
              role: 'ai_result',
              resultData: { type: 'error', data: 'Lỗi khi gọi API AI: ' + message },
              timestamp: new Date().toISOString()
            }));
        }
      }
    );
  };

  // Tự động nhận xét sau khi 1 biểu đồ chạy thành công — dùng lại đúng lệnh /nhanxet
  // ở phía backend (mode='comment'), backend tự tìm kết quả biểu đồ mới nhất của
  // cuộc hội thoại này. Hiện dạng bong bóng văn bản streaming ngay dưới biểu đồ.
  const triggerAutoComment = (afterRequestId) => {
    const tempId = 'cmt_' + afterRequestId;
    setMessages(prev => [...prev, {
      id: tempId,
      role: 'ai_text',
      content: '',
      streaming: true,
      isComment: true,
      timestamp: new Date().toISOString()
    }]);

    AiService.streamRequest(
      { prompt: '', conversationId: currentConversationId, mode: 'comment' },
      {
        onDelta: (text) => {
          setMessages(prev => prev.map(m =>
            m.id === tempId ? { ...m, content: (m.content || '') + text } : m
          ));
        },
        onDone: (meta) => {
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? {
                  ...m, id: meta.requestId + '_comment', requestId: meta.requestId,
                  streaming: false, suggestions: meta.suggestions || []
                }
              : m
          ));
          fetchHistory();
        },
        onError: () => {
          setMessages(prev => prev.map(m =>
            m.id === tempId
              ? { ...m, streaming: false, commentError: true, content: 'Không thể tạo nhận xét tự động.' }
              : m
          ));
        }
      }
    );
  };

  const handleApprove = async (requestId, editedCode) => {
    setExecutingId(requestId);

    // Update code message status to executing
    setMessages(prev => prev.map(m =>
      m.requestId === requestId && m.role === 'ai_code'
        ? { ...m, status: 'executing', code: editedCode }
        : m
    ));

    try {
      const response = await AiService.executeCode(requestId, editedCode);
      const newStatus = response.status === 'success' ? 'success' : 'error';

      // Update code message status
      setMessages(prev => prev.map(m =>
        m.requestId === requestId && m.role === 'ai_code'
          ? { ...m, status: newStatus }
          : m
      ));

      // Add result message
      const resultMsg = {
        id: requestId + '_result',
        role: 'ai_result',
        resultData: response.result || { type: 'error', data: response.logs },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, resultMsg]);
      fetchHistory();

      // Tách 2 pha: biểu đồ đã hiện xong ở trên — nếu bật tự động nhận xét và có
      // dữ liệu (result.csv) thì mới gọi tiếp, không làm chậm việc hiện biểu đồ.
      if (autoComment && response.result?.type === 'plotly' && response.result?.csv) {
        triggerAutoComment(requestId);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => prev.map(m =>
        m.requestId === requestId && m.role === 'ai_code'
          ? { ...m, status: 'error' }
          : m
      ));

      const errorMsg = {
        id: requestId + '_result',
        role: 'ai_result',
        resultData: { type: 'error', data: 'Lỗi khi thực thi: ' + error.message },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
      fetchHistory();
    } finally {
      setExecutingId(null);
    }
  };

  const handleReject = (requestId) => {
    setMessages(prev => prev.map(m =>
      m.requestId === requestId && m.role === 'ai_code'
        ? { ...m, status: 'rejected' }
        : m
    ));
  };

  // Dựng lại toàn bộ tin nhắn của 1 cuộc hội thoại (nhiều câu hỏi nối tiếp nhau).
  // conversation.items đã được sắp xếp tăng dần theo thời gian ở History Panel.
  const handleSelectConversation = (conversation) => {
    setCurrentConversationId(conversation.conversationId);
    const rebuilt = [];
    conversation.items.forEach(item => {
      rebuilt.push({
        id: item.id + '_user',
        role: 'user',
        content: item.prompt,
        image: item.image || null,
        timestamp: item.timestamp
      });
      if (item.type === 'text') {
        rebuilt.push({
          id: item.id + '_text',
          role: 'ai_text',
          content: item.answer,
          prompt: item.prompt,
          requestId: item.id,
          catalogId: item.catalogId || null,
          figure: item.figure || null,
          suggestions: item.suggestions || [],
          timestamp: item.timestamp
        });
      } else if (item.code) {
        rebuilt.push({
          id: item.id + '_code',
          role: 'ai_code',
          code: item.code,
          preamble: item.preamble || '',
          prompt: item.prompt,
          status: item.status || 'success',
          requestId: item.id,
          timestamp: item.timestamp
        });
        if (item.result) {
          rebuilt.push({
            id: item.id + '_result',
            role: 'ai_result',
            resultData: item.result,
            timestamp: item.timestamp
          });
        }
      }
    });
    setMessages(rebuilt);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await AiService.deleteConversation(conversationId);
      // Nếu đang xem đúng cuộc hội thoại vừa xóa thì dọn khung chat về trạng thái mới
      if (conversationId === currentConversationId) {
        handleNewChat();
      }
      fetchHistory();
    } catch (error) {
      console.error('Failed to delete conversation', error);
    }
  };

  const handleTogglePin = async (conversationId) => {
    try {
      await AiService.togglePin(conversationId);
      fetchHistory();
    } catch (error) {
      console.error('Failed to toggle pin', error);
    }
  };

  // Tạo lại / Sửa & gửi lại: đều gửi 1 câu hỏi mới trong cùng cuộc hội thoại hiện tại
  // (nhờ ngữ cảnh, AI vẫn hiểu mạch hội thoại). Dùng chung handleSendRequest.
  const handleResend = (prompt) => {
    if (prompt && prompt.trim() && !isSubmitting) {
      handleSendRequest(prompt.trim());
    }
  };

  return (
    <div className="ai-chat-container">
      <AiHistoryPanel
        historyList={historyList}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onTogglePin={handleTogglePin}
        currentConversationId={currentConversationId}
        onNewChat={handleNewChat}
      />

      <div className="ai-chat-main">
        <div className="ai-auto-comment-bar">
          <label className="ai-toggle">
            <input
              type="checkbox"
              checked={autoComment}
              onChange={(e) => setAutoComment(e.target.checked)}
            />
            <span className="ai-toggle-track"><span className="ai-toggle-thumb" /></span>
          </label>
          <span>Tự động nhận xét sau khi chạy biểu đồ</span>
        </div>

        <div className="ai-chat-messages">
          {messages.map(msg => (
            <AiChatMessage
              key={msg.id}
              message={msg}
              onApprove={handleApprove}
              onReject={handleReject}
              onResend={handleResend}
              isExecuting={executingId === msg.requestId}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        <AiRequestForm
          onSubmit={handleSendRequest}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  );
}
