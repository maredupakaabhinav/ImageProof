import React, { useState, useEffect } from 'react';
import { 
  History as HistoryIcon, Search, FileText, Trash2, 
  RefreshCw, UploadCloud, AlertTriangle, ExternalLink, Filter 
} from 'lucide-react';
import { fetchHistory, deleteAnalysisRecord, getReportDownloadUrl } from '../services/api';
import Badge from '../components/Badge';

export default function History({ setActivePage, setSelectedAnalysisId }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all' | 'warnings' | 'verified'

  const loadRecords = async (query = '') => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchHistory(query);
      setRecords(data);
    } catch (err) {
      setError(err.message || 'Failed to load case history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecords(searchQuery);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadRecords(searchQuery);
  };

  const handleInspect = (id) => {
    if (setSelectedAnalysisId) setSelectedAnalysisId(id);
    setActivePage('result');
  };

  const handleDelete = async (id, originalFilename) => {
    const confirmed = window.confirm(`Are you sure you want to delete forensic record #${id} (${originalFilename})?`);
    if (!confirmed) return;

    try {
      await deleteAnalysisRecord(id);
      setRecords(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      alert(`Failed to delete record: ${err.message}`);
    }
  };

  // Filter records in memory
  const filteredRecords = records.filter(item => {
    const warnings = item.anomalies?.summary?.warning_count || 0;
    if (filterType === 'warnings') return warnings > 0;
    if (filterType === 'verified') return warnings === 0;
    return true;
  });

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            Digital Evidence Case History
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Audit trail of analyzed image files, cryptographic digests, and generated forensic reports.
          </p>
        </div>

        <button 
          className="btn btn-primary" 
          onClick={() => setActivePage('upload')}
        >
          <UploadCloud size={16} />
          <span>New Analysis</span>
        </button>
      </div>

      {error && (
        <div className="alert alert-danger">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '0.75rem', flex: 1, minWidth: '280px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input 
                type="text" 
                className="form-input"
                placeholder="Search by Case ID, Filename, or SHA-256 hash..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ paddingLeft: '2.25rem' }}
              />
              <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
            <button type="submit" className="btn btn-secondary" style={{ padding: '0.6rem 1rem' }}>
              Search
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={14} color="var(--text-muted)" />
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
              className="form-input"
              style={{ width: 'auto', padding: '0.55rem 0.85rem', cursor: 'pointer' }}
            >
              <option value="all">All Records ({records.length})</option>
              <option value="warnings">With Warnings</option>
              <option value="verified">Clean / Verified</option>
            </select>

            <button 
              type="button"
              className="btn btn-outline" 
              onClick={() => { setSearchQuery(''); loadRecords(''); }}
              title="Reload all records"
              style={{ padding: '0.55rem 0.75rem' }}
            >
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
            </button>
          </div>
        </form>
      </div>

      {/* History Table */}
      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <RefreshCw size={24} className="spin" style={{ marginBottom: '0.5rem' }} />
            <div>Loading forensic case history from SQLite...</div>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
            <HistoryIcon size={36} color="var(--text-subtle)" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              {searchQuery ? 'No matching records found' : 'No evidence analyses recorded yet'}
            </h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              {searchQuery ? 'Try searching for a different keyword or clearing the filter.' : 'Upload an image file to begin digital evidence tracking.'}
            </p>
            {searchQuery ? (
              <button className="btn btn-secondary" onClick={() => { setSearchQuery(''); loadRecords(''); }}>
                Clear Search Filter
              </button>
            ) : (
              <button className="btn btn-primary" onClick={() => setActivePage('upload')}>
                <UploadCloud size={16} />
                <span>Upload First Image</span>
              </button>
            )}
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>#ID</th>
                  <th>Case ID</th>
                  <th>Evidence Filename</th>
                  <th>SHA-256 Checksum</th>
                  <th>Date & Time</th>
                  <th>Forensic Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((item) => {
                  const warnings = item.anomalies?.summary?.warning_count || 0;
                  return (
                    <tr key={item.id}>
                      <td style={{ color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>
                        #{item.id}
                      </td>
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
                        {item.sha256_hash.substring(0, 10)}...{item.sha256_hash.substring(58)}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {item.created_at}
                      </td>
                      <td>
                        {warnings > 0 ? (
                          <Badge status="warning" label={`${warnings} Warning${warnings > 1 ? 's' : ''}`} />
                        ) : (
                          <Badge status="verified" label="Consistent" />
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                          <button 
                            className="btn btn-secondary" 
                            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
                            onClick={() => handleInspect(item.id)}
                            title="Inspect detailed metadata and analysis"
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
                              title="Download PDF evidence report"
                            >
                              <FileText size={12} />
                              <span>PDF</span>
                            </a>
                          )}
                          <button 
                            className="btn btn-danger"
                            style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
                            onClick={() => handleDelete(item.id, item.original_filename)}
                            title="Delete evidence record"
                          >
                            <Trash2 size={12} />
                          </button>
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
