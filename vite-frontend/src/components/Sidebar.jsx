import React from 'react';
import { Link } from 'react-router-dom';

export default function Sidebar() {
    return (
      <div className="w-64 h-screen bg-gray-800 text-white flex flex-col p-4">
        <h1 className="text-2xl font-bold mb-6">Anomaly Dashboard</h1>
        <Link className="mb-4 hover:text-gray-400" to="/logs">All Logs</Link>
        <Link className="mb-4 hover:text-gray-400" to="/flagged-logs">Flagged Logs</Link>
        <Link className="hover:text-gray-400" to="/flagged-users">Flagged Users</Link>
      </div>
    );
  }