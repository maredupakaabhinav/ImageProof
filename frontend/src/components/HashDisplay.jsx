import React, { useState } from 'react';
import { Hash, Copy, Check } from 'lucide-react';

export default function HashDisplay({ hash, label = "SHA-256 Evidence Checksum" }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!hash) return;
    navigator.clipboard.writeText(hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Hash size={14} color="var(--accent-blue)" />
          {label}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>FIPS 180-4 256-bit Digest</span>
      </div>

      <div className="hash-box">
        <span className="hash-text">{hash || "Hash not available"}</span>
        <button 
          onClick={handleCopy} 
          className="copy-btn" 
          title="Copy cryptographic hash to clipboard"
        >
          {copied ? <Check size={14} color="var(--color-success)" /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
        <strong style={{ color: 'var(--text-main)' }}>Cyber Forensics Note:</strong> Any single-bit alteration to this evidence image will produce a drastically different hash (the <em>Avalanche Effect</em>).
      </div>
    </div>
  );
}
