import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import AllLogs from './pages/AllLogs';
import FlaggedLogs from './pages/FlaggedLogs';
import FlaggedUsers from './pages/FlaggedUsers';
import UserSessions from './pages/UserSessions';

function App() {
    return (
      <Router>
        <div className="flex">
          <Sidebar />
          <div className="flex-1 bg-gray-100 min-h-screen">
            <Routes>
              <Route path="/logs" element={<AllLogs />} />
              <Route path="/flagged-logs" element={<FlaggedLogs />} />
              <Route path="/flagged-users" element={<FlaggedUsers />} />
              <Route path="/flagged-users/:userId" element={<UserSessions />} />
            </Routes>
          </div>
        </div>
      </Router>
    );
  }
  
  export default App;