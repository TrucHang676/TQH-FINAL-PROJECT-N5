import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';
import Select from 'react-select';
import KpiCard from './KpiCard';

const Dashboard1 = () => {
  // =============================================================================
  // Quản lý trạng thái (State) của các bộ lọc
  // =============================================================================
  const [sources, setSources] = useState(['TopCV', 'VietnamWorks', 'ITviec', 'JobsGO', 'TopDev']);
  const [position, setPosition] = useState(null);
  const [experience, setExperience] = useState(null);
  const [region, setRegion] = useState(null);

  // Trạng thái chuyển đổi chế độ xem bản đồ / biểu đồ cột
  const [mapToggle, setMapToggle] = useState('region_chart');

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

  // Set default values explicitly
  useEffect(() => {
    setPosition(positionOptions[0]);
    setExperience(experienceOptions[0]);
    setRegion(regionOptions[0]);
  }, []);

  const sourceOptions = ['ITviec', 'JobsGO', 'TopCV', 'TopDev', 'VietnamWorks'];

  useEffect(() => {
    if (!position || !experience || !region) return;
    let isActive = true;

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.post('http://localhost:8000/api/dashboard/page1', {
          sources,
          position: position.value,
          experience: experience.value,
          region: region.value
        });
        if (isActive) {
          setData(response.data);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
      if (isActive) {
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      isActive = false;
    };
  }, [sources, position, experience, region]);

  const handleSourceChange = (val) => {
    if (sources.includes(val)) {
      setSources(sources.filter((s) => s !== val));
    } else {
      setSources([...sources, val]);
    }
  };

  const resetFilters = () => {
    setSources(['TopCV', 'VietnamWorks', 'ITviec', 'JobsGO', 'TopDev']);
    setPosition(positionOptions[0]);
    setExperience(experienceOptions[0]);
    setRegion(regionOptions[0]);
    setMapToggle('map');
  };

  // Custom styles for react-select to match the palette
  const customSelectStyles = {
    control: (provided, state) => ({
      ...provided,
      borderColor: state.isFocused ? '#59B292' : '#d1d5db',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(89, 178, 146, 0.2)' : 'none',
      '&:hover': {
        borderColor: '#59B292',
        backgroundColor: '#f0faf6'
      },
      cursor: 'pointer',
      padding: '2px',
      borderRadius: '4px',
      fontSize: '14px',
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected
        ? '#59B292'
        : state.isFocused
          ? '#f0faf6'
          : 'white',
      color: state.isSelected ? 'white' : '#111827',
      cursor: 'pointer',
      '&:active': {
        backgroundColor: '#469d7e',
        color: 'white'
      },
      fontSize: '14px',
    }),
    menu: (provided) => ({
      ...provided,
      zIndex: 9999,
      borderRadius: '6px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    }),
    menuList: (provided) => ({
      ...provided,
      padding: '4px',
      scrollbarWidth: 'thin',
      scrollbarColor: '#59B292 #f0faf6',
      '&::-webkit-scrollbar': {
        width: '6px',
      },
      '&::-webkit-scrollbar-track': {
        background: '#f0faf6',
        borderRadius: '4px',
      },
      '&::-webkit-scrollbar-thumb': {
        background: '#59B292',
        borderRadius: '4px',
      },
      '&::-webkit-scrollbar-thumb:hover': {
        background: '#469d7e',
      },
    }),
    singleValue: (provided) => ({
      ...provided,
      color: '#111827'
    })
  };

  const handleRegionClick = (e) => {
    if (e.points && e.points.length > 0) {
      // For vertical bar chart, x is the label (Region)
      let clickedLabel = e.points[0].x;
      // Also try y if the chart is horizontal
      if (!clickedLabel && e.points[0].y) {
         clickedLabel = e.points[0].y;
      }
      if (!clickedLabel && e.points[0].label) {
         clickedLabel = e.points[0].label;
      }

      if (clickedLabel) {
        // Match with regionOptions
        const matchedRegion = regionOptions.find(r => r.value === clickedLabel || r.label === clickedLabel);
        if (matchedRegion) {
          setRegion(matchedRegion);
        }
      }
    }
  };

  return (
    <div id="page1-container">
      <div className="workspace">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-title-section">
            <span className="sidebar-title">Bộ lọc</span>
            <button className="btn-reset" onClick={resetFilters}>⟲ Đặt lại</button>
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
            <Select
              value={position}
              onChange={setPosition}
              options={positionOptions}
              styles={customSelectStyles}
              isSearchable={false}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">Cấp độ kinh nghiệm</label>
            <Select
              value={experience}
              onChange={setExperience}
              options={experienceOptions}
              styles={customSelectStyles}
              isSearchable={false}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">Vùng miền địa lý</label>
            <Select
              value={region}
              onChange={setRegion}
              options={regionOptions}
              styles={customSelectStyles}
            />
          </div>
        </div>

        {/* Main Panel */}
        <div className="main-panel">
          <div className="kpi-row">
            <KpiCard
              title="Tổng tin tuyển dụng"
              badge="Năm 2024"
              value={data?.kpi?.total_jobs?.toLocaleString() || 0}
              description="Toàn bộ dữ liệu thu thập"
              sparkline={data?.charts?.spark1}
              tooltip="Tổng số tin tuyển dụng IT được thu thập từ tất cả nguồn dữ liệu, sau khi áp dụng các bộ lọc hiện tại."
            />

            <KpiCard
              title="Tháng cao điểm"
              badge="Đỉnh"
              value={data?.kpi?.peak_month?.month || 'N/A'}
              description={`Đạt đỉnh với ${data?.kpi?.peak_month?.count?.toLocaleString() || 0} tin`}
              sparkline={data?.charts?.spark2}
              tooltip="Tháng ghi nhận số lượng tin tuyển dụng cao nhất trong toàn bộ giai đoạn dữ liệu."
            />

            <KpiCard
              title="Địa bàn lớn nhất"
              badge="Hot"
              value={data?.kpi?.top_city?.city || 'N/A'}
              description={`Chiếm ${data?.kpi?.top_city?.pct?.toFixed(1) || 0}% toàn quốc`}
              sparkline={data?.charts?.spark3}
              tooltip="Tỉnh/thành phố có nhu cầu tuyển dụng IT cao nhất, được tính theo tỉ lệ phần trăm so với tổng cả nước."
            />

            <KpiCard
              title="Hình thức chủ đạo"
              badge="Phổ biến"
              value={data?.kpi?.top_work?.work || 'N/A'}
              description={`Chiếm ${data?.kpi?.top_work?.pct?.toFixed(1) || 0}% tổng thể`}
              sparkline={data?.charts?.spark4}
              tooltip="Hình thức làm việc được đăng tuyển nhiều nhất, phản ánh xu hướng tuyển dụng chủ đạo của thị trường IT hiện tại."
            />
          </div>

          <div className="charts-container">
            {/* Left map */}
            <div className="chart-card map-card">
              <div className="chart-header map-header">
                <span className="chart-title">
                  {mapToggle === 'map' ? 'Bản đồ phân bố tuyển dụng' : 'Biểu đồ phân bố tuyển dụng'}
                </span>
                <div className="toggle-container">
                  <div className="toggle-switch" style={{ display: 'flex', gap: '10px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="region_chart" checked={mapToggle === 'region_chart'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Theo vùng</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="map" checked={mapToggle === 'map'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Bản đồ</span>
                    </label>
                  </div>
                </div>
              </div>
              <div className="chart-content" style={{ position: 'relative' }}>
                {/* Geographic Map */}
                {mapToggle === 'map' && data?.charts?.map && (
                  <PlotlyChart key="map-view" figure={data.charts.map} />
                )}

                {/* Vertical Region Bar Chart */}
                {mapToggle === 'region_chart' && data?.charts?.region_chart && (
                  <PlotlyChart key="region-view" figure={data.charts.region_chart} onChartClick={handleRegionClick} />
                )}

                {/* Floating Widgets on Left and Right of Vietnam Map */}
                {mapToggle === 'map' && data?.regions && (
                  <>
                    {/* Left overlay for Remote / Other jobs */}
                    <div className="map-overlay-box overlay-left">
                      <div className="overlay-box-title">Ngoài địa lý cụ thể</div>
                      <div className="overlay-item">
                        <span className="overlay-dot" style={{ backgroundColor: '#0d9488' }}></span>
                        <span className="overlay-label">Từ xa / Remote:</span>
                        <span className="overlay-val-bold">{data.regions['Từ xa / Remote']?.toLocaleString() || 0} tin</span>
                      </div>
                      <div className="overlay-item">
                        <span className="overlay-dot" style={{ backgroundColor: '#9ca3af' }}></span>
                        <span className="overlay-label">Khác / Không rõ:</span>
                        <span className="overlay-val-bold">{data.regions['Khác']?.toLocaleString() || 0} tin</span>
                      </div>
                    </div>

                    {/* Right overlay for region breakdown */}
                    <div className="map-overlay-box overlay-right">
                      <div className="overlay-box-title">Thống kê theo 3 Miền</div>
                      <div className="overlay-item">
                        <span className="overlay-dot" style={{ backgroundColor: '#FA6781' }}></span>
                        <span className="overlay-label">Miền Bắc:</span>
                        <span className="overlay-val-bold">
                          {data.regions['Bắc']?.toLocaleString() || 0} tin ({((data.regions['Bắc'] / (data.kpi?.total_jobs || 1)) * 100).toFixed(1)}%)
                        </span>
                      </div>
                      <div className="overlay-item">
                        <span className="overlay-dot" style={{ backgroundColor: '#FFC94D' }}></span>
                        <span className="overlay-label">Miền Trung:</span>
                        <span className="overlay-val-bold">
                          {data.regions['Trung']?.toLocaleString() || 0} tin ({((data.regions['Trung'] / (data.kpi?.total_jobs || 1)) * 100).toFixed(1)}%)
                        </span>
                      </div>
                      <div className="overlay-item">
                        <span className="overlay-dot" style={{ backgroundColor: '#59B292' }}></span>
                        <span className="overlay-label">Miền Nam:</span>
                        <span className="overlay-val-bold">
                          {data.regions['Nam']?.toLocaleString() || 0} tin ({((data.regions['Nam'] / (data.kpi?.total_jobs || 1)) * 100).toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </div>
              {mapToggle === 'map' && (
                <div className="chart-caption">{data?.caption || ''}</div>
              )}
            </div>

            {/* Right Panel */}
            <div className="charts-right-panel">
              <div className="chart-card trend-card">
                <div className="chart-header">
                  <span className="chart-title">
                    Xu hướng tuyển dụng theo tháng
                  </span>
                </div>
                <div className="chart-content">
                  {data?.charts?.trend && <PlotlyChart figure={data.charts.trend} />}
                </div>
              </div>

              <div className="split-row">
                <div className="chart-card donut-card">
                  <div className="chart-header">
                    <span className="chart-title">
                      Hình thức làm việc chủ đạo
                    </span>
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
