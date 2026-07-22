import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyChart from './PlotlyChart';
import Select from 'react-select';
import KpiCard from './KpiCard';

const page1Cache = new Map();

const Dashboard_page1 = () => {
  // =============================================================================
  // Quản lý trạng thái (State) của các bộ lọc
  // =============================================================================
  const sourceOptions = ['ITviec', 'TopDev', 'VietJobs', 'Vieclam24h', 'TopCV', 'JobsGO'];
  const [sources, setSources] = useState([...sourceOptions]);
  const [position, setPosition] = useState(null);
  const [experience, setExperience] = useState(null);
  const [mapToggle, setMapToggle] = useState('region_chart');
  const [region, setRegion] = useState(null);

  // Trạng thái drill-down: null = đang xem 3 vùng, 'Nam'/'Bắc'/'Trung' = đang xem tỉnh của vùng đó
  const [drillRegion, setDrillRegion] = useState(null);
  // State 2: Vùng đang được cross-filter / highlight (click lần 1) — chưa drill-down
  const [selectedRegion, setSelectedRegion] = useState(null);

  // Trạng thái lọc chéo (Cross-filter): Hình thức làm việc -> Line chart xu hướng
  const [workType, setWorkType] = useState(null);

  // =============================================================================
  // Quản lý trạng thái dữ liệu trả về từ API và trạng thái tải (Loading)
  // =============================================================================
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Thêm đầy đủ options từ file page1.py cũ
  const positionOptions = [
    { value: 'All', label: 'Tất cả vị trí' },
    { value: 'Software Development', label: 'Software Development' },
    { value: 'AI / ML / Data Science', label: 'AI / ML / Data Science' },
    { value: 'Mobile / Game / Embedded', label: 'Mobile / Game / Embedded' },
    { value: 'Cloud / DevOps / SRE', label: 'Cloud / DevOps / SRE' },
    { value: 'QA / Testing', label: 'QA / Testing' },
    { value: 'Data Engineering / Database', label: 'Data Engineering / Database' },
    { value: 'IT Support / ERP', label: 'IT Support / ERP' },
    { value: 'Management / Architecture', label: 'Management / Architecture' },
    { value: 'Product / Business / UX', label: 'Product / Business / UX' },
    { value: 'Cybersecurity', label: 'Cybersecurity' },
    { value: 'Other', label: 'Khác' }
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

  useEffect(() => {
    if (!position || !experience || !region) return;
    let isActive = true;

    const cacheKey = JSON.stringify({ sources: [...sources].sort(), position: position.value, experience: experience.value, region: region.value, work_type: workType });
    if (page1Cache.has(cacheKey)) {
      setData(page1Cache.get(cacheKey));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.post('http://localhost:8000/api/dashboard/page1', {
          sources,
          position: position.value,
          experience: experience.value,
          region: region.value,
          work_type: workType
        });
        if (isActive) {
          page1Cache.set(cacheKey, response.data);
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
  }, [sources, position, experience, region, workType]);

  const handleSourceChange = (val) => {
    if (sources.includes(val)) {
      setSources(sources.filter((s) => s !== val));
    } else {
      setSources([...sources, val]);
    }
  };

  const resetFilters = () => {
    setSources([...sourceOptions]);
    setPosition(positionOptions[0]);
    setExperience(experienceOptions[0]);
    setRegion(regionOptions[0]);
    setWorkType(null);
    setMapToggle('region_chart');
    setSelectedRegion(null);
    setDrillRegion(null);
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

  // Drill-down 2 bước:
  // Click lần 1  → highlight cột, dim các cột khác (selectedRegion) & lọc API toàn trang!
  // Click lần 2 trên cùng cột → drill-down vào tỉnh (drillRegion)
  const handleRegionClick = (e) => {
    if (!e.points || e.points.length === 0) return;
    const clickedLabel = e.points[0].x || e.points[0].y || e.points[0].label;
    if (!clickedLabel) return;
    const canDrill = ['Bắc', 'Trung', 'Nam'].includes(clickedLabel);

    if (selectedRegion === clickedLabel) {
      // Click lần 2 vào cùng cột
      if (canDrill) {
        setDrillRegion(clickedLabel); // → drill-down
      } else {
        setSelectedRegion(null); // → bỏ chọn
        setRegion(regionOptions[0]); // Reset filter API về Tất cả
      }
    } else {
      // Click lần 1 (hoặc đổi sang cột khác) → chỉ highlight & lọc API toàn trang
      setSelectedRegion(clickedLabel);
      const matchedOpt = regionOptions.find(o => o.value === clickedLabel) || regionOptions[0];
      setRegion(matchedOpt);
    }
  };

  // Helper: dim các cột không được chọn trong figure (hoặc trả lại opacity 1 cho tất cả khi reset)
  const getHighlightedFigure = (figure, highlightLabel) => {
    if (!figure || !figure.data) return figure;
    const newData = figure.data.map(trace => {
      const labels = Array.isArray(trace.x) ? trace.x
        : Array.isArray(trace.y) ? trace.y : [];
      if (!labels.length) return { ...trace, selectedpoints: null };
      const opacities = labels.map(lbl => (!highlightLabel || lbl === highlightLabel) ? 1 : 0.28);
      return {
        ...trace,
        selectedpoints: null,
        marker: {
          ...trace.marker,
          opacity: opacities
        }
      };
    });
    return { ...figure, data: newData };
  };

  // Cross-filter: click thanh hình thức làm việc → lọc Line chart xu hướng
  const handleWorkClick = (e) => {
    if (e.points && e.points.length > 0) {
      // Vì là horizontal bar chart nên tên hình thức nằm ở trục Y (point.y)
      let clickedLabel = e.points[0].y || e.points[0].label || e.points[0].x;
      if (clickedLabel) {
        setWorkType((prev) => (prev === clickedLabel ? null : clickedLabel));
      }
    }
  };

  // Tạo Plotly figure cho drill-down từ city_breakdown data
  const buildDrillChart = (regionName) => {
    const cities = data?.city_breakdown?.[regionName] || [];
    if (cities.length === 0) return null;
    const labels = cities.map(c => c.city);
    const values = cities.map(c => c.count);
    const max = Math.max(...values);

    // Màu theme theo vùng miền (khớp với màu cột vùng gốc)
    const regionTheme = {
      'Bắc':  { r: 250, g: 103, b: 129 }, // #FA6781 – đỏ hồng
      'Trung':{ r: 255, g: 201, b:  77 }, // #FFC94D – vàng
      'Nam':  { r:  89, g: 178, b: 146 }, // #59B292 – xanh lá
    };
    const theme = regionTheme[regionName] || { r: 89, g: 178, b: 146 };

    // Gradient opacity: cột cao nhất = 100%, thấp nhất = 40%
    const colors = values.map(v => {
      const opacity = 0.40 + (v / max) * 0.60;
      return `rgba(${theme.r},${theme.g},${theme.b},${opacity.toFixed(2)})`;
    });

    // Chỉ hiện số trên cột khi giá trị đủ lớn (top 3), ẩn các cột nhỏ tránh lộn xộn
    const threshold = max * 0.05;
    const barText = values.map(v => v >= threshold ? v.toLocaleString('vi-VN') : '');

    return {
      data: [{
        type: 'bar',
        x: labels,
        y: values,
        marker: {
          color: colors,
          line: { color: colors.map(c => c.replace(/[\d.]+\)$/, '1)')), width: 1 }
        },
        text: barText,
        textposition: 'outside',
        textfont: { size: 11, color: '#374151' },
        hovertemplate: '<b>%{x}</b><br>%{y:,} tin<extra></extra>',
        cliponaxis: false
      }],
      layout: {
        margin: { t: 50, b: 75, l: 50, r: 15 },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
          tickangle: -35,
          automargin: true,
          tickfont: { size: 10, color: '#6B7280' }
        },
        yaxis: {
          gridcolor: 'rgba(0,0,0,0.06)',
          tickfont: { size: 10 },
          rangemode: 'nonnegative'
        },
        bargap: 0.35,
        uniformtext: { minsize: 9, mode: 'hide' }
      }
    };
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
              tooltip="Tổng số tin tuyển dụng IT được thu thập từ tất cả nguồn dữ liệu, sau khi áp dụng các bộ lọc hiện tại."
            />

            <KpiCard
              title="Tháng cao điểm"
              badge="Đỉnh"
              value={data?.kpi?.peak_month?.month || 'N/A'}
              description={`Đạt đỉnh với ${data?.kpi?.peak_month?.count?.toLocaleString() || 0} tin`}
              tooltip="Tháng ghi nhận số lượng tin tuyển dụng cao nhất trong toàn bộ giai đoạn dữ liệu."
            />

            <KpiCard
              title="Địa bàn lớn nhất"
              badge="Hot"
              value={data?.kpi?.top_city?.city || 'N/A'}
              description={`Chiếm ${data?.kpi?.top_city?.pct?.toFixed(1) || 0}% toàn quốc`}
              tooltip="Tỉnh/thành phố có nhu cầu tuyển dụng IT cao nhất, được tính theo tỉ lệ phần trăm so với tổng cả nước."
            />

            <KpiCard
              title="Hình thức chủ đạo"
              badge="Phổ biến"
              value={data?.kpi?.top_work?.work || 'N/A'}
              description={`Chiếm ${data?.kpi?.top_work?.pct?.toFixed(1) || 0}% tổng thể`}
              tooltip="Hình thức làm việc được đăng tuyển nhiều nhất, phản ánh xu hướng tuyển dụng chủ đạo của thị trường IT hiện tại."
            />
          </div>

          <div className="charts-container">
            {/* Left map */}
            <div className={`chart-card map-card${loading ? ' is-loading' : ''}`}>
              <div className="chart-header map-header">
                <span className="chart-title">
                  {mapToggle === 'map' ? 'Bản đồ phân bố tuyển dụng' : (
                    drillRegion
                      ? `📍 Miền ${drillRegion} — Top tỉnh/thành`
                      : 'Biểu đồ phân bố tuyển dụng'
                  )}
                  {mapToggle === 'region_chart' && !drillRegion && (
                    <span style={{ fontSize: '11px', fontWeight: 400, color: '#9CA3AF', marginLeft: 8 }}>
                      {selectedRegion
                        ? '(click lại để drill-down)'
                        : '(click cột để lọc)'}
                    </span>
                  )}
                </span>
                <div className="toggle-container">
                  <div className="toggle-switch" style={{ display: 'flex', gap: '10px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="region_chart" checked={mapToggle === 'region_chart'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Theo vùng</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <input type="radio" value="map" checked={mapToggle === 'map'} onChange={(e) => setMapToggle(e.target.value)} />
                      <span className="radio-label-text">Theo tỉnh</span>
                    </label>
                  </div>
                </div>
              </div>
              <div className="chart-content" style={{ position: 'relative' }}>
                {/* Geographic Map */}
                {mapToggle === 'map' && data?.charts?.map && (
                  <PlotlyChart key="map-view" figure={data.charts.map} scrollZoom={true} />
                )}

                {/* Vertical Region Bar Chart — hỗ trợ Drill-down 2 bước */}
                {mapToggle === 'region_chart' && data?.charts?.region_chart && !drillRegion && (
                  <div className="plotly-clickable" style={{ width: '100%', height: '100%' }}>
                    <PlotlyChart
                      key={`region-view-${selectedRegion || 'reset'}`}
                      figure={getHighlightedFigure(data.charts.region_chart, selectedRegion)}
                      onChartClick={handleRegionClick}
                    />
                  </div>
                )}

                {/* Drill-down: hiện tỉnh/thành theo vùng đã chọn */}
                {mapToggle === 'region_chart' && drillRegion && (() => {
                  const drillFigure = buildDrillChart(drillRegion);
                  const btnColors = {
                    'Bắc':  { border: '#FA6781', bg: 'rgba(250,103,129,0.1)', text: '#c0324e' },
                    'Trung':{ border: '#e6a800', bg: 'rgba(255,201,77,0.15)',  text: '#9a6d00' },
                    'Nam':  { border: '#59B292', bg: 'rgba(89,178,146,0.1)',   text: '#469d7e' },
                  };
                  const btn = btnColors[drillRegion] || btnColors['Nam'];
                  return drillFigure ? (
                    <div className="drill-chart-wrapper">
                      <button
                        onClick={() => {
                          setDrillRegion(null); // Quay về State 2 (vẫn giữ selectedRegion)
                        }}
                        style={{
                          position: 'absolute', top: 8, left: 8, zIndex: 10,
                          display: 'flex', alignItems: 'center', gap: 5,
                          padding: '4px 12px', border: `1px solid ${btn.border}`,
                          borderRadius: 20, background: btn.bg,
                          color: btn.text, fontSize: 12, fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        ↩ Quay lại
                      </button>
                      <PlotlyChart key={`drill-${drillRegion}`} figure={drillFigure} />
                    </div>
                  ) : null;
                })()}

                {/* Floating Widget on Right of Vietnam Map */}
                {mapToggle === 'map' && data?.regions && (
                  <>
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
              <div className={`chart-card trend-card${loading ? ' is-loading' : ''}`}>
                <div className="chart-header">
                  <span className="chart-title">
                    Xu hướng tuyển dụng theo tháng
                    {workType && (
                      <span style={{
                        marginLeft: 8,
                        fontSize: '11px',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        background: 'rgba(89, 178, 146, 0.15)',
                        color: '#469d7e',
                        fontWeight: 600,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        📍 Đã lọc: {workType}
                        <button
                          onClick={() => setWorkType(null)}
                          style={{
                            border: 'none',
                            background: 'none',
                            cursor: 'pointer',
                            color: '#469d7e',
                            fontSize: '11px',
                            fontWeight: 'bold',
                            padding: 0,
                            marginLeft: '2px'
                          }}
                          title="Bỏ lọc"
                        >
                          ✕
                        </button>
                      </span>
                    )}
                  </span>
                </div>
                <div className="chart-content">
                  {data?.charts?.trend && <PlotlyChart figure={data.charts.trend} />}
                </div>
              </div>

              <div className="split-row">
                <div className={`chart-card donut-card${loading ? ' is-loading' : ''}`}>
                  <div className="chart-header">
                    <span className="chart-title">
                      Hình thức làm việc chủ đạo
                      <span style={{ fontSize: '11px', fontWeight: 400, color: '#9CA3AF', marginLeft: 8 }}>
                        (click cột để lọc line chart)
                      </span>
                    </span>
                  </div>
                  <div className="chart-content plotly-clickable">
                    {data?.charts?.work && <PlotlyChart figure={data.charts.work} onChartClick={handleWorkClick} />}
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

export default Dashboard_page1;
