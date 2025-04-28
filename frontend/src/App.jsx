export default function App() {
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