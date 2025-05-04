const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

exports.loginUser = async (req, res) => {
    const { userId, password } = req.body;

    try {
        const user = await User.findOne({ userId });
        if (!user) return res.status(404).json({ msg: 'User not found' });

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).json({ msg: 'Invalid credentials' });

        const token = jwt.sign({ userId: user.userId, role: user.role }, process.env.JWT_SECRET, {
            expiresIn: '1d'
        });

        res.json({ token, role: user.role, name: user.userId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: 'Server error' });
    }
};

exports.registerUser = async (req, res) => {
    const { userId, password, role } = req.body;

    try {
        let userExists = await User.findOne({ userId });
        if (userExists) {
            return res.status(400).json({ msg: "User already exists" });
        }

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        const newUser = new User({
            userId,
            password: hashedPassword,
            role
        });

        await newUser.save();
        res.status(201).json({ msg: "User registered successfully" });
    } catch (err) {
        console.error(err);
        res.status(500).json({ msg: "Server error" });
    }
};
