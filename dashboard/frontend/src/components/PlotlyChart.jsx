import React from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ figure, style }) => {
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

  return (
    <Plot
      data={figure.data}
      layout={modifiedLayout}
      config={{
        displayModeBar: false,
        responsive: true,
        scrollZoom: false,
        doubleClick: 'reset'
      }}
      style={{ width: '100%', height: '100%', ...style }}
      useResizeHandler={true}
    />
  );
};

export default PlotlyChart;
