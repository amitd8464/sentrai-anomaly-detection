import React, { useEffect, useState } from 'react';
import APIClient from '../api/api';

export default function HealthStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    APIClient.get('/health')
      .then(res => setStatus(res.data))
      .catch(() => setStatus({ status: 'unhealthy', details: {} }));
  }, []);

  return (
    <div>
      <h2>System Health</h2>
      {status ? (
        <pre>{JSON.stringify(status, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}
