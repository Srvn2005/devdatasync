// routes/orders.js
const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');
const { verifyToken, isStudent } = require('../middleware/authMiddleware'); // ✅ import middleware

// Routes
router.get('/summary', verifyToken, orderController.getAllStudentOrders); // or use isOrganizer here

// 👇 Secure these routes
router.post('/place', verifyToken, isStudent, orderController.placeOrder);
router.get('/my-orders', verifyToken, isStudent, orderController.getMyOrders);
router.put('/order/edit', verifyToken, isStudent, orderController.updateTodayOrder);
router.delete('/order/delete', verifyToken, isStudent, orderController.deleteTodayOrder);

module.exports = router;
