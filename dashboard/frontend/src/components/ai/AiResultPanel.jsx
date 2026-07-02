import React from 'react';
import PlotlyChart from '../PlotlyChart';
import { BarChart3, Info } from 'lucide-react';

const AiResultPanel = ({ resultData }) => {
  if (!resultData) return null;

  return (
    <div className="chart-card" style={{ marginBottom: '20px' }}>
      <div className="chart-header">
        <span className="chart-title">
          <BarChart3 size={16} color="#B45309" />
          Kết Quả Phân Tích
        </span>
      </div>
      
      <div className="chart-content" style={{ padding: '20px', minHeight: '300px' }}>
        {resultData.type === 'plotly' && (
          <PlotlyChart figure={resultData.data} />
        )}
        
        {resultData.type === 'html' && (
          <div 
            className="ai-html-result"
            dangerouslySetInnerHTML={{ __html: resultData.data }} 
            style={{ overflowX: 'auto' }}
          />
        )}
        
        {resultData.type === 'text' && (
          <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px', backgroundColor: '#F3F4F6', padding: '15px', borderRadius: '8px' }}>
            {resultData.data}
          </div>
        )}

        {resultData.type === 'error' && (
          <div style={{ color: '#DC2626', backgroundColor: '#FEE2E2', padding: '15px', borderRadius: '8px', fontSize: '14px', fontWeight: '500' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Lỗi khi thực thi mã nguồn:</div>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', margin: 0, fontFamily: 'monospace' }}>
              {resultData.data}
            </pre>
          </div>
        )}
      </div>

      <div className="chart-caption" style={{ display: 'flex', alignItems: 'center', gap: '6px', justifyContent: 'center' }}>
        <Info size={14} color="#6B7280" />
        Lưu ý: Kết quả này được tính toán hoàn toàn dựa trên bộ dữ liệu thật (vietnam_it_jobs_processed.csv) của dự án.
      </div>
    </div>
  );
};

export default AiResultPanel;
