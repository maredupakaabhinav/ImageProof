import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import AnalysisResult from './pages/AnalysisResult';
import History from './pages/History';

export default function App() {
  const [activePage, setActivePage] = useState('home');
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null);

  const handleDataReset = () => {
    setSelectedAnalysisId(null);
    setActivePage('dashboard');
  };

  return (
    <div className="app-container">
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      <main className="main-content">
        {activePage === 'home' && (
          <Home setActivePage={setActivePage} />
        )}

        {activePage === 'dashboard' && (
          <Dashboard 
            setActivePage={setActivePage} 
            setSelectedAnalysisId={setSelectedAnalysisId} 
          />
        )}

        {activePage === 'upload' && (
          <Upload 
            setActivePage={setActivePage} 
            setSelectedAnalysisId={setSelectedAnalysisId} 
          />
        )}

        {activePage === 'result' && (
          <AnalysisResult 
            analysisId={selectedAnalysisId} 
            setActivePage={setActivePage} 
          />
        )}

        {activePage === 'history' && (
          <History 
            setActivePage={setActivePage} 
            setSelectedAnalysisId={setSelectedAnalysisId} 
          />
        )}
      </main>

      <Footer onDataReset={handleDataReset} />
    </div>
  );
}
