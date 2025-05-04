const jwt = require('jsonwebtoken');

exports.verifyToken = (req, res, next) => {
    const token = req.headers.authorization?.split(" ")[1];
    if (!token) return res.status(401).json({ msg: "Access Denied. No token provided." });

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded; // attach decoded user to request
        next();
    } catch (err) {
        return res.status(400).json({ msg: "Invalid Token" });
    }
};

exports.isOrganizer = (req, res, next) => {
    if (req.user.role !== 'organizer') {
        return res.status(403).json({ msg: "Access Denied: Organizers only" });
    }
    next();
};

exports.isStudent = (req, res, next) => {
    if (req.user.role !== 'student') {
        return res.status(403).json({ msg: "Access Denied: Students only" });
    }
    next();
};
