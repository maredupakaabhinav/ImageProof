import React, { useState, useEffect } from 'react';
import { Shield, LayoutDashboard, UploadCloud, History, Home, RefreshCw, CheckCircle2, AlertOctagon } from 'lucide-react';
import { checkBackendHealth } from '../services/api';

export default function Navbar({ activePage, setActivePage }) {
  const [backendStatus, setBackendStatus] = useState('checking'); // 'online' | 'offline' | 'checking'

  const verifyHealth = async () => {
    setBackendStatus('checking');
    const res = await checkBackendHealth();
    if (res.status === 'healthy') {
      setBackendStatus('online');
    } else {
      setBackendStatus('offline');
    }
  };

  useEffect(() => {
    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Analyze', icon: UploadCloud },
    { id: 'history', label: 'Case History', icon: History },
  ];

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div 
          className="brand-link" 
          onClick={() => setActivePage('home')}
          style={{ cursor: 'pointer' }}
        >
          <Shield className="brand-icon" />
          <div>
            <div>ImageProof</div>
            <span className="brand-subtitle">Digital Evidence Analyzer</span>
          </div>
        </div>

        <nav className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="system-status" title={backendStatus === 'online' ? 'Flask Backend Connected (127.0.0.1:5000)' : 'Backend Disconnected'}>
          <span className={`status-dot ${backendStatus === 'online' ? 'online' : 'offline'}`} />
          <span style={{ color: backendStatus === 'online' ? 'var(--color-success)' : 'var(--color-danger)' }}>
            {backendStatus === 'online' ? 'API Online' : backendStatus === 'checking' ? 'Connecting...' : 'API Offline'}
          </span>
          <button 
            onClick={verifyHealth}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            title="Refresh connection status"
          >
            <RefreshCw size={12} className={backendStatus === 'checking' ? 'spin' : ''} />
          </button>
        </div>
      </div>
    </header>
  );
}
