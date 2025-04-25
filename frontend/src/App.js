import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './pages/Dashboard';
import Logs from './pages/Logs';
import Detect from './pages/Detect';
import LogForm from './components/LogForm';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Topbar />
          <Routes>
          <Route path='/anomalous-logs' element={<AnomalousLogs />} />
          <Route path='/suspicious-users' element={<SuspiciousUsers />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/anomalies" element={<Detect />} />
            <Route path="/analyze-log" element={<LogForm />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
