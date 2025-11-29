const express = require('express');
const router = express.Router();

// Health check endpoint
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'kratos-auth-ui',
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
