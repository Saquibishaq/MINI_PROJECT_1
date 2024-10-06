// app.js
const express = require('express');
const bodyParser = require('body-parser');
const videoRoutes = require('./routes/videoRoutes');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use('/video', videoRoutes); // Mount video routes

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
