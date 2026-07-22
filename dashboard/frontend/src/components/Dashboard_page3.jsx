import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';
import Select from 'react-select';
import KpiCard from './KpiCard';

const Dashboard_page3 = () => {
  // =========================================================================
  // State: Bộ lọc (giống hệt Page 1 & 2)
  // =========================================================================
  const sourceOptions = ['ITviec', 'TopDev', 'VietJobs', 'Vieclam24h', 'TopCV', 'JobsGO'];

  const [sources, setSources] = useState([...sourceOptions]);
  const [position, setPosition] = useState(null);
  const [experience, setExperience] = useState(null);
  const [region, setRegion] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // ---- Dropdown options (giống Page 2) ----
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
    { value: 'Không rõ', label: 'Không rõ' },
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

const page3Cache = new Map();

  // Gọi API khi bộ lọc thay đổi
  useEffect(() => {
    if (!position || !experience || !region) return;
    let isActive = true;

    const cacheKey = JSON.stringify({ sources: [...sources].sort(), position: position.value, experience: experience.value, region: region.value });
    if (page3Cache.has(cacheKey)) {
      setData(page3Cache.get(cacheKey));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.post('http://localhost:8000/api/dashboard/page3', {
          sources,
          position: position.value,
          experience: experience.value,
          region: region.value,
        });
        if (isActive) {
          page3Cache.set(cacheKey, response.data);
          setData(response.data);
        }
      } catch (error) {
        console.error('Error fetching page3 data:', error);
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

  // Custom styles cho react-select (giống hệt Page 1 & 2)
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

  return (
    <div id="page3-container">
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
              title="Lương TB ngành IT"
              badge="Trung bình"
              value={data?.kpi?.avg_salary ? `${data.kpi.avg_salary} triệu` : '0'}
              description={`Từ ${data?.kpi?.total_with_salary?.toLocaleString() || 0} tin có công khai lương`}
              tooltip="Mức lương trung bình tính từ tất cả các tin tuyển dụng có công khai khoảng lương, sau khi áp dụng bộ lọc."
            />

            <KpiCard
              title="Tỷ lệ công khai lương"
              badge="Minh bạch"
              value={data?.kpi?.salary_disclosure_pct ? `${data.kpi.salary_disclosure_pct}%` : '0%'}
              description={`${data?.kpi?.total_with_salary?.toLocaleString() || 0} / ${data?.kpi?.total_jobs?.toLocaleString() || 0} tin tuyển dụng`}
              tooltip="Tỷ lệ phần trăm số tin tuyển dụng có đăng khoảng lương cụ thể, phản ánh mức độ minh bạch của thị trường."
            />

            <KpiCard
              title="Vị trí lương cao nhất"
              badge="Top"
              value={(() => {
                const name = data?.kpi?.top_salary_position?.name || 'N/A';
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
              description={`Trung bình ${data?.kpi?.top_salary_position?.value || 0} triệu VNĐ`}
              tooltip="Nhóm vị trí công việc có mức lương trung bình cao nhất trong các tin tuyển dụng đã lọc."
            />

            <KpiCard
              title="Khoảng cách lương"
              badge="Gap"
              value={data?.kpi?.salary_gap?.ratio ? `${data.kpi.salary_gap.ratio} lần` : 'N/A'}
              description={data?.kpi?.salary_gap?.description || 'N/A'}
              tooltip="Tỷ số giữa lương TB của cấp kinh nghiệm cao nhất và thấp nhất (loại trừ 'Không rõ'), thể hiện mức chênh lệch lương theo thâm niên."
            />
          </div>

          {/* ---- CHARTS CONTAINER ---- */}
          <div className="charts-container">

            {/* LEFT: Biểu đồ 1 - Phân bố lương (Histogram) */}
            <div className="chart-card salary-dist-card">
              <div className="chart-header">
                <span className="chart-title">
                  Phân bố mức lương trung bình
                </span>
              </div>
              <div className="chart-content">
                {data?.charts?.salary_distribution && (
                  <PlotlyChart key="dist-histogram" figure={data.charts.salary_distribution} />
                )}
              </div>
            </div>

            {/* RIGHT PANEL: 2 biểu đồ xếp dọc */}
            <div className="salary-right-panel">

              {/* RIGHT TOP: Biểu đồ 2 - Lương theo Vị trí & Kinh nghiệm */}
              <div className="chart-card salary-pos-exp-card">
                <div className="chart-header">
                  <span className="chart-title">
                    Lương theo Vị trí & Kinh nghiệm
                  </span>
                </div>
                <div className="chart-content">
                  {data?.charts?.salary_by_position_experience && (
                    <PlotlyChart figure={data.charts.salary_by_position_experience} />
                  )}
                </div>
              </div>

              {/* RIGHT BOTTOM: Biểu đồ 3 - Lương theo Khu vực & Remote */}
              <div className="chart-card salary-location-card">
                <div className="chart-header">
                  <span className="chart-title">
                    Lương theo Khu vực & Remote
                  </span>
                  <span className="chart-subtitle">Hà Nội, TP.HCM, Đà Nẵng & Remote</span>
                </div>
                <div className="chart-content">
                  {data?.charts?.salary_by_location && (
                    <PlotlyChart figure={data.charts.salary_by_location} />
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

export default Dashboard_page3;
