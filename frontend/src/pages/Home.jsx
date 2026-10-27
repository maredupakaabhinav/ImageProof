import React from 'react';
import { Shield, UploadCloud, FileCheck, Hash, Camera, AlertTriangle, FileText, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function Home({ setActivePage }) {
  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-pill">
          <Shield size={14} />
          <span>Digital Forensics & Incident Response (DFIR) Platform</span>
        </div>

        <h1 className="hero-title">
          Image Metadata & Evidence Authenticity Analyzer
        </h1>

        <p className="hero-description">
          <strong>ImageProof</strong> automates the forensic examination of digital images. 
          Extract EXIF metadata, calculate bitwise SHA-256 cryptographic hashes, 
          detect editing artifacts and metadata anomalies, and generate court-ready PDF forensic reports.
        </p>

        <div className="hero-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setActivePage('upload')}
          >
            <UploadCloud size={18} />
            <span>Upload Evidence Image</span>
          </button>

          <button 
            className="btn btn-secondary"
            onClick={() => setActivePage('dashboard')}
          >
            <span>Open Dashboard</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </section>

      {/* Core Technical Pillars Grid */}
      <section style={{ marginTop: '2rem', marginBottom: '3rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Forensic Analysis Capabilities
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Built according to international digital evidence handling principles (ISO/IEC 27037).
          </p>
        </div>

        <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
          <div className="card">
            <div style={{ color: 'var(--accent-blue)', marginBottom: '0.75rem' }}>
              <Hash size={28} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.4rem' }}>
              SHA-256 Evidence Integrity
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Computes a 256-bit cryptographic fingerprint to verify file integrity. Any 1-bit alteration causes an avalanche effect, altering the hash completely.
            </p>
          </div>

          <div className="card">
            <div style={{ color: 'var(--accent-blue)', marginBottom: '0.75rem' }}>
              <Camera size={28} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.4rem' }}>
              Deep EXIF Extraction
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Extracts camera make, model, lens parameters, shutter speed, ISO, aperture, original capture timestamps, and embedded GPS satellite geolocation.
            </p>
          </div>

          <div className="card">
            <div style={{ color: 'var(--color-warning)', marginBottom: '0.75rem' }}>
              <AlertTriangle size={28} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.4rem' }}>
              Forensic Anomaly Heuristics
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Rule-based checks identify software signatures (Photoshop, GIMP), missing camera hardware tags, timestamp divergence, and metadata stripping.
            </p>
          </div>

          <div className="card">
            <div style={{ color: 'var(--color-success)', marginBottom: '0.75rem' }}>
              <FileText size={28} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.4rem' }}>
              Forensic PDF Reports
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Generates formal evidence documentation using ReportLab with case logs, cryptographic checksums, audit findings, and examiner attestation sign-offs.
            </p>
          </div>
        </div>
      </section>

      {/* Cyber Security Viva Reference Box */}
      <section className="card" style={{ borderLeft: '4px solid var(--accent-blue)', marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileCheck size={18} color="var(--accent-blue)" />
          Digital Forensics Primer: Integrity vs. Authenticity
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.7', marginBottom: '0.75rem' }}>
          <strong>Cryptographic Hashing</strong> proves that a digital evidence file has not been altered or corrupted since it was seized (evidence integrity). However, a hash alone cannot prove an image was never manipulated before seizure.
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.7' }}>
          <strong>Metadata Analysis & Anomaly Detection</strong> examines the internal structure of the file: looking for software tags, camera consistency, and timeline continuity to help forensic investigators assess whether the photo represents a direct camera capture or a modified export.
        </p>
      </section>
    </div>
  );
}
