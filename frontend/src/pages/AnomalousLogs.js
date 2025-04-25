
import React, { useEffect, useState } from 'react';

export default function AnomalousLogs() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/api/anomalous-logs')
      .then(res => res.json())
      .then(data => setLogs(data))
      .catch(err => console.error('Error loading logs:', err));
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Anomalous Logs (SVM)</h2>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Action</th>
            <th>Resource</th>
            <th>Location</th>
            <th>Device</th>
            <th>Hour</th>
            <th>Files Accessed</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={i}>
              <td>{log.user_id}</td>
              <td>{log.action_type}</td>
              <td>{log.resource}</td>
              <td>{log.location}</td>
              <td>{log.device}</td>
              <td>{log.hour_of_day}</td>
              <td>{log.num_files_accessed}</td>
              <td>{log.anomaly_score?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
