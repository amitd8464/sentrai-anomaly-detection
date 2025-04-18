import React, { useEffect, useState } from 'react';
import APIClient from '../api/api';

export default function Detect() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Step 1: Get all logs
    APIClient.get('/logs')
      .then(res => {
        const allLogs = res.data;

        // Step 2: POST logs to /detect-anomalies
        return APIClient.post('/detect-anomalies', allLogs);
      })
      .then(response => {
        // Step 3: Set anomalies returned by backend
        console.log(response);
        setLogs(response.data.anomalies);  // make sure backend returns { anomalies: [...] }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);


  return (
    <div>
      <h2>Detected Anomalies</h2>
      {loading ? (
        <p>Loading...</p>
      ) : logs.length === 0 ? (
        <p>No anomalies found.</p>
      ) : (
        <table className="logs-table">
          <thead>
            <tr>
              {logs[0] && Object.keys(logs[0]).map((key, idx) => (
                <th key={idx}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={idx} className="anomaly-row">
                {Object.values(log).map((val, i) => (
                  <td key={i}>{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
