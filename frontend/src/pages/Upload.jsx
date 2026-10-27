import React, { useState, useRef } from 'react';
import { UploadCloud, FileImage, ShieldAlert, CheckCircle2, ArrowRight, X, AlertCircle } from 'lucide-react';
import { uploadAndAnalyzeImage } from '../services/api';

const MAX_SIZE_MB = 16;
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

export default function Upload({ setActivePage, setSelectedAnalysisId }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [caseId, setCaseId] = useState('');
  const [notes, setNotes] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    setErrorMessage(null);

    if (!file) return;

    // Check extension
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['jpg', 'jpeg', 'png'].includes(ext)) {
      setErrorMessage(`Unsupported file format (.${ext}). Only JPG, JPEG, and PNG images are accepted.`);
      return;
    }

    // Check file size (16MB limit)
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_SIZE_MB) {
      setErrorMessage(`File exceeds ${MAX_SIZE_MB}MB limit (selected file is ${sizeMb.toFixed(1)}MB). Please choose a smaller file.`);
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setErrorMessage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage('Please select an evidence image to analyze.');
      return;
    }

    try {
      setUploading(true);
      setErrorMessage(null);
      setStatusMessage('Ingesting image and computing SHA-256 cryptographic checksum...');

      const formData = new FormData();
      formData.append('image', selectedFile);
      if (caseId.trim()) formData.append('case_id', caseId.trim());
      if (notes.trim()) formData.append('notes', notes.trim());

      const result = await uploadAndAnalyzeImage(formData);

      setStatusMessage('Analysis complete! Redirecting to report...');
      
      // Pass the new analysis ID and navigate to results page
      if (setSelectedAnalysisId) {
        setSelectedAnalysisId(result.id);
      }
      setTimeout(() => {
        setActivePage('result');
      }, 500);

    } catch (err) {
      setErrorMessage(err.message || 'Image analysis failed. Please verify that the Flask backend is running on http://127.0.0.1:5000.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
          Ingest & Analyze Evidence Image
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Upload JPG or PNG evidence. The backend will extract EXIF metadata, calculate SHA-256 checksums, and evaluate anomaly rules.
        </p>
      </div>

      {errorMessage && (
        <div className="alert alert-danger">
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        {/* Case Metadata Inputs */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              Case Reference ID (Optional)
            </label>
            <input 
              type="text" 
              className="form-input"
              placeholder="e.g. CASE-2026-LAB-01 (Auto-generated if blank)"
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              disabled={uploading}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              Investigator Notes (Optional)
            </label>
            <input 
              type="text" 
              className="form-input"
              placeholder="e.g. Seized from suspect smartphone during lab exam"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={uploading}
            />
          </div>
        </div>

        {/* Dropzone */}
        {!selectedFile ? (
          <div 
            className={`dropzone ${isDragging ? 'active' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
            <UploadCloud className="dropzone-icon" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Drag & Drop Image Here, or Click to Browse
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Supports JPG, JPEG, and PNG formats (Max size: 16 MB)
            </p>
          </div>
        ) : (
          /* Preview Selected File */
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-md)', padding: '1.25rem', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <FileImage size={24} color="var(--accent-blue)" />
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{selectedFile.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type || 'image'}
                  </div>
                </div>
              </div>
              <button 
                type="button" 
                onClick={handleClear} 
                className="btn btn-secondary" 
                style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
                disabled={uploading}
              >
                <X size={14} />
                <span>Remove</span>
              </button>
            </div>

            {previewUrl && (
              <div style={{ textAlign: 'center', background: '#070a12', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-dim)' }}>
                <img 
                  src={previewUrl} 
                  alt="Selected Preview" 
                  style={{ maxHeight: '240px', maxWidth: '100%', objectFit: 'contain', borderRadius: 'var(--radius-sm)' }}
                />
              </div>
            )}
          </div>
        )}

        {/* Submit Action */}
        <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {uploading ? (
              <span style={{ color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="spin" style={{ display: 'inline-block' }}>⟳</span>
                {statusMessage}
              </span>
            ) : (
              <span>Files are securely validated and processed locally.</span>
            )}
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={!selectedFile || uploading}
            style={{ minWidth: '180px' }}
          >
            {uploading ? (
              <span>Processing...</span>
            ) : (
              <>
                <ShieldAlert size={16} />
                <span>Start Forensic Analysis</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Forensic Ingestion Standards */}
      <div className="card" style={{ marginTop: '1.5rem', background: 'var(--bg-secondary)', border: '1px solid var(--border-dim)' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle2 size={16} color="var(--accent-blue)" />
          Forensic Acquisition Standards (ISO/IEC 27037)
        </h4>
        <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', paddingLeft: '1.25rem', lineHeight: '1.7' }}>
          <li><strong>Cryptographic Chain of Custody:</strong> Bitwise SHA-256 hash is computed immediately upon ingestion.</li>
          <li><strong>Non-Destructive Extraction:</strong> Image metadata, EXIF tags, and GPS coordinates are analyzed in read-only memory.</li>
          <li><strong>Tampering Heuristics:</strong> Discrepancies between capture timestamps and modification signatures are automatically evaluated.</li>
        </ul>
      </div>
    </div>
  );
}
