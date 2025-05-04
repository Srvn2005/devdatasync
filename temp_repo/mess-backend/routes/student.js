const express = require('express');
const router = express.Router();
const {
    placeOrder,
    getMyOrders,
    updateTodayOrder,
    deleteTodayOrder
} = require('../controllers/orderController');
const { verifyToken, isStudent } = require('../middleware/authMiddleware');

router.post('/order', verifyToken, isStudent, placeOrder);
router.get('/my-orders', verifyToken, isStudent, getMyOrders);
router.put('/order/edit', verifyToken, isStudent, updateTodayOrder);
router.delete('/order', verifyToken, isStudent, deleteTodayOrder); // ✅ new route

module.exports = router;
