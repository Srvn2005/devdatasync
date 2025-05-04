// models/Order.js
const mongoose = require('mongoose');

const OrderSchema = new mongoose.Schema({
  studentId: { type: String, required: true },
  morning: {
    item: String,
    qty: Number
  },
  afternoon: {
    item: String,
    qty: Number
  },
  night: {
    item: String,
    qty: Number
  }
}, { timestamps: true });

module.exports = mongoose.model('Order', OrderSchema);
