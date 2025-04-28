export default function UserSessions() {
    const { userId } = useParams();
    const [sessions, setSessions] = useState([]);
  
    useEffect(() => {
      fetch(`http://localhost:5000/anomaly/users/${userId}/suspicious_sessions`)
        .then(res => res.json())
        .then(data => setSessions(data));
    }, [userId]);
  
    return (
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-4">Suspicious Sessions for {userId}</h2>
        <div className="space-y-4">
          {sessions.map((session, idx) => (
            <div key={idx} className="p-4 bg-white rounded shadow">
              <h3 className="font-semibold mb-2">Anomaly Score: {session.anomaly_score}</h3>
              {session.logs.map((log, logIdx) => (
                <div key={logIdx} className="text-sm text-gray-700">{JSON.stringify(log)}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }