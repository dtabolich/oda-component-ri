const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();

const smsService = require('./services/sms');

const app = express();
const PORT = process.env.PORT || 4436;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'kratos-sms-service' });
});

// SMS sending endpoint (called by Kratos courier)
app.post('/sms/send', async (req, res) => {
  try {
    const { to, body } = req.body;

    if (!to || !body) {
      return res.status(400).json({
        error: 'Missing required fields: to, body',
      });
    }

    console.log(`Sending SMS to ${to}: ${body}`);

    // Send SMS using configured provider
    const result = await smsService.sendSMS(to, body);

    res.json({
      success: true,
      messageId: result.messageId,
      provider: result.provider,
    });
  } catch (error) {
    console.error('SMS sending error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// Verification callback (optional, for delivery status)
app.post('/sms/callback', (req, res) => {
  console.log('SMS delivery callback:', req.body);
  res.json({ received: true });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    error: err.message || 'Internal Server Error',
  });
});

app.listen(PORT, () => {
  console.log(`Kratos SMS Service running on http://localhost:${PORT}`);
  console.log(`SMS Provider: ${process.env.SMS_PROVIDER || 'mock'}`);
});
