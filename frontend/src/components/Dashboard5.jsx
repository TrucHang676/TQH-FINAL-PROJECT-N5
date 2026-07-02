import React from 'react';

export default function Dashboard5() {
  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: 'rgba(89, 178, 146, 0.03)', 
      minHeight: 'calc(100vh - 180px)', 
      borderRadius: '12px', 
      border: '1px dashed rgba(89, 178, 146, 0.3)',
      margin: '20px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <h2 style={{ fontSize: '28px', fontWeight: '800', color: '#1a5944', textTransform: 'uppercase', letterSpacing: '1px' }}>
        05 AI phân tích
      </h2>
      <p style={{ marginTop: '12px', color: '#6b7280', fontSize: '14px' }}>
        Trang phân tích thông minh sử dụng trí tuệ nhân tạo (AI) để đưa ra đề xuất định hướng nghề nghiệp.
      </p>
    </div>
  );
}
