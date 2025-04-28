export default function FlaggedLogs() {
    const [logs, setLogs] = useState([]);
  
    useEffect(() => {
      fetch('http://localhost:5000/anomaly/logs/flagged')
        .then(res => res.json())
        .then(data => setLogs(data));
    }, []);
  
    return (
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-4">Flagged Logs</h2>
        <div className="space-y-2">
          {logs.map((log, idx) => (
            <div key={idx} className="p-4 bg-white rounded shadow">{JSON.stringify(log)}</div>
          ))}
        </div>
      </div>
    );
  }