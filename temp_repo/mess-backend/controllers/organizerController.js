const MenuItem = require('../models/MenuItem');
const Order = require('../models/Order');

// Add new food item
exports.addMenuItem = async (req, res) => {
    const { name, mealType } = req.body;

    try {
        const newItem = new MenuItem({ name, mealType });
        await newItem.save();
        res.status(201).json({ msg: "Menu item added successfully" });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Error adding item" });
    }
};

// Get full menu
exports.getMenu = async (req, res) => {
    try {
        const items = await MenuItem.find();
        const grouped = { morning: [], afternoon: [], night: [] };

        items.forEach(item => {
            grouped[item.mealType].push(item.name);
        });

        res.json(grouped);
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Error fetching menu" });
    }
};

// Get all orders with meal-wise item counts
exports.getAllOrders = async (req, res) => {
    try {
        const orders = await Order.find();
        const itemCounts = {};

        orders.forEach(order => {
            ['morning', 'afternoon', 'night'].forEach(meal => {
                const mealItem = order[meal];
                if (mealItem && mealItem.item) {
                    const { item, qty } = mealItem;
                    if (!itemCounts[item]) itemCounts[item] = {};
                    if (!itemCounts[item][meal]) itemCounts[item][meal] = 0;
                    itemCounts[item][meal] += qty;
                }
            });
        });

        res.json(itemCounts);
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Error fetching orders" });
    }
};

exports.updateMenuItem = async (req, res) => {
    const menuItemId = req.params.id;
    const { name, mealType } = req.body;

    try {
        const updatedItem = await MenuItem.findByIdAndUpdate(
            menuItemId,
            { name, mealType },
            { new: true } // return the updated document
        );

        if (!updatedItem) {
            return res.status(404).json({ msg: 'Menu item not found' });
        }

        res.json({ msg: 'Menu item updated', item: updatedItem });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: 'Error updating item' });
    }
};



exports.deleteMenuItemByName = async (req, res) => {
    const { name, mealType } = req.query;

    if (!name || !mealType) {
        return res.status(400).json({ msg: "Missing name or mealType" });
    }

    try {
        const deleted = await MenuItem.findOneAndDelete({ name, mealType });

        if (!deleted) {
            return res.status(404).json({ msg: "Menu item not found" });
        }

        res.json({ msg: "Menu item deleted successfully", item: deleted });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Error deleting menu item" });
    }
};

exports.bulkAddMenuItems = async (req, res) => {
    const items = req.body;

    if (!Array.isArray(items) || items.length === 0) {
        return res.status(400).json({ msg: "Request body must be a non-empty array." });
    }

    const validMealTypes = ['morning', 'afternoon', 'night'];
    const invalidItems = items.filter(
        item => !item.name || !validMealTypes.includes(item.mealType)
    );

    if (invalidItems.length > 0) {
        return res.status(400).json({
            msg: "Some items are invalid. Each item must have 'name' and a valid 'mealType'.",
            invalidItems
        });
    }

    try {
        const inserted = await MenuItem.insertMany(items);
        res.status(201).json({ msg: "Menu items added successfully.", inserted });
    } catch (err) {
        console.error("❌ Bulk menu insert error:", err);
        res.status(500).json({ msg: "Server error" });
    }
};