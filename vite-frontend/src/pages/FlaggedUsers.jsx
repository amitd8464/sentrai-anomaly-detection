import React from 'react';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function UserCard({ userId }) {
  return (
    <Link to={`/flagged-users/${userId}`} className="p-4 bg-white rounded shadow hover:bg-gray-100">
      <h3 className="text-lg font-semibold">{userId}</h3>
      <p className="text-gray-600">View Suspicious Sessions</p>
    </Link>
  );
}

export default function FlaggedUsers() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/anomaly/users/suspicious')
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Flagged Users</h2>
      <div className="grid grid-cols-2 gap-4">
        {users.map((user, idx) => (
          <UserCard key={idx} userId={user} />  // ✅ use UserCard here
        ))}
      </div>
    </div>
  );
}