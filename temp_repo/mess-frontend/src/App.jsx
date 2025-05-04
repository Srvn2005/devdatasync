import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import OrganizerDashboard from './pages/OrganizerDashboard';
import Layout from './components/Layout';



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><Login /></Layout>} />
        <Route path="/register" element={<Layout><Register /></Layout>} />
        <Route path="/student" element={<Layout><StudentDashboard /></Layout>} />
        <Route path="/organizer" element={<Layout><OrganizerDashboard /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;
