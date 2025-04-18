import React, { useEffect, useState } from 'react';
import APIClient from '../api/api';
import './LogsTable.css';

export default function LogsTable() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        console.log("Fetching raw logs…");
        const logsRes = await APIClient.get('/logs');
        console.log("raw logs:", logsRes.data);

        console.log("Detecting anomalies…");
        const detectRes = await APIClient.post('/detect-anomalies', logsRes.data);
        console.log("annotated logs:", detectRes.data);

        const anomalies = detectRes.data.filter(l => l.is_anomalous === true);
        console.log("filtered anomalies:", anomalies);
        setLogs(anomalies);
      } catch (err) {
        console.error("Error loading logs:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <p>Loading logs…</p>;

  return (
    <div>
      <h2>Anomalous Logs</h2>
      {logs.length === 0 ? (
        <p>No anomalies found.</p>
      ) : (
        <table className="logs-table">
          <thead>
            <tr>
              {Object.keys(logs[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id || log.timestamp} className="anomaly-row">
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
