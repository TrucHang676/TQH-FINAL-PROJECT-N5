import React, { useState, useEffect, useRef } from 'react';
import AiService from './ai/AiService';
import AiHistoryPanel from './ai/AiHistoryPanel';
import AiRequestForm from './ai/AiRequestForm';
import AiChatMessage from './ai/AiChatMessage';
import { Sparkles } from 'lucide-react';

export default function Dashboard5() {
  const [historyList, setHistoryList] = useState([]);
  const [currentRequestId, setCurrentRequestId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [executingId, setExecutingId] = useState(null);
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
    setCurrentRequestId(null);
    setIsSubmitting(false);
    setExecutingId(null);
  };

  const handleSendRequest = async (prompt) => {
    // Add user message
    const userMsg = {
      id: Date.now() + '_user',
      role: 'user',
      content: prompt,
      timestamp: new Date().toISOString()
    };

    // Add loading indicator
    const loadingMsg = {
      id: Date.now() + '_loading',
      role: 'loading',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setIsSubmitting(true);

    try {
      const response = await AiService.sendRequest(prompt);
      setCurrentRequestId(response.requestId);

      // Replace loading with AI code message
      const aiCodeMsg = {
        id: response.requestId + '_code',
        role: 'ai_code',
        code: response.code,
        status: 'pending_approval',
        requestId: response.requestId,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => prev.filter(m => m.role !== 'loading').concat(aiCodeMsg));
      fetchHistory();
    } catch (error) {
      console.error(error);
      // Replace loading with error
      const errorMsg = {
        id: Date.now() + '_result',
        role: 'ai_result',
        resultData: { type: 'error', data: 'Lỗi khi gọi API AI: ' + error.message },
        timestamp: new Date().toISOString()
      };
      setMessages(prev => prev.filter(m => m.role !== 'loading').concat(errorMsg));
    } finally {
      setIsSubmitting(false);
    }
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

  const handleSelectHistoryItem = (item) => {
    setCurrentRequestId(item.id);
    // Rebuild messages from history item
    const rebuilt = [];
    rebuilt.push({
      id: item.id + '_user',
      role: 'user',
      content: item.prompt,
      timestamp: item.timestamp
    });
    if (item.code) {
      rebuilt.push({
        id: item.id + '_code',
        role: 'ai_code',
        code: item.code,
        status: item.status || 'success',
        requestId: item.id,
        timestamp: item.timestamp
      });
    }
    if (item.result) {
      rebuilt.push({
        id: item.id + '_result',
        role: 'ai_result',
        resultData: item.result,
        timestamp: item.timestamp
      });
    }
    setMessages(rebuilt);
  };

  return (
    <div className="ai-chat-container">
      <AiHistoryPanel
        historyList={historyList}
        onSelectItem={handleSelectHistoryItem}
        currentRequestId={currentRequestId}
        onNewChat={handleNewChat}
      />

      <div className="ai-chat-main">
        {messages.length === 0 ? (
          <div className="ai-welcome">
            <div className="ai-welcome-icon">
              <Sparkles size={30} color="#59B292" />
            </div>
            <h3>AI Phân tích Dữ liệu</h3>
            <p>
              Hãy nhập câu hỏi hoặc yêu cầu phân tích bên dưới.
              AI sẽ tự động viết mã Python, bạn duyệt và chạy để xem kết quả trực quan.
            </p>
          </div>
        ) : (
          <div className="ai-chat-messages">
            {messages.map(msg => (
              <AiChatMessage
                key={msg.id}
                message={msg}
                onApprove={handleApprove}
                onReject={handleReject}
                isExecuting={executingId === msg.requestId}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        <AiRequestForm
          onSubmit={handleSendRequest}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  );
}
