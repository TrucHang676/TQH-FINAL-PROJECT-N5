import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';

const Dashboard = () => {
  const [sources, setSources] = useState(['TopCV', 'VietnamWorks', 'ITviec']);
  const [position, setPosition] = useState('All');
  const [experience, setExperience] = useState('All');
  const [region, setRegion] = useState('All');
  const [mapToggle, setMapToggle] = useState('map');

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const positionOptions = [
    { value: 'All', label: 'Tất cả vị trí' },
    { value: 'Backend', label: 'Backend' },
    { value: 'Frontend', label: 'Frontend' },
    { value: 'Fullstack', label: 'Fullstack' },
    { value: 'Mobile', label: 'Mobile' },
    { value: 'Data', label: 'Data' },
    { value: 'DevOps/System', label: 'DevOps/System' },
    { value: 'Tester/QA/QC', label: 'Tester/QA/QC' },
    { value: 'Manager/Leader', label: 'Manager/Leader' },
    { value: 'Security', label: 'Security' },
    { value: 'BA', label: 'Business Analyst' },
    { value: 'Khác', label: 'Khác' }
  ];

  const experienceOptions = [
    { value: 'All', label: 'Tất cả cấp bậc' },
    { value: 'Không yêu cầu kinh nghiệm', label: 'Không yêu cầu kinh nghiệm' },
    { value: 'Dưới 1 năm', label: 'Dưới 1 năm' },
    { value: '1 - 3 năm', label: '1 - 3 năm' },
    { value: '3 - 5 năm', label: '3 - 5 năm' },
    { value: 'Trên 5 năm', label: 'Trên 5 năm' }
  ];

  const regionOptions = [
    { value: 'All', label: 'Tất cả vùng miền' },
    { value: 'Bắc', label: 'Miền Bắc' },
    { value: 'Trung', label: 'Miền Trung' },
    { value: 'Nam', label: 'Miền Nam' },
    { value: 'Từ xa / Remote', label: 'Từ xa / Remote' }
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/dashboard/page1', {
        sources,
        position,
        experience,
        region,
        map_toggle: mapToggle
      });
      setData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [sources, position, experience, region, mapToggle]);

  const handleSourceChange = (val) => {
    if (sources.includes(val)) {
      setSources(sources.filter((s) => s !== val));
    } else {
      setSources([...sources, val]);
    }
  };

  const resetFilters = () => {
    setSources(['TopCV', 'VietnamWorks', 'ITviec']);
    setPosition('All');
    setExperience('All');
    setRegion('All');
    setMapToggle('map');
  };

  return (
    <div id="page1-container">
      <div className="workspace">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-title-section">
            <span className="sidebar-title">BỘ LỌC DỮ LIỆU</span>
            <button className="btn-reset" onClick={resetFilters}>⟳ Đặt lại</button>
          </div>

          <div className="filter-group">
            <div className="filter-label">Nguồn tuyển dụng</div>
            <div className="source-checklist">
              {['TopCV', 'VietnamWorks', 'ITviec'].map((src) => (
                <label key={src} style={{ display: 'block', marginBottom: '8px' }}>
                  <input
                    type="checkbox"
                    checked={sources.includes(src)}
                    onChange={() => handleSourceChange(src)}
                    style={{ marginRight: '8px' }}
                  />
                  {src}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <div className="filter-label">Nhóm vị trí</div>
            <select
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              className="form-control"
              style={{ width: '100%', padding: '8px', border: '1px solid #eae5db', borderRadius: '4px' }}
            >
              {positionOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <div className="filter-label">Kinh nghiệm</div>
            <select
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
              className="form-control"
              style={{ width: '100%', padding: '8px', border: '1px solid #eae5db', borderRadius: '4px' }}
            >
              {experienceOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <div className="filter-label">Vùng miền</div>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="form-control"
              style={{ width: '100%', padding: '8px', border: '1px solid #eae5db', borderRadius: '4px' }}
            >
              {regionOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Main Panel */}
        <div className="main-panel">
          {/* KPIs */}
          <div className="kpi-row">
            <div className="kpi-card">
              <div className="kpi-title">Tổng Tin Tuyển Dụng</div>
              <div className="kpi-val-container">
                <div className="kpi-main-val">{data?.kpi?.total_jobs?.toLocaleString() || 0}</div>
                <div className="kpi-desc">Toàn bộ dữ liệu thu thập</div>
                <div style={{ height: '40px', marginTop: '4px' }}>
                  {data?.charts?.spark1 && <PlotlyChart figure={data.charts.spark1} />}
                </div>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-title">Tháng Cao Điểm</div>
              <div className="kpi-val-container">
                <div className="kpi-main-val">{data?.kpi?.peak_month?.month || 'N/A'}</div>
                <div className="kpi-desc">Đạt đỉnh với {data?.kpi?.peak_month?.count?.toLocaleString() || 0} tin</div>
                <div style={{ height: '40px', marginTop: '4px' }}>
                  {data?.charts?.spark2 && <PlotlyChart figure={data.charts.spark2} />}
                </div>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-title">Địa Bàn Đứng Đầu</div>
              <div className="kpi-val-container">
                <div className="kpi-main-val">{data?.kpi?.top_city?.city || 'N/A'}</div>
                <div className="kpi-desc">Chiếm {data?.kpi?.top_city?.pct?.toFixed(1) || 0}% toàn quốc</div>
                <div style={{ height: '40px', marginTop: '4px' }}>
                  {data?.charts?.spark3 && <PlotlyChart figure={data.charts.spark3} />}
                </div>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-title">Hình Thức Phổ Biến Nhất</div>
              <div className="kpi-val-container">
                <div className="kpi-main-val">{data?.kpi?.top_work?.work || 'N/A'}</div>
                <div className="kpi-desc">Chiếm {data?.kpi?.top_work?.pct?.toFixed(1) || 0}% toàn quốc</div>
                <div style={{ height: '40px', marginTop: '4px' }}>
                  {data?.charts?.spark4 && <PlotlyChart figure={data.charts.spark4} />}
                </div>
              </div>
            </div>
          </div>

          {/* Insights (Optional) */}
          <div className="insights-strip">
            <div className="insight-item">💡 Khám phá xu hướng tuyển dụng dựa trên dữ liệu thực tế tại thị trường IT Việt Nam.</div>
          </div>

          {/* Charts Container */}
          <div className="charts-container" style={{ display: 'flex', gap: '16px', flex: 1, overflow: 'hidden' }}>
            
            {/* Map Card */}
            <div className="chart-card map-card" style={{ flex: '1.2', display: 'flex', flexDirection: 'column' }}>
              <div className="chart-header map-header">
                <div>
                  <span className="chart-title"><span className="chart-title-num">01</span>Phân bố địa lý</span><br/>
                  <span className="chart-subtitle">So sánh mật độ tuyển dụng giữa các địa bàn</span>
                </div>
                <div className="toggle-container">
                  <div className="toggle-switch" style={{ display: 'flex', gap: '8px' }}>
                    <label>
                      <input type="radio" value="map" checked={mapToggle === 'map'} onChange={(e) => setMapToggle(e.target.value)} /> Bản đồ
                    </label>
                    <label>
                      <input type="radio" value="region_chart" checked={mapToggle === 'region_chart'} onChange={(e) => setMapToggle(e.target.value)} /> Theo vùng
                    </label>
                  </div>
                </div>
              </div>
              <div className="chart-content" style={{ flex: 1 }}>
                {loading ? <div>Đang tải...</div> : data?.charts?.map && <PlotlyChart figure={data.charts.map} />}
              </div>
              <div className="chart-caption">{data?.caption || ''}</div>
            </div>

            {/* Right Panel */}
            <div className="charts-right-panel" style={{ flex: '0.8', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              
              <div className="chart-card trend-card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div className="chart-header">
                  <span className="chart-title"><span className="chart-title-num">02</span>Xu hướng tuyển dụng</span><br/>
                  <span className="chart-subtitle">Lưu lượng tin đăng theo thời gian</span>
                </div>
                <div className="chart-content" style={{ flex: 1 }}>
                  {loading ? <div>Đang tải...</div> : data?.charts?.trend && <PlotlyChart figure={data.charts.trend} />}
                </div>
              </div>

              <div className="chart-card donut-card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div className="chart-header">
                  <span className="chart-title"><span className="chart-title-num">03</span>Hình thức làm việc chủ đạo</span><br/>
                  <span className="chart-subtitle">Tỷ lệ hình thức làm việc tuyển dụng</span>
                </div>
                <div className="chart-content" style={{ flex: 1 }}>
                  {loading ? <div>Đang tải...</div> : data?.charts?.work && <PlotlyChart figure={data.charts.work} />}
                </div>
              </div>

            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
