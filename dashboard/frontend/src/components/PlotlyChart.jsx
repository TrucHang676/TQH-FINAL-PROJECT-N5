import React from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ figure, style }) => {
  if (!figure) return null;

  return (
    <Plot
      data={figure.data}
      layout={{
        ...figure.layout,
        autosize: true
      }}
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
