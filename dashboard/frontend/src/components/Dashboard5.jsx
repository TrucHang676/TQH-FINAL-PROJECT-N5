import React, { useState, useEffect } from 'react';
import AiService from './ai/AiService';
import AiHistoryPanel from './ai/AiHistoryPanel';
import AiRequestForm from './ai/AiRequestForm';
import AiCodeCard from './ai/AiCodeCard';
import AiResultPanel from './ai/AiResultPanel';

export default function Dashboard5() {
  const [historyList, setHistoryList] = useState([]);
  const [currentRequestId, setCurrentRequestId] = useState(null);
  
  // Trạng thái hiện tại của phiên làm việc
  const [status, setStatus] = useState('empty'); // empty, loading_ai, pending_approval, executing, success, error, rejected
  const [code, setCode] = useState('');
  const [resultData, setResultData] = useState(null);

  // Load lịch sử lần đầu
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await AiService.getHistory();
      setHistoryList(data);
    } catch (error) {
      console.error('Failed to load history', error);
    }
  };

  const handleSendRequest = async (prompt) => {
    setStatus('loading_ai');
    setCode('');
    setResultData(null);
    setCurrentRequestId(null);

    try {
      const response = await AiService.sendRequest(prompt);
      setCode(response.code);
      setCurrentRequestId(response.requestId);
      setStatus('pending_approval');
      fetchHistory(); // Refresh lịch sử
    } catch (error) {
      console.error(error);
      setStatus('error');
      setResultData({ type: 'error', data: 'Lỗi khi gọi API AI: ' + error.message });
    }
  };

  const handleApprove = async (editedCode) => {
    setStatus('executing');
    setCode(editedCode);
    setResultData(null);

    try {
      const response = await AiService.executeCode(currentRequestId, editedCode);
      if (response.status === 'success') {
        setStatus('success');
      } else {
        setStatus('error');
      }
      setResultData(response.result || { type: 'error', data: response.logs });
      fetchHistory(); // Cập nhật lại trạng thái trong lịch sử
    } catch (error) {
      console.error(error);
      setStatus('error');
      setResultData({ type: 'error', data: 'Lỗi khi gọi API thực thi: ' + error.message });
      fetchHistory();
    }
  };

  const handleReject = () => {
    setStatus('rejected');
    setResultData(null);
    // Có thể gọi backend để update status nếu cần, hiện tại update local UI
  };

  const handleSelectHistoryItem = (item) => {
    setCurrentRequestId(item.id);
    setCode(item.code || '');
    setStatus(item.status || 'empty');
    setResultData(item.result || null);
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 120px)', backgroundColor: 'var(--bg-color)' }}>
      
      {/* 1. Cột trái: Panel Lịch sử */}
      <AiHistoryPanel 
        historyList={historyList} 
        onSelectItem={handleSelectHistoryItem}
        currentRequestId={currentRequestId}
      />

      {/* Khu vực trung tâm & bên phải */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto', padding: '20px' }}>
        
        <div style={{ display: 'flex', gap: '20px', flex: 1 }}>
          
          {/* 2. Cột giữa: Tương tác & Code */}
          <div style={{ flex: 1, minWidth: '0', display: 'flex', flexDirection: 'column' }}>
            <AiRequestForm 
              onSubmit={handleSendRequest} 
              isSubmitting={status === 'loading_ai'} 
            />
            
            <AiCodeCard 
              code={code}
              status={status}
              isExecuting={status === 'executing'}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          </div>

          {/* 3. Cột phải: Kết quả */}
          <div style={{ width: '450px', minWidth: '450px', display: 'flex', flexDirection: 'column' }}>
            {status === 'empty' ? (
              <div style={{ 
                height: '100%', 
                border: '1px dashed var(--border-color)', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: 'var(--text-secondary)',
                fontSize: '14px',
                textAlign: 'center',
                padding: '20px'
              }}>
                Chưa có kết quả phân tích. Vui lòng gửi yêu cầu từ form bên trái.
              </div>
            ) : status === 'loading_ai' || status === 'pending_approval' || status === 'executing' ? (
               <div style={{ 
                height: '100%', 
                border: '1px dashed var(--border-color)', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: 'var(--text-secondary)',
                fontSize: '14px',
                textAlign: 'center',
                padding: '20px'
              }}>
                Đang chờ thực thi mã nguồn...
              </div>
            ) : (
              <AiResultPanel resultData={resultData} />
            )}
          </div>
          
        </div>
      </div>
    </div>
  );
}

