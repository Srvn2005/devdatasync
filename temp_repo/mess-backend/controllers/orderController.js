const Order = require('../models/Order');
const MenuItem = require('../models/MenuItem');

const validateOrderItemsAgainstMenu = async (order) => {
    const menuItems = await MenuItem.find();

    const validItems = {
        morning: new Set(menuItems.filter(i => i.mealType === 'morning').map(i => i.name)),
        afternoon: new Set(menuItems.filter(i => i.mealType === 'afternoon').map(i => i.name)),
        night: new Set(menuItems.filter(i => i.mealType === 'night').map(i => i.name))
    };

    if (
        (order.morning && !validItems.morning.has(order.morning.item)) ||
        (order.afternoon && !validItems.afternoon.has(order.afternoon.item)) ||
        (order.night && !validItems.night.has(order.night.item))
    ) {
        return false;
    }

    return true;
};


exports.placeOrder = async (req, res) => {
    const studentId = req.user.userId;
    const { morning, afternoon, night } = req.body;

    const isValid = await validateOrderItemsAgainstMenu({ morning, afternoon, night });
    if (!isValid) {
        return res.status(400).json({ msg: "Invalid order items: Item not in current menu." });
    }

    try {
        const newOrder = new Order({
            studentId,
            morning,
            afternoon,
            night
        });

        await newOrder.save();
        res.status(201).json({ msg: "Order placed successfully." });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Server error" });
    }
};


// View student’s orders
exports.getMyOrders = async (req, res) => {
    try {
        const orders = await Order.find({ studentId: req.user.studentId }).sort({ _id: -1 });
        res.json(orders);
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Server error" });
    }
};

// Update today’s order


exports.updateTodayOrder = async (req, res) => {
    const studentId = req.user.userId;
    const { morning, afternoon, night } = req.body;

    const isValid = await validateOrderItemsAgainstMenu({ morning, afternoon, night });
    if (!isValid) {
        return res.status(400).json({ msg: "Invalid update: Item not in current menu." });
    }

    const startOfToday = new Date();
    startOfToday.setHours(0, 0, 0, 0);
    const endOfToday = new Date();
    endOfToday.setHours(23, 59, 59, 999);

    try {
        const updated = await Order.findOneAndUpdate(
            {
                studentId,
                createdAt: { $gte: startOfToday, $lte: endOfToday }
            },
            { morning, afternoon, night },
            { new: true }
        );

        if (!updated) {
            return res.status(404).json({ msg: "No order found to update today." });
        }

        res.json({ msg: "Order updated", order: updated });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Server error" });
    }
};


exports.deleteTodayOrder = async (req, res) => {
    const studentId = req.user.userId;

    // Define today's start and end
    const startOfToday = new Date();
    startOfToday.setHours(0, 0, 0, 0);

    const endOfToday = new Date();
    endOfToday.setHours(23, 59, 59, 999);

    try {
        const deleted = await Order.findOneAndDelete({
            studentId,
            createdAt: { $gte: startOfToday, $lte: endOfToday }
        });

        if (!deleted) {
            return res.status(404).json({ msg: "No order found for today." });
        }

        res.json({ msg: "Order deleted successfully." });
    } catch (err) {
        console.error("❌ Error deleting order:", err);
        res.status(500).json({ msg: "Server error" });
    }
};

// controllers/orderController.js
exports.getAllStudentOrders = async (req, res) => {
    try {
      const startOfToday = new Date();
      startOfToday.setHours(0, 0, 0, 0);
  
      const endOfToday = new Date();
      endOfToday.setHours(23, 59, 59, 999);
  
      const orders = await Order.find({
        createdAt: { $gte: startOfToday, $lte: endOfToday }
      });
  
      const count = {};
  
      orders.forEach(order => {
        ['morning', 'afternoon', 'night'].forEach(meal => {
          const item = order[meal]?.item;
          const qty = order[meal]?.qty || 0;
  
          if (item) {
            const key = `${item.toLowerCase()}: ${meal.toUpperCase()}`;
            count[key] = (count[key] || 0) + qty;
          }
        });
      });
  
      res.json(count);
    } catch (err) {
      console.error(err);
      res.status(500).json({ msg: 'Server error' });
    }
  };
  