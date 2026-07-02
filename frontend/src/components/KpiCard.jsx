import React from 'react';
import PlotlyChart from './PlotlyChart';

/**
 * Reusable KPI Card Component
 * 
 * Props:
 * @param {string} title - The title of the KPI (e.g. "Tổng tin tuyển dụng")
 * @param {string} badge - A small badge text (e.g. "Năm 2024")
 * @param {string|number} value - The main metric value (e.g. "5.803")
 * @param {string} description - Subtext describing the metric
 * @param {object} sparkline - A Plotly figure object for the trend line (optional)
 * @param {string} tooltip - Tooltip description shown on hover (optional)
 */
export default function KpiCard({ title, badge, value, description, sparkline, tooltip }) {
  const cardContent = (
    <div className="kpi-card-info">
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        {badge && <span className="kpi-badge">{badge}</span>}
      </div>
      <div className="kpi-body">
        <div className="kpi-main-val">{value}</div>
        <div className="kpi-desc">{description}</div>
        {sparkline && (
          <div style={{ height: '40px', marginTop: '4px' }}>
            <PlotlyChart figure={sparkline} />
          </div>
        )}
      </div>
    </div>
  );

  if (tooltip) {
    return (
      <div className="kpi-card tooltip-wrap" data-tooltip={tooltip}>
        {cardContent}
      </div>
    );
  }

  return (
    <div className="kpi-card">
      {cardContent}
    </div>
  );
}
