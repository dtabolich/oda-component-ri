const provider = process.env.SMS_PROVIDER || 'mock';

/**
 * Send SMS using configured provider
 * @param {string} to - Phone number in E.164 format
 * @param {string} body - Message body
 * @returns {Promise<{messageId: string, provider: string}>}
 */
async function sendSMS(to, body) {
  switch (provider.toLowerCase()) {
    case 'twilio':
      return sendTwilio(to, body);
    case 'aws-sns':
      return sendAWSSNS(to, body);
    case 'vonage':
      return sendVonage(to, body);
    case 'mock':
    default:
      return sendMock(to, body);
  }
}

/**
 * Send SMS via Twilio
 */
async function sendTwilio(to, body) {
  const twilio = require('twilio');
  const client = twilio(
    process.env.TWILIO_ACCOUNT_SID,
    process.env.TWILIO_AUTH_TOKEN
  );

  try {
    const message = await client.messages.create({
      body: body,
      from: process.env.TWILIO_PHONE_NUMBER,
      to: to,
    });

    return {
      messageId: message.sid,
      provider: 'twilio',
    };
  } catch (error) {
    console.error('Twilio error:', error);
    throw new Error(`Failed to send SMS via Twilio: ${error.message}`);
  }
}

/**
 * Send SMS via AWS SNS
 */
async function sendAWSSNS(to, body) {
  const AWS = require('aws-sdk');
  
  AWS.config.update({
    region: process.env.AWS_REGION || 'us-east-1',
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  });

  const sns = new AWS.SNS();

  try {
    const result = await sns.publish({
      Message: body,
      PhoneNumber: to,
      MessageAttributes: {
        'AWS.SNS.SMS.SMSType': {
          DataType: 'String',
          StringValue: 'Transactional',
        },
      },
    }).promise();

    return {
      messageId: result.MessageId,
      provider: 'aws-sns',
    };
  } catch (error) {
    console.error('AWS SNS error:', error);
    throw new Error(`Failed to send SMS via AWS SNS: ${error.message}`);
  }
}

/**
 * Send SMS via Vonage (formerly Nexmo)
 */
async function sendVonage(to, body) {
  const { Vonage } = require('@vonage/server-sdk');

  const vonage = new Vonage({
    apiKey: process.env.VONAGE_API_KEY,
    apiSecret: process.env.VONAGE_API_SECRET,
  });

  try {
    const result = await vonage.sms.send({
      to: to,
      from: process.env.VONAGE_FROM_NUMBER,
      text: body,
    });

    if (result.messages[0].status === '0') {
      return {
        messageId: result.messages[0]['message-id'],
        provider: 'vonage',
      };
    } else {
      throw new Error(result.messages[0]['error-text']);
    }
  } catch (error) {
    console.error('Vonage error:', error);
    throw new Error(`Failed to send SMS via Vonage: ${error.message}`);
  }
}

/**
 * Mock SMS sender for development/testing
 */
async function sendMock(to, body) {
  console.log('\n==================================================');
  console.log('📱 MOCK SMS SENT');
  console.log('==================================================');
  console.log(`To: ${to}`);
  console.log(`Message: ${body}`);
  console.log('==================================================\n');

  // Extract verification code if present
  const codeMatch = body.match(/\b\d{6}\b/);
  if (codeMatch) {
    console.log(`🔑 VERIFICATION CODE: ${codeMatch[0]}`);
    console.log('==================================================\n');
  }

  return {
    messageId: `mock_${Date.now()}`,
    provider: 'mock',
  };
}

module.exports = {
  sendSMS,
};
