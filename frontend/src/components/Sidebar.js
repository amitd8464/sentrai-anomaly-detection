import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2>🧠 AI Anomaly</h2>
      <nav>
        <Link to="/">Dashboard</Link>
        <Link to="/logs">Logs</Link>
        <Link to="/anomalies">Anomalies</Link>
        <Link to="/analyze-log">Analyze Log</Link>
      </nav>
    </div>
  );
}
