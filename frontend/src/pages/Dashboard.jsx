import React, { useState, useEffect } from 'react';
import { 
  FileImage, Briefcase, AlertTriangle, ShieldCheck, 
  UploadCloud, ArrowRight, FileText, ExternalLink, RefreshCw 
} from 'lucide-react';
import { fetchDashboardStats, getReportDownloadUrl, getImageUrl } from '../services/api';
import Badge from '../components/Badge';

export default function Dashboard({ setActivePage, setSelectedAnalysisId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDashboardStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleViewAnalysis = (id) => {
    if (setSelectedAnalysisId) setSelectedAnalysisId(id);
    setActivePage('result');
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            Forensics Lab Dashboard
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Overview of examined digital evidence files and active case records.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button 
            className="btn btn-secondary" 
            onClick={loadStats} 
            disabled={loading}
            title="Refresh statistics"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
          <button 
            className="btn btn-primary" 
            onClick={() => setActivePage('upload')}
          >
            <UploadCloud size={16} />
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--color-info-bg)', color: 'var(--accent-blue)' }}>
            <FileImage size={24} />
          </div>
          <div>
            <div className="stat-value">{stats ? stats.total_analyzed : '-'}</div>
            <div className="stat-label">Total Images Analyzed</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(56, 189, 248, 0.12)', color: 'var(--accent-blue)' }}>
            <Briefcase size={24} />
          </div>
          <div>
            <div className="stat-value">{stats ? stats.total_cases : '-'}</div>
            <div className="stat-label">Unique Case Files</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--color-warning-bg)', color: 'var(--color-warning)' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div className="stat-value">{stats ? stats.warning_cases : '-'}</div>
            <div className="stat-label">Flagged with Warnings</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)' }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--color-success)' }}>SHA-256</div>
            <div className="stat-label">Forensic Hash Engine Active</div>
          </div>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <FileImage size={18} color="var(--accent-blue)" />
            Recent Forensic Analyses
          </h2>
          <button 
            className="btn btn-outline" 
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            onClick={() => setActivePage('history')}
          >
            <span>View All Cases</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            <RefreshCw size={24} className="spin" style={{ marginBottom: '0.5rem' }} />
            <div>Loading recent evidence records...</div>
          </div>
        ) : !stats || stats.recent_analyses.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
            <UploadCloud size={40} color="var(--text-subtle)" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              No evidence images analyzed yet
            </h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              Upload your first JPG or PNG image to extract metadata and compute SHA-256 hash.
            </p>
            <button className="btn btn-primary" onClick={() => setActivePage('upload')}>
              <UploadCloud size={16} />
              <span>Upload First Image</span>
            </button>
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Evidence Filename</th>
                  <th>SHA-256 Digest</th>
                  <th>Analysis Timestamp</th>
                  <th>Findings</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_analyses.map((item) => {
                  const warnings = item.anomalies?.summary?.warning_count || 0;
                  return (
                    <tr key={item.id}>
                      <td style={{ fontWeight: 600, color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>
                        {item.case_id}
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{item.original_filename}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {item.file_format} • {item.metadata?.file_info?.size_formatted || `${item.file_size} B`}
                        </div>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {item.sha256_hash.substring(0, 12)}...{item.sha256_hash.substring(56)}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {item.created_at}
                      </td>
                      <td>
                        {warnings > 0 ? (
                          <Badge status="warning" label={`${warnings} Warning${warnings > 1 ? 's' : ''}`} />
                        ) : (
                          <Badge status="verified" label="Standard" />
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                          <button 
                            className="btn btn-secondary" 
                            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
                            onClick={() => handleViewAnalysis(item.id)}
                            title="Inspect metadata and anomaly findings"
                          >
                            Inspect
                          </button>
                          {item.report_filename && (
                            <a 
                              href={getReportDownloadUrl(item.report_filename)}
                              className="btn btn-outline"
                              style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
                              target="_blank"
                              rel="noreferrer"
                              title="Download official PDF forensic report"
                            >
                              <FileText size={12} />
                              <span>PDF</span>
                            </a>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
