import React from 'react';
import Dashboard from './components/Dashboard';

// Import CSS y hệt như cấu trúc của Dash
import './styles/style.css';
import './styles/stylePage1.css';

function App() {
  return (
    <div id="page1-container">
      {/* Cấu trúc Header toàn cục chuẩn xác từ app.py */}
      <div className="global-header">
        <div className="global-title-container">
          <h1 className="global-title">Thị trường tuyển dụng IT Việt Nam</h1>
          <div className="global-subtitle-container">
            <span className="global-subtitle-main">Mục tiêu 1</span>
            <span className="global-subtitle-divider"> | </span>
            <span className="global-subtitle-desc">Xu hướng nhu cầu theo thời gian, địa lý và hình thức làm việc</span>
          </div>
        </div>
        <div className="global-badge-container">
          <div className="dataset-badge">
            <span className="dataset-name">Dataset: vietnam_it_jobs_processed.csv</span>
            <span className="dataset-count">8,452 tin tuyển dụng</span>
          </div>
        </div>
      </div>

      {/* Thanh điều hướng Navigation Tabs */}
      <div className="nav-container">
        <div className="nav-tabs-wrapper">
          <a href="#" className="nav-tab active">01 Xu hướng & Địa lý</a>
          <a href="#" className="nav-tab">02 Kỹ năng & Công nghệ</a>
          <a href="#" className="nav-tab">03 Lương thị trường</a>
          <a href="#" className="nav-tab">04 Nhân sự trẻ</a>
          <a href="#" className="nav-tab">05 AI phân tích</a>
        </div>
      </div>

      {/* Main Content Workspace */}
      <Dashboard />
    </div>
  );
}

export default App;
