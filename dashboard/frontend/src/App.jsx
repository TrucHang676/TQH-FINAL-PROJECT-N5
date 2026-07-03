import React, { useState } from 'react';
import Dashboard1 from './components/Dashboard_page1';
import Dashboard2 from './components/Dashboard_page2';
import Dashboard3 from './components/Dashboard_page3';
import Dashboard4 from './components/Dashboard_page4';
import Dashboard5 from './components/Dashboard_page5';

// Import CSS y hệt như cấu trúc của Dash
import './styles/style.css';
import './styles/style_page1.css';
import './styles/style_page2.css';

const tabConfig = {
  1: {
    goal: 'Mục tiêu 1',
    desc: 'Tổng quan nhu cầu tuyển dụng IT tại Việt Nam theo thời gian, địa lý và hình thức làm việc'
  },
  2: {
    goal: 'Mục tiêu 2',
    desc: 'Phân tích kỹ năng phổ biến, ngôn ngữ lập trình và xu hướng công nghệ tuyển dụng'
  },
  3: {
    goal: 'Mục tiêu 3',
    desc: 'Phân tích cơ cấu mức lương theo vị trí tuyển dụng, kinh nghiệm và địa lý'
  },
  4: {
    goal: 'Mục tiêu 4',
    desc: 'Thống kê cơ hội tuyển dụng cho sinh viên, Intern, Fresher và cơ hội nghề nghiệp trẻ'
  },
  5: {
    goal: 'Mục tiêu 5',
    desc: 'AI phân tích sâu dữ liệu tuyển dụng và đề xuất định hướng lộ trình nghề nghiệp'
  }
};

function App() {
  const [activeTab, setActiveTab] = useState(1);

  return (
    // Bọc toàn bộ ứng dụng trong một thẻ div chung, không dùng id page1-container ở đây
    <div className="app-wrapper" style={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column' }}>
      {/* Cấu trúc Header toàn cục chuẩn xác từ app.py */}
      <div className="global-header">
        <div className="global-title-container">
          <h1 className="global-title">Thị trường tuyển dụng IT Việt Nam</h1>
          <div className="global-subtitle-container">
            {activeTab !== 5 && (
              <span className="goal-badge">
                {tabConfig[activeTab].goal}
              </span>
            )}
            <span className="global-subtitle-desc">{tabConfig[activeTab].desc}</span>
          </div>
        </div>
        <div className="global-badge-container">
          <div className="dataset-badge">
            <span className="dataset-name">vietnam_it_jobs_processed.csv</span>
            <span className="dataset-count">8,452 bản ghi</span>
          </div>
        </div>
      </div>

      {/* Thanh điều hướng Navigation Tabs */}
      <div className="nav-container">
        <div className="nav-tabs-wrapper">
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab(1); }} className={`nav-tab ${activeTab === 1 ? 'active' : ''}`}>01 Xu hướng & Địa lý</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab(2); }} className={`nav-tab ${activeTab === 2 ? 'active' : ''}`}>02 Kỹ năng & Công nghệ</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab(3); }} className={`nav-tab ${activeTab === 3 ? 'active' : ''}`}>03 Lương thị trường</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab(4); }} className={`nav-tab ${activeTab === 4 ? 'active' : ''}`}>04 Nhân sự trẻ</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab(5); }} className={`nav-tab ${activeTab === 5 ? 'active' : ''}`}>05 AI phân tích</a>
        </div>
      </div>

      {/* Nội dung chính của trang (Render theo tab hiện tại) */}
      <div className="tab-content-container" style={{ flex: 1, overflowY: 'auto' }}>
        {activeTab === 1 && <Dashboard1 />}
        {activeTab === 2 && <Dashboard2 />}
        {activeTab === 3 && <Dashboard3 />}
        {activeTab === 4 && <Dashboard4 />}
        {activeTab === 5 && <Dashboard5 />}
      </div>
    </div>
  );
}

export default App;
