const mongoose = require('mongoose');

const MenuItemSchema = new mongoose.Schema({
    name: { type: String, required: true },
    mealType: { type: String, enum: ['morning', 'afternoon', 'night'], required: true }
});

module.exports = mongoose.model('MenuItem', MenuItemSchema);
