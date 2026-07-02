import React from 'react';

export default function Dashboard_page4() {
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
        04 Nhân sự trẻ
      </h2>
      <p style={{ marginTop: '12px', color: '#6b7280', fontSize: '14px' }}>
        Trang thống kê cơ hội tuyển dụng cho sinh viên, Intern, Fresher và cơ hội nghề nghiệp trẻ.
      </p>
    </div>
  );
}
