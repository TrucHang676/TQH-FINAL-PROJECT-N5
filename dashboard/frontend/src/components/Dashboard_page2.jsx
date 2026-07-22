import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';
import Select from 'react-select';
import KpiCard from './KpiCard';

const Dashboard_page2 = () => {
  // =========================================================================
  // State: Bộ lọc
  // Nguồn dữ liệu thực tế trong CSV: ITviec, TopDev, VietJobs, Vieclam24h, TopCV, JobsGO
  // =========================================================================
  const sourceOptions = ['ITviec', 'TopDev', 'VietJobs', 'Vieclam24h', 'TopCV', 'JobsGO'];

  const [sources, setSources] = useState([...sourceOptions]);
  const [position, setPosition] = useState(null);
  const [experience, setExperience] = useState(null);
  const [region, setRegion] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendMode, setTrendMode] = useState('smoothed'); // 'actual' hoặc 'smoothed'

  // ---- Dropdown options (giống Page 1 nhưng với nhóm vị trí cập nhật) ----
  const positionOptions = [
    { value: 'All', label: 'Tất cả vị trí' },
    { value: 'Software Development', label: 'Software Development' },
    { value: 'AI / ML / Data Science', label: 'AI / ML / Data Science' },
    { value: 'Mobile / Game / Embedded', label: 'Mobile / Game / Embedded' },
    { value: 'Cloud / DevOps / SRE', label: 'Cloud / DevOps / SRE' },
    { value: 'QA / Testing', label: 'QA / Testing' },
    { value: 'Data Engineering / Database', label: 'Data Engineering' },
    { value: 'IT Support / ERP', label: 'IT Support / ERP' },
    { value: 'Management / Architecture', label: 'Management / Architecture' },
    { value: 'Product / Business / UX', label: 'Product / Business / UX' },
    { value: 'Cybersecurity', label: 'Cybersecurity' },
    { value: 'Other', label: 'Khác' },
  ];

  const experienceOptions = [
    { value: 'All', label: 'Tất cả cấp bậc' },
    { value: 'Intern', label: 'Intern' },
    { value: 'Fresher', label: 'Fresher' },
    { value: 'Junior', label: 'Junior' },
    { value: 'Middle', label: 'Middle' },
    { value: 'Senior', label: 'Senior' },
  ];

  const regionOptions = [
    { value: 'All', label: 'Tất cả vùng miền' },
    { value: 'Bắc', label: 'Bắc' },
    { value: 'Trung', label: 'Trung' },
    { value: 'Nam', label: 'Nam' },
    { value: 'Từ xa / Remote', label: 'Từ xa / Remote' },
  ];

  // Set default values khi component mount
  useEffect(() => {
    setPosition(positionOptions[0]);
    setExperience(experienceOptions[0]);
    setRegion(regionOptions[0]);
  }, []);

const page2Cache = new Map();

  // Gọi API khi bộ lọc thay đổi
  useEffect(() => {
    if (!position || !experience || !region) return;
    let isActive = true;

    const cacheKey = JSON.stringify({ sources: [...sources].sort(), position: position.value, experience: experience.value, region: region.value });
    if (page2Cache.has(cacheKey)) {
      setData(page2Cache.get(cacheKey));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.post('http://localhost:8000/api/dashboard/page2', {
          sources,
          position: position.value,
          experience: experience.value,
          region: region.value,
        });
        if (isActive) {
          page2Cache.set(cacheKey, response.data);
          setData(response.data);
        }
      } catch (error) {
        console.error('Error fetching page2 data:', error);
      } finally {
        if (isActive) setLoading(false);
      }
    };

    fetchData();
    return () => { isActive = false; };
  }, [sources, position, experience, region]);

  const handleSourceChange = (val) => {
    setSources(prev =>
      prev.includes(val) ? prev.filter(s => s !== val) : [...prev, val]
    );
  };

  const resetFilters = () => {
    setSources([...sourceOptions]);
    setPosition(positionOptions[0]);
    setExperience(experienceOptions[0]);
    setRegion(regionOptions[0]);
  };

  // Custom styles cho react-select (giống hệt Page 1)
  const customSelectStyles = {
    control: (provided, state) => ({
      ...provided,
      borderColor: state.isFocused ? '#59B292' : '#d1d5db',
      boxShadow: state.isFocused ? '0 0 0 2px rgba(89, 178, 146, 0.2)' : 'none',
      '&:hover': { borderColor: '#59B292', backgroundColor: '#f0faf6' },
      cursor: 'pointer',
      padding: '2px',
      borderRadius: '4px',
      fontSize: '14px',
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected ? '#59B292' : state.isFocused ? '#f0faf6' : 'white',
      color: state.isSelected ? 'white' : '#111827',
      cursor: 'pointer',
      '&:active': { backgroundColor: '#469d7e', color: 'white' },
      fontSize: '14px',
    }),
    menu: (provided) => ({
      ...provided,
      zIndex: 9999,
      borderRadius: '6px',
      boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
    }),
    menuList: (provided) => ({
      ...provided,
      padding: '4px',
      scrollbarWidth: 'thin',
      scrollbarColor: '#59B292 #f0faf6',
    }),
    singleValue: (provided) => ({ ...provided, color: '#111827' }),
  };

  const getFilteredTrendFigure = (figure, mode) => {
    if (!figure || !figure.data) return figure;

    const filteredData = figure.data.map((trace, index) => {
      const isSmoothed = index % 2 === 1;
      const isActive = mode === 'smoothed' ? isSmoothed : !isSmoothed;

      return {
        ...trace,
        visible: isActive,
        showlegend: isActive,
        name: trace.name.replace(' (TB trượt)', '').replace(' (Thực tế)', ''),
        line: {
          ...trace.line,
          width: isActive ? (mode === 'smoothed' ? 3 : 2.5) : trace.line.width
        },
        opacity: isActive ? 1.0 : trace.opacity
      };
    });

    return {
      ...figure,
      data: filteredData
    };
  };

  return (
    <div id="page2-container">
      <div className="workspace">
        {/* ======================== SIDEBAR ======================== */}
        <div className="sidebar">
          <div className="sidebar-title-section">
            <span className="sidebar-title">Bộ lọc</span>
            <button className="btn-reset" onClick={resetFilters}>⟲ Đặt lại</button>
          </div>

          {/* Nguồn tuyển dụng */}
          <div className="filter-group">
            <label className="filter-label">Nguồn tuyển dụng</label>
            <div className="source-checklist" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sourceOptions.map(src => (
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

          {/* Nhóm vị trí */}
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

          {/* Cấp độ kinh nghiệm */}
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

          {/* Vùng miền */}
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

        {/* ======================== MAIN PANEL ======================== */}
        <div className="main-panel">

          {/* ---- KPI ROW ---- */}
          <div className="kpi-row">
            <KpiCard
              title="Kỹ năng công nghệ"
              badge="Unique"
              value={data?.kpi?.total_unique_skills?.toLocaleString() || 0}
              description={`Trên tổng ${data?.kpi?.total_jobs?.toLocaleString() || 0} tin tuyển dụng`}
              tooltip="Tổng số kỹ năng kỹ thuật khác nhau được yêu cầu trong các tin tuyển dụng sau khi áp dụng bộ lọc."
            />

            <KpiCard
              title="Kỹ năng hot nhất"
              badge="#1"
              value={data?.kpi?.top_skill?.name || 'N/A'}
              description={`Xuất hiện trong ${data?.kpi?.top_skill?.count?.toLocaleString() || 0} tin tuyển dụng`}
              tooltip="Kỹ năng công nghệ được yêu cầu nhiều nhất trong toàn bộ tin tuyển dụng được lọc."
            />

            <KpiCard
              title="Nhóm đa dạng nhất"
              badge="Đa năng"
              value={(() => {
                const name = data?.kpi?.most_diverse_position?.name || 'N/A';
                // Rút gọn tên dài
                const shortMap = {
                  'Software Development': 'Software Dev',
                  'AI / ML / Data Science': 'AI / ML',
                  'Mobile / Game / Embedded': 'Mobile / Game',
                  'Cloud / DevOps / SRE': 'Cloud / DevOps',
                  'Data Engineering / Database': 'Data Eng.',
                  'Management / Architecture': 'Management',
                  'Product / Business / UX': 'Product / UX',
                };
                return shortMap[name] || name;
              })()}
              description={`TB ${data?.kpi?.most_diverse_position?.avg_skills?.toFixed(1) || 0} kỹ năng / tin`}
              tooltip="Nhóm vị trí công việc có số lượng kỹ năng yêu cầu trung bình trên mỗi tin tuyển dụng cao nhất."
            />

            <KpiCard
              title="Công nghệ tăng trưởng mạnh"
              badge="Trending"
              value={data?.kpi?.trending_tech?.name || 'N/A'}
              description={`Tăng ${data?.kpi?.trending_tech?.growth_pct > 0 ? '+' : ''}${data?.kpi?.trending_tech?.growth_pct?.toFixed(1) || 0}% gần đây`}
              tooltip="Nhóm công nghệ có tốc độ tăng trưởng nhu cầu tuyển dụng cao nhất so với giai đoạn trước."
            />
          </div>

          {/* ---- CHARTS CONTAINER ---- */}
          <div className="charts-container">

            {/* LEFT: Top 15 Skills (Bar ngang) */}
            <div className="chart-card skills-bar-card">
              <div className="chart-header">
                <span className="chart-title">
                  Top 15 kỹ năng công nghệ được săn đón nhất
                </span>
              </div>
              <div className="chart-content">
                {data?.charts?.top_skills && (
                  <PlotlyChart figure={data.charts.top_skills} />
                )}
              </div>
            </div>

            {/* RIGHT PANEL: Heatmap + Multi-line */}
            <div className="skills-right-panel">

              {/* RIGHT TOP: Heatmap kỹ năng × vị trí */}
              <div className="chart-card heatmap-card">
                <div className="chart-header">
                  <span className="chart-title">
                    Kỹ năng theo nhóm vị trí công việc
                  </span>
                  <span className="chart-subtitle">Top 10 kỹ năng × 6 nhóm vị trí chính</span>
                </div>
                <div className="chart-content">
                  {data?.charts?.heatmap && (
                    <PlotlyChart figure={data.charts.heatmap} />
                  )}
                </div>
              </div>

              {/* RIGHT BOTTOM: Xu hướng công nghệ theo thời gian */}
              <div className="chart-card trend-tech-card">
                <div className="chart-header map-header" style={{ flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', flex: '1', minWidth: '280px' }}>
                    <span className="chart-title">
                      Xu hướng công nghệ mới theo thời gian
                    </span>
                    <span className="chart-subtitle" style={{ marginTop: '4px' }}>
                      {trendMode === 'smoothed' 
                        ? 'Xu hướng: Trung bình trượt 3 tháng giúp lọc biến động ngắn hạn để nhìn rõ xu thế.' 
                        : 'Thực tế: Số liệu gốc ghi nhận hàng tháng, phản ánh chính xác lượng tuyển dụng.'}
                    </span>
                  </div>
                  <div className="toggle-container" style={{ display: 'flex', alignItems: 'center' }}>
                    <div className="toggle-switch" style={{ display: 'flex', gap: '10px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }} className="toggle-label">
                        <input 
                          type="radio" 
                          value="actual" 
                          checked={trendMode === 'actual'} 
                          onChange={(e) => setTrendMode(e.target.value)} 
                        />
                        <span className="radio-label-text">Thực tế</span>
                      </label>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }} className="toggle-label">
                        <input 
                          type="radio" 
                          value="smoothed" 
                          checked={trendMode === 'smoothed'} 
                          onChange={(e) => setTrendMode(e.target.value)} 
                        />
                        <span className="radio-label-text">Xu hướng</span>
                      </label>
                    </div>
                  </div>
                </div>
                <div className="chart-content">
                  {data?.charts?.tech_trend && (
                    <PlotlyChart figure={getFilteredTrendFigure(data.charts.tech_trend, trendMode)} />
                  )}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard_page2;
