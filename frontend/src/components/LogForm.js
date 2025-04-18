import React, { useState } from 'react';
import APIClient from '../api/api';
import './LogForm.css';

export default function LogForm() {
    const [timestamp, setTimestamp] = useState('');
    const [userId, setUserId] = useState('');
    const [actionType, setActionType] = useState('');
    const [resource, setResource] = useState('');
    const [location, setLocation] = useState('US');
    const [device, setDevice] = useState('laptop');
    const [hourOfDay, setHourOfDay] = useState('0');
    const [numFilesAccessed, setNumFiles] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        const log = {
            timestamp,
            user_id: Number(userId),
            action_type: actionType,
            resource,
            location,
            device,
            hour_of_day: Number(hourOfDay),
            num_files_accessed: Number(numFilesAccessed),
        };

        try {
            const res = await APIClient.post('/detect-anomaly', log);
            setResult(res.data);
        } catch (err) {
            setError('Failed to analyze log.');
            console.error(err);
        }
    };

    return (
        <div className="log-page-wrapper">
            <div className="log-form-container">
                <h2>Analyze Single Log</h2>

                <form className="log-form" onSubmit={handleSubmit}>
                    <label htmlFor="timestamp">Timestamp:</label>
                    <input
                        id="timestamp"
                        name="timestamp"
                        type="datetime-local"
                        value={timestamp}
                        onChange={e => setTimestamp(e.target.value)}
                        required
                    />

                    <label htmlFor="user_id">User ID:</label>
                    <input
                        id="user_id"
                        name="user_id"
                        type="number"
                        value={userId}
                        onChange={e => setUserId(e.target.value)}
                        required
                    />

                    <label htmlFor="action_type">Action Type:</label>
                    <input
                        id="action_type"
                        name="action_type"
                        type="text"
                        value={actionType}
                        onChange={e => setActionType(e.target.value)}
                        required
                    />

                    <label htmlFor="resource">Resource:</label>
                    <input
                        id="resource"
                        name="resource"
                        type="text"
                        value={resource}
                        onChange={e => setResource(e.target.value)}
                        required
                    />

                    <label htmlFor="location">Location:</label>
                    <select
                        id="location"
                        name="location"
                        value={location}
                        onChange={e => setLocation(e.target.value)}
                    >
                        <option value="US">US</option>
                        <option value="IN">IN</option>
                        <option value="UK">UK</option>
                    </select>

                    <label htmlFor="device">Device:</label>
                    <select
                        id="device"
                        name="device"
                        value={device}
                        onChange={e => setDevice(e.target.value)}
                    >
                        <option value="laptop">laptop</option>
                        <option value="mobile">mobile</option>
                        <option value="vpn">vpn</option>
                    </select>

                    <label htmlFor="hour_of_day">Hour of Day:</label>
                    <input
                        id="hour_of_day"
                        name="hour_of_day"
                        type="number"
                        min="0"
                        max="23"
                        value={hourOfDay}
                        onChange={e => setHourOfDay(e.target.value)}
                        required
                    />

                    <label htmlFor="num_files_accessed">Files Accessed:</label>
                    <input
                        id="num_files_accessed"
                        name="num_files_accessed"
                        type="number"
                        value={numFilesAccessed}
                        onChange={e => setNumFiles(e.target.value)}
                        required
                    />

                    <button type="submit">Check Anomaly</button>
                </form>

            </div>
            {error && <p className="error">{error}</p>}
            {result && (
                <div className="result">
                    <p>Score: {result.anomaly_score.toFixed(4)}</p>
                    <span
                        className={
                            result.is_anomalous ? 'badge anomalous' : 'badge normal'
                        }
                    >
                        {result.is_anomalous ? 'Anomalous' : 'Normal'}
                    </span>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}
