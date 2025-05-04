import Navbar from './Navbar'; // assuming this path
import { useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
  const location = useLocation();

  // Don't show Navbar on login or register pages
  const hideNavbar = location.pathname === '/' || location.pathname === '/register';

  return (
    <div className="auth-wrapper">
      {!hideNavbar && <Navbar />}
      <div className="auth-container">
        {children}
      </div>
    </div>
  );
};

export default Layout;