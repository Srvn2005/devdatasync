import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import MenuManager from '../components/MenuManager';
import axios from 'axios'; // If you're not using a separate axios instance


const OrganizerDashboard = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(true);
  const [orderSummary, setOrderSummary] = useState({});

  // Auth & Role Check
  useEffect(() => {
    const role = localStorage.getItem('role');
    const user = localStorage.getItem('name');
    const token = localStorage.getItem('token');

    console.log("Token:", token);
    console.log("Role:", role);
    console.log("Name:", user);

    if (!token || role !== 'organizer') {
      navigate('/');
    } else {
      setName(user);
    }

    setLoading(false);
  }, [navigate]);

  // Fetch summary data
  useEffect(() => {
    const fetchSummary = async () => {
      const token = localStorage.getItem('token');
  
      try {
        const res = await axios.get('http://localhost:5000/api/orders/summary', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setOrderSummary(res.data);
        console.log("Order Summary:", res.data);
      } catch (err) {
        console.error("Failed to fetch order summary", err);
      }
    };
  
    fetchSummary();
    const interval = setInterval(fetchSummary, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);
  if (loading) return <p>Loading dashboard...</p>;

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', backgroundColor: '#5c3626', minHeight: '100vh', color: 'white' }}>
      
      <h1 style={{ textAlign: 'center', paddingTop: '20px' }}>Organizer Dashboard</h1>
      <p style={{ textAlign: 'center' }}>👀 This should show before MenuManager renders.</p>

      {/* All Student Orders Summary Section */}
      <div style={{
        backgroundColor: '#794832',
        maxWidth: '400px',
        margin: '30px auto',
        padding: '20px',
        borderRadius: '10px',
        textAlign: 'center',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
      }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '10px' }}>All Student Orders</h2>
        <button style={{
          backgroundColor: '#ff5c33',
          border: 'none',
          padding: '8px 16px',
          borderRadius: '5px',
          color: 'white',
          fontWeight: 'bold',
          cursor: 'pointer',
          marginBottom: '15px'
        }}>
          View All Orders
        </button>

        {Object.keys(orderSummary).length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {Object.entries(orderSummary).map(([key, value], idx) => (
              <li key={idx} style={{ marginBottom: '5px', fontSize: '16px' }}>
                • {key}: {value}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontSize: '14px' }}>No orders yet.</p>
        )}
      </div>

      {/* Render Menu Manager Below */}
      <MenuManager />
    </div>
  );
};

export default OrganizerDashboard;
