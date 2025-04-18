import React, { useState } from 'react';
import APIClient from '../api/api';

export default function AnomalyDetector() {
  const [jsonData, setJsonData] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = () => {
    try {
      const parsed = JSON.parse(jsonData);
      APIClient.post('/detect-anomalies', parsed)
        .then(res => setResult(res.data));
    } catch (e) {
      alert("Invalid JSON");
    }
  };

  return (
    <div>
      <h2>Detect Anomalies</h2>
      <textarea
        rows="10"
        cols="60"
        placeholder="Paste JSON array of logs here"
        value={jsonData}
        onChange={e => setJsonData(e.target.value)}
      />
      <br />
      <button onClick={handleSubmit}>Detect</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
