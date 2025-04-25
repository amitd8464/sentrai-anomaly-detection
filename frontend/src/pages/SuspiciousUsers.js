
import React, { useEffect, useState } from 'react';

export default function SuspiciousUsers() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetch('/api/suspicious-users')
      .then(res => res.json())
      .then(data => setSessions(data))
      .catch(err => console.error('Error loading sessions:', err));
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Suspicious Users (Transformer)</h2>
      {sessions.map((sess, i) => (
        <div key={i} style={{ marginBottom: '2rem', borderBottom: '1px solid #ccc' }}>
          <h4>User: {sess.user_id} | Session #{sess.session_index}</h4>
          <p>Anomaly Score: <strong>{sess.anomaly_score}</strong> | Predicted: {sess.predicted_label}</p>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Location</th>
                <th>Device</th>
                <th>Hour</th>
                <th>Files Accessed</th>
              </tr>
            </thead>
            <tbody>
              {sess.logs.map((log, j) => (
                <tr key={j}>
                  <td>{log.timestamp}</td>
                  <td>{log.action_type}</td>
                  <td>{log.resource}</td>
                  <td>{log.location}</td>
                  <td>{log.device}</td>
                  <td>{log.hour_of_day}</td>
                  <td>{log.num_files_accessed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
