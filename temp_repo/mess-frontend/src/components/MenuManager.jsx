import { useEffect, useState } from 'react';
import API from '../api/axiosInstance';

const MenuManager = () => {
  const [menu, setMenu] = useState([]);
  const [name, setName] = useState('');
  const [mealType, setMealType] = useState('morning');

  const fetchMenu = async () => {
    try {
      const res = await API.get('/menu');
      console.log("API /menu response:", res.data);
  
      // Convert { morning: [...], afternoon: [...], night: [...] }
      // into flat array of { name, mealType }
      const data = res.data;
      const flatMenu = [];
  
      for (const meal in data) {
        if (Array.isArray(data[meal])) {
          data[meal].forEach(item => {
            flatMenu.push({ name: item, mealType: meal });
          });
        }
      }
  
      setMenu(flatMenu);
    } catch (err) {
      console.error("Failed to fetch menu:", err);
      setMenu([]);
    }
  };
  
  


  const addItem = async () => {
    try {
      const res = await API.post('/menu/add', { name, mealType });
      console.log("✅ Item added:", res.data);
      setName('');
      setMealType('morning');
      fetchMenu(); // refresh after adding
    } catch (err) {
      console.error("❌ Add failed:", err.response?.data || err.message);
      alert(err.response?.data?.msg || 'Failed to add item');
    }
  };
  
  const removeItem = async (name, mealType) => {
    try {
      const res = await API.delete(`/menu?name=${name}&mealType=${mealType}`);
      console.log("🗑️ Item removed:", res.data);
      fetchMenu(); // refresh after removing
    } catch (err) {
      console.error("❌ Remove failed:", err.response?.data || err.message);
      alert(err.response?.data?.msg || 'Failed to remove item');
    }
  };

  useEffect(() => {
    fetchMenu();
  }, []);

  // Grouping the items safely
  const grouped = {
    morning: menu?.filter(m => m.mealType === 'morning') || [],
    afternoon: menu?.filter(m => m.mealType === 'afternoon') || [],
    night: menu?.filter(m => m.mealType === 'night') || [],
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>🍽️ Add Menu Item</h2>
      <input
        placeholder="Item name"
        value={name}
        onChange={e => setName(e.target.value)}
      />
      <select value={mealType} onChange={e => setMealType(e.target.value)}>
        <option value="morning">Morning</option>
        <option value="afternoon">Afternoon</option>
        <option value="night">Night</option>
      </select>
      <button onClick={addItem}>Add</button>

      <hr />

      {['morning', 'afternoon', 'night'].map(meal => (
        <div key={meal}>
          <h3>{meal.toUpperCase()} Menu</h3>
          <ul>
            {grouped[meal].length > 0 ? (
              grouped[meal].map(item => (
                <li key={item.name}>
                  {item.name}
                  <button onClick={() => removeItem(item.name, meal)}>❌ Remove</button>
                </li>
              ))
            ) : (
              <li>No items yet.</li>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default MenuManager;
