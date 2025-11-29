const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const path = require('path');
require('dotenv').config();

const kratosRoutes = require('./routes/kratos');
const healthRoutes = require('./routes/health');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());

// Session configuration
app.use(
  session({
    secret: process.env.SESSION_SECRET || 'change-me-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
    },
  })
);

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Make session available to all views
app.use((req, res, next) => {
  res.locals.session = req.session;
  next();
});

// Routes
app.use('/', healthRoutes);
app.use('/', kratosRoutes);

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).render('error', {
    error: err.message || 'Internal Server Error',
    details: process.env.NODE_ENV === 'development' ? err : {},
  });
});

app.listen(PORT, () => {
  console.log(`Kratos Auth UI running on http://localhost:${PORT}`);
  console.log(`Kratos Public URL: ${process.env.KRATOS_PUBLIC_URL}`);
});
