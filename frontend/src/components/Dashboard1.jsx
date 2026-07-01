import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';

const Dashboard1 = () => {
  // =============================================================================
  // Quản lý trạng thái (State) của các bộ lọc
  // =============================================================================
  const [sources, setSources] = useState(['TopCV', 'VietnamWorks', 'ITviec', 'JobsGO', 'TopDev']);
  const [position, setPosition] = useState('All');
  const [experience, setExperience] = useState('All');
  const [region, setRegion] = useState('All');
  
  // Trạng thái chuyển đổi chế độ xem bản đồ / biểu đồ cột
  const [mapToggle, setMapToggle] = useState('map');

  // =============================================================================
  // Quản lý trạng thái dữ liệu trả về từ API và trạng thái tải (Loading)
  // =============================================================================
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Thêm đầy đủ options từ file page1.py cũ
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
    { value: 'Intern', label: 'Intern' },
    { value: 'Fresher', label: 'Fresher' },
    { value: 'Junior', label: 'Junior' },
    { value: 'Middle', label: 'Middle' },
    { value: 'Senior', label: 'Senior' },
    { value: 'Không rõ', label: 'Không rõ' }
  ];

  const regionOptions = [
    { value: 'All', label: 'Tất cả vùng miền' },
    { value: 'Bắc', label: 'Bắc' },
    { value: 'Trung', label: 'Trung' },
    { value: 'Nam', label: 'Nam' },
    { value: 'Từ xa / Remote', label: 'Từ xa / Remote' }
  ];

  const sourceOptions = ['ITviec', 'JobsGO', 'TopCV', 'TopDev', 'VietnamWorks'];

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
    setSources(['TopCV', 'VietnamWorks', 'ITviec', 'JobsGO', 'TopDev']);
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
            <span className="sidebar-title">Bộ lọc</span>
            <button className="btn-reset" onClick={resetFilters}>Đặt lại</button>
          </div>

          <div className="filter-group">
            <label className="filter-label">Nguồn tuyển dụng</label>
            <div className="source-checklist" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sourceOptions.map((src) => (
                <label key={src} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={sources.includes(src)}
                    onChange={() => handleSourceChange(src)}
                  />
                  <span>{src}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Nhóm vị trí công việc</label>
            <select
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', backgroundColor: 'white' }}
            >
              {positionOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Cấp độ kinh nghiệm</label>
            <select
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', backgroundColor: 'white' }}
            >
              {experienceOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Vùng miền địa lý</label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', backgroundColor: 'white' }}
            >
              {regionOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Main Panel */}
        <div className="main-panel">
          <div className="kpi-row">
            {/* KPI 1 */}
            <div className="kpi-card">
              <div className="kpi-card-info">
                <div className="kpi-header">
                  <span className="kpi-title">Tổng tin tuyển dụng</span>
                  <span className="kpi-badge">Năm 2024</span>
                </div>
                <div className="kpi-body">
                  <div className="kpi-main-val">{data?.kpi?.total_jobs?.toLocaleString() || 0}</div>
                  <div className="kpi-desc">Toàn bộ dữ liệu thu thập</div>
                  {data?.charts?.spark1 && <div style={{ height: '40px', marginTop: '4px' }}><PlotlyChart figure={data.charts.spark1} /></div>}
                </div>
              </div>
            </div>

            {/* KPI 2 */}
            <div className="kpi-card">
              <div className="kpi-card-info">
                <div className="kpi-header">
                  <span className="kpi-title">Tháng cao điểm</span>
                  <span className="kpi-badge">Đỉnh</span>
                </div>
                <div className="kpi-body">
                  <div className="kpi-main-val">{data?.kpi?.peak_month?.month || 'N/A'}</div>
                  <div className="kpi-desc">Đạt đỉnh với {data?.kpi?.peak_month?.count?.toLocaleString() || 0} tin</div>
                  {data?.charts?.spark2 && <div style={{ height: '40px', marginTop: '4px' }}><PlotlyChart figure={data.charts.spark2} /></div>}
                </div>
              </div>
            </div>

            {/* KPI 3 */}
            <div className="kpi-card">
              <div className="kpi-card-info">
                <div className="kpi-header">
                  <span className="kpi-title">Địa bàn lớn nhất</span>
                  <span className="kpi-badge">Hot</span>
                </div>
                <div className="kpi-body">
                  <div className="kpi-main-val">{data?.kpi?.top_city?.city || 'N/A'}</div>
                  <div className="kpi-desc">Chiếm {data?.kpi?.top_city?.pct?.toFixed(1) || 0}% toàn quốc</div>
                  {data?.charts?.spark3 && <div style={{ height: '40px', marginTop: '4px' }}><PlotlyChart figure={data.charts.spark3} /></div>}
                </div>
              </div>
            </div>

            {/* KPI 4 */}
            <div className="kpi-card">
              <div className="kpi-card-info">
                <div className="kpi-header">
                  <span className="kpi-title">Hình thức chủ đạo</span>
                  <span className="kpi-badge">Phổ biến</span>
                </div>
                <div className="kpi-body">
                  <div className="kpi-main-val">{data?.kpi?.top_work?.work || 'N/A'}</div>
                  <div className="kpi-desc">Chiếm {data?.kpi?.top_work?.pct?.toFixed(1) || 0}% tổng thể</div>
                  {data?.charts?.spark4 && <div style={{ height: '40px', marginTop: '4px' }}><PlotlyChart figure={data.charts.spark4} /></div>}
                </div>
              </div>
            </div>
          </div>

          <div className="charts-container">
            {/* Left map */}
            <div className="chart-card map-card">
              <div className="chart-header map-header">
                <div>
                  <span className="chart-title">
                    <span className="chart-title-num">01</span> Bản đồ phân bố tuyển dụng
                  </span><br/>
                  <span className="chart-subtitle">Bản đồ phân bố địa lý Việt Nam</span>
                </div>
                <div className="toggle-container">
                  <div className="toggle-switch" style={{ display: 'flex', gap: '10px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="map" checked={mapToggle === 'map'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Bản đồ</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="region_chart" checked={mapToggle === 'region_chart'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Theo vùng</span>
                    </label>
                  </div>
                </div>
              </div>
              <div className="chart-content">
                {data?.charts?.map && <PlotlyChart figure={data.charts.map} />}
              </div>
              <div className="chart-caption">{data?.caption || ''}</div>
            </div>

            {/* Right Panel */}
            <div className="charts-right-panel">
              <div className="chart-card trend-card">
                <div className="chart-header">
                  <span className="chart-title">
                    <span className="chart-title-num">02</span> Xu hướng tuyển dụng theo tháng
                  </span><br/>
                  <span className="chart-subtitle">Số lượng tin tuyển dụng IT theo thời gian</span>
                </div>
                <div className="chart-content">
                  {data?.charts?.trend && <PlotlyChart figure={data.charts.trend} />}
                </div>
                <div className="chart-caption">Biểu đồ thời gian chỉ tính các tin có thang_dang.</div>
              </div>

              <div className="split-row">
                <div className="chart-card donut-card">
                  <div className="chart-header">
                    <span className="chart-title">
                      <span className="chart-title-num">03</span> Hình thức làm việc chủ đạo
                    </span><br/>
                    <span className="chart-subtitle">Tỷ lệ hình thức làm việc tuyển dụng</span>
                  </div>
                  <div className="chart-content">
                    {data?.charts?.work && <PlotlyChart figure={data.charts.work} />}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard1;
