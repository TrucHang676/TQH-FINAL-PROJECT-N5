import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';
import Select from 'react-select';
import KpiCard from './KpiCard';

const page4Cache = new Map();

const Dashboard_page4 = () => {
  // =========================================================================
  // State: Bộ lọc
  // Nguồn dữ liệu thực tế trong CSV: ITviec, TopDev, VietJobs, Vieclam24h, TopCV, JobsGO
  // =========================================================================
  const sourceOptions = ['ITviec', 'TopDev', 'VietJobs', 'Vieclam24h', 'TopCV', 'JobsGO'];

  const [sources, setSources] = useState([...sourceOptions]);
  const [region, setRegion] = useState(null);
  const [position, setPosition] = useState(null);
  const [workType, setWorkType] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Giá trị thực trong cột vung_mien của CSV: Bắc, Trung, Nam, Khác
  const regionOptions = [
    { value: 'All', label: 'Tất cả vùng miền' },
    { value: 'Bắc', label: 'Bắc' },
    { value: 'Trung', label: 'Trung' },
    { value: 'Nam', label: 'Nam' },
    { value: 'Khác', label: 'Khác' },
  ];

  // Danh sách nhóm vị trí thật trong cột nhom_vi_tri (đồng bộ với trang 2)
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
  ];

  // Giá trị thực trong cột hinh_thuc_lam_viec — Internship đặc biệt hữu ích cho trang này
  const workTypeOptions = [
    { value: 'All', label: 'Tất cả hình thức' },
    { value: 'Full-time', label: 'Full-time' },
    { value: 'Internship', label: 'Internship' },
    { value: 'Part-time', label: 'Part-time' },
    { value: 'Contract', label: 'Contract' },
    { value: 'Khác', label: 'Khác' },
  ];

  // Set default values khi component mount
  useEffect(() => {
    setRegion(regionOptions[0]);
    setPosition(positionOptions[0]);
    setWorkType(workTypeOptions[0]);
  }, []);

  // Gọi API khi bộ lọc thay đổi
  useEffect(() => {
    if (!region || !position || !workType) return;
    let isActive = true;

    const cacheKey = JSON.stringify({ sources: [...sources].sort(), region: region.value, position: position.value, work_type: workType.value });
    if (page4Cache.has(cacheKey)) {
      setData(page4Cache.get(cacheKey));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.post('http://localhost:8000/api/dashboard/page4', {
          sources,
          region: region.value,
          position: position.value,
          work_type: workType.value,
        });
        if (isActive) {
          page4Cache.set(cacheKey, response.data);
          setData(response.data);
        }
      } catch (error) {
        console.error('Error fetching page4 data:', error);
      } finally {
        if (isActive) setLoading(false);
      }
    };

    fetchData();
    return () => { isActive = false; };
  }, [sources, region, position, workType]);

  const handleSourceChange = (val) => {
    setSources(prev =>
      prev.includes(val) ? prev.filter(s => s !== val) : [...prev, val]
    );
  };

  const handleTreemapClick = (event) => {
    if (!event || !event.points || !event.points[0]) return;
    const point = event.points[0];
    const rawLabel = point.label || point.hovertext || point.customdata;
    if (rawLabel) {
      const cleanText = String(rawLabel).replace(/<[^>]*>/g, '').split('\n')[0].trim();
      const matchedOption = positionOptions.find(
        opt => opt.value !== 'All' && (opt.value === cleanText || opt.label === cleanText || cleanText.includes(opt.value))
      );
      if (matchedOption) {
        // NẾU Ô NÀY ĐANG ĐƯỢC CHỌN -> BẤM LẠI SẼ HỦY LỌC (QUAY VỀ BIỂU ĐỒ GỐC)!
        if (position?.value === matchedOption.value) {
          setPosition(positionOptions[0]);
        } else {
          setPosition(matchedOption);
        }
      } else {
        // Bấm ngoài ô hoặc ô tổng -> Quay về biểu đồ gốc
        setPosition(positionOptions[0]);
      }
    }
  };

  const resetFilters = () => {
    setSources([...sourceOptions]);
    setRegion(regionOptions[0]);
    setPosition(positionOptions[0]);
    setWorkType(workTypeOptions[0]);
  };

  // Custom styles cho react-select (giống hệt các trang khác)
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
    <div id="page4-container">
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

          {/* Hình thức làm việc */}
          <div className="filter-group">
            <label className="filter-label">Hình thức làm việc</label>
            <Select
              value={workType}
              onChange={setWorkType}
              options={workTypeOptions}
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
              title="Tổng tin tuyển dụng"
              badge="Đã lọc"
              value={data?.kpi?.total_jobs?.toLocaleString() || 0}
              description="Theo bộ lọc hiện tại"
              tooltip="Tổng số tin tuyển dụng sau khi áp dụng bộ lọc nguồn và vùng miền."
            />

            <KpiCard
              title="Cơ hội cho nhân sự trẻ"
              badge="Intern/Fresher/Junior"
              value={`${data?.kpi?.young_pct?.toFixed(1) || 0}%`}
              description={`${data?.kpi?.total_young_jobs?.toLocaleString() || 0} tin trong số tin có ghi rõ cấp bậc`}
              tooltip="Tỷ lệ tin tuyển dụng dành cho Intern/Fresher/Junior, tính trên các tin có ghi rõ cấp độ kinh nghiệm (đã loại tin 'Không rõ')."
            />

            <KpiCard
              title="Nhóm vị trí cởi mở nhất"
              badge="Dễ xin nhất"
              value={(() => {
                const name = data?.kpi?.most_open_group?.name || 'N/A';
                const shortMap = {
                  'Software Development': 'Software Dev',
                  'AI / ML / Data Science': 'AI / ML',
                  'Mobile / Game / Embedded': 'Mobile / Game',
                  'Cloud / DevOps / SRE': 'Cloud / DevOps',
                  'Data Engineering / Database': 'Data Eng.',
                  'Management / Architecture': 'Management',
                  'Product / Business / UX': 'Product / UX',
                  'IT Support / ERP': 'IT Support',
                };
                return shortMap[name] || name;
              })()}
              description={`${data?.kpi?.most_open_group?.pct?.toFixed(1) || 0}% tin dành cho nhân sự trẻ`}
              tooltip="Nhóm vị trí công việc có tỷ lệ tin tuyển dụng dành cho Intern/Fresher/Junior cao nhất (trong các nhóm có đủ mẫu thống kê)."
            />

            <KpiCard
              title="Lương khởi điểm Fresher"
              badge="Trung vị"
              value={`${data?.kpi?.fresher_median_salary?.toFixed(1) || 0} tr`}
              description="Lương trung bình / tháng (VNĐ)"
              tooltip="Mức lương trung vị (median) của các tin tuyển dụng Fresher có công khai khoảng lương, sau khi áp dụng bộ lọc."
            />
          </div>

          {/* ---- CHARTS CONTAINER ---- */}
          <div className="charts-container p4-charts">

            {/* CỘT TRÁI: Câu 1 (Donut) ở trên + Câu 2 (Treemap) ở dưới */}
            <div className="p4-left-panel">

              {/* Donut: Nhóm trẻ chiếm tỷ trọng bao nhiêu */}
              <div className={`chart-card donut-card${loading ? ' is-loading' : ''}`}>
                <div className="chart-header">
                  <span className="chart-title">
                    Nhóm ít kinh nghiệm chiếm tỷ trọng bao nhiêu?
                  </span>
                </div>
                <div className="chart-content">
                  {data?.charts?.experience_distribution && (
                    <PlotlyChart figure={data.charts.experience_distribution} />
                  )}
                </div>
              </div>

              {/* Treemap: Quy mô & độ cởi mở với nhân sự trẻ theo nhóm vị trí */}
              <div className={`chart-card treemap-card${loading ? ' is-loading' : ''}`}>
                <div className="chart-header">
                  <span className="chart-title">
                    Nhóm vị trí nào cởi mở nhất với Fresher/Intern?
                  
                  </span>
                </div>
                <div className="chart-content plotly-clickable">
                  {data?.charts?.youth_opportunity_treemap && (
                    <PlotlyChart
                      key={`treemap-${position?.value || 'all'}`}
                      figure={data.charts.youth_opportunity_treemap}
                      onChartClick={handleTreemapClick}
                    />
                  )}
                </div>
              </div>

            </div>

            {/* CỘT PHẢI: Câu 3 (Box plot) trải toàn bộ chiều cao */}
            <div className="p4-right-panel">

              <div className={`chart-card boxplot-card${loading ? ' is-loading' : ''}`}>
                <div className="chart-header">
                  <span className="chart-title">
                    Lương khởi điểm Intern/Fresher chênh lệch thế nào giữa các nhóm vị trí?
                  </span>
                </div>
                <div className="chart-content">
                  {data?.charts?.youth_salary_boxplot && (
                    <PlotlyChart figure={data.charts.youth_salary_boxplot} />
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

export default Dashboard_page4;
