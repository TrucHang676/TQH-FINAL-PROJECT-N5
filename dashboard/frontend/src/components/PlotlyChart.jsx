import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ figure, style, onChartClick, onGraphReady }) => {
  const [revision, setRevision] = useState(0);

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

  return (
    <Plot
      data={figure.data}
      layout={modifiedLayout}
      revision={revision}
      config={{
        displayModeBar: false,
        responsive: true,
        scrollZoom: false,
        doubleClick: 'reset'
      }}
      onClick={onChartClick ? (e) => onChartClick(e) : undefined}
      onInitialized={(fig, graphDiv) => onGraphReady && onGraphReady(graphDiv)}
      onUpdate={(fig, graphDiv) => onGraphReady && onGraphReady(graphDiv)}
      style={{ width: '100%', height: '100%', cursor: onChartClick ? 'pointer' : 'default', ...style }}
      useResizeHandler={true}
    />
  );
};

export default PlotlyChart;
