import React from 'react';
import { AlertTriangle, CheckCircle2, Info, ShieldCheck, ChevronDown, Compass } from 'lucide-react';
import Badge from './Badge';

export default function AnomaliesViewer({ anomalies }) {
  if (!anomalies || !anomalies.findings) {
    return null;
  }

  const { summary = {}, findings = [] } = anomalies;

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">
          <ShieldCheck size={18} color="var(--accent-blue)" />
          Digital Authenticity & Anomaly Audit
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {summary.warning_count > 0 && (
            <Badge status="warning" label={`${summary.warning_count} Warning${summary.warning_count > 1 ? 's' : ''}`} />
          )}
          <Badge status="info" label={`${summary.info_count} Observations`} />
          <Badge status="verified" label={`${summary.verified_count} Verified`} />
        </div>
      </div>

      {/* Forensic Assessment Banner */}
      <div 
        style={{
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          marginBottom: '1.25rem',
          backgroundColor: summary.warning_count > 0 ? 'var(--color-warning-bg)' : 'var(--color-info-bg)',
          border: `1px solid ${summary.warning_count > 0 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(56, 189, 248, 0.3)'}`,
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}
      >
        <div style={{ flexShrink: 0 }}>
          {summary.warning_count > 0 ? (
            <AlertTriangle size={24} color="var(--color-warning)" />
          ) : (
            <Compass size={24} color="var(--accent-blue)" />
          )}
        </div>
        <div>
          <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
            Forensic Heuristic Assessment
          </div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {summary.assessment_label || 'Analysis Completed'}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Classification: <strong>{summary.assessment_category || 'General Digital Asset'}</strong>. Review findings below before making admissibility determinations.
          </div>
        </div>
      </div>

      {/* Findings List */}
      <div>
        {findings.map((item, idx) => {
          const status = (item.status || 'info').toLowerCase();
          return (
            <div key={item.rule_id || idx} className={`finding-item ${status}`}>
              <div className="finding-header">
                <div className="finding-title">
                  {status === 'warning' && <AlertTriangle size={16} color="var(--color-warning)" />}
                  {status === 'verified' && <CheckCircle2 size={16} color="var(--color-success)" />}
                  {status === 'info' && <Info size={16} color="var(--accent-blue)" />}
                  <span>{item.title}</span>
                </div>
                <Badge status={item.status} label={item.status.toUpperCase()} />
              </div>

              <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '0.4rem', fontWeight: 500 }}>
                {item.finding}
              </div>

              <div className="finding-body">
                <strong style={{ color: 'var(--text-muted)' }}>Forensic Context:</strong> {item.forensic_explanation}
              </div>

              {item.recommendation && (
                <div className="finding-rec">
                  <strong>Examiner Recommendation:</strong> {item.recommendation}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
