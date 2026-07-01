import React from 'react';
import Dashboard from './components/Dashboard';

// Import CSS y hệt như cấu trúc của Dash
import './styles/style.css';
import './styles/stylePage1.css';

function App() {
  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#FDFBF7' }}>
      {/* Header */}
      <div className="header" style={{ padding: '15px 24px', backgroundColor: '#1F6F5F', color: '#FDFBF7', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="logo-placeholder" style={{ width: '32px', height: '32px', backgroundColor: '#FDFBF7', borderRadius: '4px' }}></div>
          <span style={{ fontSize: '18px', fontWeight: 'bold' }}>Dashboard Phân Tích Tin Tuyển Dụng IT Việt Nam</span>
        </div>
        <div style={{ display: 'flex', gap: '20px' }}>
          <a href="#" style={{ color: '#FDFBF7', textDecoration: 'none' }}>Về Dự Án</a>
          <a href="#" style={{ color: '#FDFBF7', textDecoration: 'none' }}>Nguồn Dữ Liệu</a>
          <a href="#" style={{ color: '#FDFBF7', textDecoration: 'none' }}>Tác Giả</a>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="nav-tabs" style={{ display: 'flex', padding: '0 24px', backgroundColor: '#1F6F5F', borderBottom: '1px solid #165246' }}>
        <div className="nav-tab active" style={{ padding: '12px 24px', cursor: 'pointer', borderBottom: '3px solid #FA6781', fontWeight: 'bold' }}>Xu Hướng & Địa Lý</div>
        <div className="nav-tab" style={{ padding: '12px 24px', cursor: 'pointer', opacity: 0.7 }}>Kỹ Năng & Lương</div>
        <div className="nav-tab" style={{ padding: '12px 24px', cursor: 'pointer', opacity: 0.7 }}>Phân Tích Sâu</div>
      </div>

      {/* Main Content */}
      <div className="main-content-wrapper" style={{ flex: 1, overflow: 'hidden' }}>
        <Dashboard />
      </div>
    </div>
  );
}

export default App;
