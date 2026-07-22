import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ figure, style, onChartClick, onGraphReady, scrollZoom = false }) => {
  const [revision, setRevision] = useState(0);
  const [hoveredPtIdx, setHoveredPtIdx] = useState(null);
  const wrapperRef = useRef(null);

  // Trigger a full Plotly recalculation/redraw when the figure data changes
  useEffect(() => {
    if (figure && figure.data) {
      setRevision(prev => prev + 1);
    }
  }, [figure]);

  if (!figure) return null;

  const modifiedLayout = {
    ...figure.layout,
    autosize: true
  };

  // Căn giữa và in đậm tiêu đề biểu đồ tự động
  if (modifiedLayout.title) {
    if (typeof modifiedLayout.title === 'string') {
      const cleanText = modifiedLayout.title.replace(/<\/?b>/g, '');
      modifiedLayout.title = {
        text: `<b>${cleanText}</b>`,
        x: 0.5,
        xanchor: 'center'
      };
    } else if (typeof modifiedLayout.title === 'object') {
      const currentText = modifiedLayout.title.text || '';
      const cleanText = currentText.replace(/<\/?b>/g, '');
      modifiedLayout.title = {
        ...modifiedLayout.title,
        text: `<b>${cleanText}</b>`,
        x: 0.5,
        xanchor: 'center'
      };
    }
  }

  // Nếu biểu đồ có thể click, thêm chế độ chọn để tự highlight
  if (onChartClick) {
    modifiedLayout.clickmode = 'event+select';
  }

  // Bar chart: e.event.target là overlay .nsewdrag (rect), không phải bar path
  // → dùng pointIndex để tìm đúng g.point > path trong DOM
  // Treemap: e.event.target là trực tiếp path → walk up từ target
  const handleHover = (e) => {
    if (!wrapperRef.current || !onChartClick) return;

    // Xóa border cũ trước
    wrapperRef.current.querySelectorAll('.hovered-bar')
      .forEach(el => el.classList.remove('hovered-bar'));

    // Thử cách 1: walk up từ event.target (hoạt động tốt cho Treemap)
    let found = false;
    let el = e?.event?.target;
    while (el && el !== wrapperRef.current) {
      if (el.tagName === 'path') {
        el.classList.add('hovered-bar');
        found = true;
        break;
      }
      el = el.parentElement;
    }

    // Cách 2 (fallback cho Bar Chart): dùng pointIndex → tìm g.point:nth-child
    if (!found) {
      const pt = e?.points?.[0];
      const idx = pt?.pointIndex ?? pt?.pointNumber;
      if (idx !== undefined) {
        const gPoints = wrapperRef.current.querySelectorAll('g.bars g.points g.point');
        const target = gPoints[idx]?.querySelector('path');
        if (target) target.classList.add('hovered-bar');
      }
    }
  };

  const handleUnhover = () => {
    if (!wrapperRef.current) return;
    wrapperRef.current.querySelectorAll('.hovered-bar')
      .forEach(el => el.classList.remove('hovered-bar'));
  };

  return (
    <div
      ref={wrapperRef}
      className={onChartClick ? 'plotly-clickable' : undefined}
      style={{ width: '100%', height: '100%' }}
    >
      <Plot
        data={figure.data}
        layout={modifiedLayout}
        revision={revision}
        config={{
          displayModeBar: false,
          responsive: true,
          scrollZoom: scrollZoom,
          doubleClick: 'reset'
        }}
        onClick={onChartClick ? (e) => onChartClick(e) : undefined}
        onHover={onChartClick ? handleHover : undefined}
        onUnhover={onChartClick ? handleUnhover : undefined}
        onInitialized={(fig, graphDiv) => onGraphReady && onGraphReady(graphDiv)}
        onUpdate={(fig, graphDiv) => onGraphReady && onGraphReady(graphDiv)}
        style={{ width: '100%', height: '100%', ...style }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default PlotlyChart;
