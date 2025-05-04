const express = require('express');
const router = express.Router();
const {
    addMenuItem,
    getMenu,
    getAllOrders,
    updateMenuItem,
    deleteMenuItemByName // ✅ include the function name here
} = require('../controllers/organizerController');

const { bulkAddMenuItems } = require('../controllers/organizerController');

router.post('/menu/add', addMenuItem);
router.get('/menu', getMenu);
router.get('/orders/all', getAllOrders);
router.put('/menu/:id', updateMenuItem);
router.delete('/menu', deleteMenuItemByName); // ✅ use query params for name & mealType

const { verifyToken, isOrganizer } = require('../middleware/authMiddleware');

// PUBLIC route: students and organizers can see menu
router.get('/menu', getMenu);

// PROTECTED routes — organizer only
router.post('/menu/add', verifyToken, isOrganizer, addMenuItem);
router.put('/menu/:id', verifyToken, isOrganizer, updateMenuItem);
router.delete('/menu', verifyToken, isOrganizer, deleteMenuItemByName);

// Organizer only can view all student orders
router.get('/orders/all', verifyToken, isOrganizer, getAllOrders);
router.post('/menu/bulk', verifyToken, isOrganizer, bulkAddMenuItems);


module.exports = router;
