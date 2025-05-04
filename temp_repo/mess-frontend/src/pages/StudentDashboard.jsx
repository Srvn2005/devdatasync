import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import API from '../api/axiosInstance';
import '../styles/StudentDashboard.css';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [menu, setMenu] = useState({ morning: [], afternoon: [], night: [] });
  const [order, setOrder] = useState({ morning: '', afternoon: '', night: '' });
  const [qty, setQty] = useState({ morning: 1, afternoon: 1, night: 1 });
  const [loading, setLoading] = useState(true);
  const [hasOrder, setHasOrder] = useState(false);

  useEffect(() => {
    const role = localStorage.getItem('role');
    const user = localStorage.getItem('name');
    const token = localStorage.getItem('token');

    if (!token || role !== 'student') {
      navigate('/');
    } else {
      setName(user);
      fetchMenu();
      fetchMyOrder();
    }
  }, []);

  const fetchMenu = async () => {
    try {
      const res = await API.get('/menu');
      setMenu(res.data);
    } catch (err) {
      console.error('Failed to fetch menu', err);
    }
  };

  const fetchMyOrder = async () => {
    try {
      const res = await API.get('/student/my-orders');
      const todayOrder = res.data[0];
      if (todayOrder) {
        setOrder({
          morning: todayOrder.morning?.item || '',
          afternoon: todayOrder.afternoon?.item || '',
          night: todayOrder.night?.item || '',
        });
        setQty({
          morning: todayOrder.morning?.qty || 1,
          afternoon: todayOrder.afternoon?.qty || 1,
          night: todayOrder.night?.qty || 1,
        });
        setHasOrder(true);
      }
    } catch (err) {
      console.error('No order found', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOrder = async () => {
    const payload = {
      morning: order.morning ? { item: order.morning, qty: qty.morning } : null,
      afternoon: order.afternoon ? { item: order.afternoon, qty: qty.afternoon } : null,
      night: order.night ? { item: order.night, qty: qty.night } : null,
    };

    try {
      if (hasOrder) {
        await API.put('/orders/order/edit', payload);
        alert('Order updated!');
      } else {
        await API.post('/orders/place', payload);
        alert('Order placed!');
        setHasOrder(true);
      }
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.msg || 'Failed to submit order');
    }
  };

  const handleDelete = async () => {
    try {
      await API.delete('/orders/order/delete');
      setOrder({ morning: '', afternoon: '', night: '' });
      setHasOrder(false);
      alert('Order deleted');
    } catch (err) {
      console.error(err);
      alert('Failed to delete order');
    }
  };

  if (loading) return <p className="loading-msg">Loading your dashboard...</p>;

  return (
    <div className="dashboard-container">
      
      <div className="dashboard-content">
        <h2>Welcome, {name} <span role="img" aria-label="wave">👋</span></h2>
        <h3>📋 Today’s Menu</h3>
        {['morning', 'afternoon', 'night'].map(meal => (
          <div key={meal} className="meal-section">
            <label className="meal-label">
              {meal.toUpperCase()}:
              <select
                value={order[meal]}
                onChange={e => setOrder({ ...order, [meal]: e.target.value })}
              >
                <option value="">-- Select --</option>
                {menu[meal]?.map((item, idx) => (
                  <option key={idx} value={item}>{item}</option>
                ))}
              </select>
              <input
                type="number"
                min="1"
                value={qty[meal]}
                onChange={e => setQty({ ...qty, [meal]: Number(e.target.value) })}
              />
            </label>
          </div>
        ))}
        <div className="button-group">
          <button onClick={handleOrder} className="order-btn">
            {hasOrder ? 'Update Order' : 'Place Order'}
          </button>
          {hasOrder && (
            <button onClick={handleDelete} className="delete-btn">
              Delete Order
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
