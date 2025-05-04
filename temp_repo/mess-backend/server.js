const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const organizerRoutes = require('./routes/organizer');
const studentRoutes = require('./routes/student');
const orderRoutes = require('./routes/orders');




const app = express();
app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => console.log('MongoDB connected'))
.catch(err => console.error(err));

app.use('/api/auth', authRoutes);
app.use('/api', organizerRoutes);
app.use('/api/student', studentRoutes);
app.use('/api/orders', orderRoutes);


const PORT = process.env.PORT || 5000;
app.listen(PORT,'0.0.0.0', () => console.log(`Server running on port ${PORT}`));
// Triggering backend workflow
// At the end of server.js
module.exports = app; // For testing
