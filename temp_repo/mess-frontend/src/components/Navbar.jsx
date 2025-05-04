import { useNavigate } from 'react-router-dom';
import '../styles/Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem('role');
  const name = localStorage.getItem('name');

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <div className="navbar">
      <div className="navbar-left">
        <h2>🥗 Hostel Mess System</h2>
      </div>
      <div className="navbar-right">
        <span>{role?.toUpperCase()} | {name}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
};

export default Navbar;
