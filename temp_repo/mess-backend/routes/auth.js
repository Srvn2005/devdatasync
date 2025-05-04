const express = require('express');
const router = express.Router();
const { loginUser, registerUser } = require('../controllers/authController');



// Temporary test route
router.get('/', (req, res) => {
  res.send('Auth API Working!');
});

// Your existing routes...
// router.post('/login', ...)
// router.post('/register', ...)

module.exports = router;

router.post('/login', loginUser);
router.post('/register', registerUser);

module.exports = router;
