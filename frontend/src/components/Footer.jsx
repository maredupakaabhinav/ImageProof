import React, { useState } from 'react';
import { ShieldCheck, RotateCcw, AlertCircle } from 'lucide-react';
import { resetAllData } from '../services/api';

export default function Footer({ onDataReset }) {
  const [resetting, setResetting] = useState(false);

  const handleReset = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to reset all records and clear uploaded images?\n\nThis will restore the database to an empty state for a fresh demonstration."
    );
    if (!confirmed) return;

    try {
      setResetting(true);
      await resetAllData();
      alert("ImageProof database and test files reset successfully.");
      if (onDataReset) onDataReset();
    } catch (err) {
      alert("Failed to reset database: " + err.message);
    } finally {
      setResetting(false);
    }
  };

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
            <ShieldCheck size={16} color="var(--accent-blue)" />
            <span>ImageProof Forensics & Incident Response Platform</span>
          </div>
          <div>Digital Evidence Authenticity & Cryptographic Verification Suite</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '0.2rem' }}>
            Complies with ISO/IEC 27037 (Digital Evidence Handling) & NIST SP 800-86 standards.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            onClick={handleReset} 
            className="btn btn-outline"
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}
            disabled={resetting}
            title="Purge analysis records and clear temporary investigation files"
          >
            <RotateCcw size={12} className={resetting ? 'spin' : ''} />
            <span>{resetting ? 'Purging...' : 'Purge Evidence Cache'}</span>
          </button>
        </div>
      </div>
    </footer>
  );
}
