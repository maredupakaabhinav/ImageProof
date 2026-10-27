import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, ArrowLeft, Shield, AlertTriangle, 
  Calendar, FileImage, RefreshCw, CheckCircle2, Share2 
} from 'lucide-react';
import { fetchAnalysisById, getReportDownloadUrl, getImageUrl } from '../services/api';
import HashDisplay from '../components/HashDisplay';
import MetadataViewer from '../components/MetadataViewer';
import AnomaliesViewer from '../components/AnomaliesViewer';
import Badge from '../components/Badge';

export default function AnalysisResult({ analysisId, setActivePage }) {
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!analysisId) {
      setError('No analysis record ID provided.');
      setLoading(false);
      return;
    }

    const loadRecord = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAnalysisById(analysisId);
        setRecord(data);
      } catch (err) {
        setError(err.message || `Failed to fetch analysis record #${analysisId}.`);
      } finally {
        setLoading(false);
      }
    };

    loadRecord();
  }, [analysisId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
        <RefreshCw size={32} className="spin" style={{ color: 'var(--accent-blue)', marginBottom: '1rem' }} />
        <h2 style={{ fontSize: '1.25rem', color: 'var(--text-main)', marginBottom: '0.5rem' }}>
          Loading Evidence Record #{analysisId}...
        </h2>
        <p style={{ fontSize: '0.85rem' }}>Retrieving metadata, cryptographic hashes, and anomaly evaluation.</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div style={{ maxWidth: '600px', margin: '2rem auto' }}>
        <div className="alert alert-danger" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={20} />
          <span>{error || 'Evidence record could not be loaded.'}</span>
        </div>
        <button className="btn btn-secondary" onClick={() => setActivePage('history')}>
          <ArrowLeft size={16} />
          <span>Back to Case History</span>
        </button>
      </div>
    );
  }

  const { case_id, original_filename, stored_filename, file_size, file_format, sha256_hash, metadata, anomalies, created_at, report_filename, notes } = record;
  const warningsCount = anomalies?.summary?.warning_count || 0;

  return (
    <div>
      {/* Top Action & Navigation Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <button 
          className="btn btn-secondary" 
          onClick={() => setActivePage('history')}
          style={{ fontSize: '0.85rem' }}
        >
          <ArrowLeft size={16} />
          <span>Case History</span>
        </button>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button 
            className="btn btn-outline"
            onClick={() => setActivePage('upload')}
            style={{ fontSize: '0.85rem' }}
          >
            <span>Analyze Another</span>
          </button>

          {report_filename && (
            <a 
              href={getReportDownloadUrl(report_filename)}
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
              style={{ fontSize: '0.85rem' }}
            >
              <Download size={16} />
              <span>Download PDF Forensic Report</span>
            </a>
          )}
        </div>
      </div>

      {/* Case Header Card */}
      <div className="card" style={{ marginBottom: '1.5rem', background: 'var(--bg-secondary)', borderLeft: '4px solid var(--accent-blue)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Evidence File Analysis
              </span>
              <Badge status={warningsCount > 0 ? 'warning' : 'verified'} label={case_id} />
            </div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
              {original_filename}
            </h1>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <span><strong>Format:</strong> {file_format}</span>
              <span>•</span>
              <span><strong>Size:</strong> {metadata?.file_info?.size_formatted || `${file_size} B`}</span>
              <span>•</span>
              <span><strong>Ingestion Date:</strong> {created_at}</span>
            </div>
          </div>

          {notes && (
            <div style={{ background: 'var(--bg-card)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-dim)', maxWidth: '380px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>
                Investigator Notes:
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>{notes}</div>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Evidence Preview & Integrity (Left) + Anomalies Audit (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Left Column: Image Preview & SHA-256 Checksum */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <FileImage size={18} color="var(--accent-blue)" />
              Evidence Asset & Integrity
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {metadata?.file_info?.width} x {metadata?.file_info?.height} px
            </span>
          </div>

          {/* Image Preview Box */}
          <div style={{ textAlign: 'center', background: '#070a12', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-dim)', marginBottom: '1.25rem' }}>
            <img 
              src={getImageUrl(stored_filename)} 
              alt={original_filename}
              style={{ maxHeight: '280px', maxWidth: '100%', objectFit: 'contain', borderRadius: 'var(--radius-sm)' }}
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>

          {/* Cryptographic Checksum Component */}
          <HashDisplay hash={sha256_hash} />
        </div>

        {/* Right Column: Anomalies & Authenticity Findings */}
        <div>
          <AnomaliesViewer anomalies={anomalies} />
        </div>
      </div>

      {/* Bottom Section: Full Extracted Forensic Metadata Tabs */}
      <MetadataViewer metadata={metadata} />
    </div>
  );
}
