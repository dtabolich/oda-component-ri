# Ory Kratos Passwordless Phone Authentication

Complete implementation of browser-based passwordless phone authentication using Ory Kratos 25.0.4.

## Overview

This implementation provides a complete authentication system where users can:

1. **Login with phone number** - Passwordless authentication using phone as identity
2. **Automatic registration redirect** - If identity doesn't exist, automatically redirect to registration
3. **Phone verification** - SMS-based verification after registration
4. **Modern UI** - Clean, responsive browser-based interface

## Architecture

### Components

- **Ory Kratos** - Identity and authentication server
- **UI Service** - Express.js application for browser flows
- **SMS Service** - Handles SMS sending via multiple providers
- **PostgreSQL** - Identity data storage

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Flow                            │
└─────────────────────────────────────────────────────────────┘

1. Login Attempt
   └─▶ User enters phone → Kratos checks identity
       ├─▶ Exists: Send SMS code → Verify → Dashboard
       └─▶ Not exists: Redirect to Registration

2. Registration Flow
   └─▶ Confirm phone → Create identity → Send SMS code
       └─▶ Verify phone → Dashboard
```

## Directory Structure

```
KratosAuth/
├── config/
│   ├── kratos.yml                 # Kratos configuration
│   └── identity.schema.json       # Identity schema (phone-based)
├── ui/
│   ├── index.js                   # Express server
│   ├── routes/
│   │   └── kratos.js              # Route handlers for flows
│   ├── views/
│   │   ├── login.ejs              # Login page
│   │   ├── registration.ejs       # Registration page
│   │   ├── verification.ejs       # Verification page
│   │   ├── dashboard.ejs          # Dashboard
│   │   └── error.ejs              # Error page
│   ├── public/
│   │   ├── css/style.css          # Styles
│   │   └── js/main.js             # Client-side JS
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── index.js                   # SMS service
│   ├── services/
│   │   └── sms.js                 # SMS providers
│   ├── package.json
│   └── Dockerfile
└── deployment/
    └── (Kubernetes manifests)
```

## Quick Start

### Local Development

#### 1. Start Kratos

```bash
cd config
docker run --rm -it \
  -p 4433:4433 \
  -p 4434:4434 \
  -v $(pwd):/etc/config/kratos \
  oryd/kratos:v1.0.4 \
  serve all --config /etc/config/kratos/kratos.yml
```

#### 2. Start SMS Service

```bash
cd backend
cp .env.example .env
npm install
npm start
```

The SMS service will use mock mode by default. Check the terminal for verification codes.

#### 3. Start UI Service

```bash
cd ui
cp .env.example .env
npm install
npm start
```

#### 4. Test the Flow

1. Open http://localhost:3000
2. Try to login with a phone number: `+1234567890`
3. Since the identity doesn't exist, you'll be redirected to registration
4. Confirm the phone number
5. Check the SMS service terminal for the verification code
6. Enter the code
7. Access the dashboard

### Docker Compose

```bash
# From the KratosAuth directory
docker-compose up
```

## Configuration

### Environment Variables

#### UI Service (.env)

```bash
PORT=3000
KRATOS_PUBLIC_URL=http://localhost:4433
KRATOS_ADMIN_URL=http://localhost:4434
SESSION_SECRET=change-me-in-production
NODE_ENV=development
```

#### SMS Service (.env)

```bash
PORT=4436
SMS_PROVIDER=mock  # Options: mock, twilio, aws-sns, vonage

# For Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# For AWS SNS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# For Vonage
VONAGE_API_KEY=your_api_key
VONAGE_API_SECRET=your_api_secret
VONAGE_FROM_NUMBER=YourBrand
```

## SMS Providers

### Mock Provider (Development)

The mock provider prints SMS messages to the console. Perfect for development.

```bash
SMS_PROVIDER=mock
```

Output example:
```
==================================================
📱 MOCK SMS SENT
==================================================
To: +1234567890
Message: Your verification code is 123456
==================================================
🔑 VERIFICATION CODE: 123456
==================================================
```

### Twilio (Production)

1. Sign up at https://www.twilio.com
2. Get Account SID, Auth Token, and Phone Number
3. Configure:

```bash
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### AWS SNS (Production)

1. Configure AWS SNS with SMS capabilities
2. Create IAM user with SNS permissions
3. Configure:

```bash
SMS_PROVIDER=aws-sns
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Vonage (Production)

1. Sign up at https://www.vonage.com
2. Get API Key and Secret
3. Configure:

```bash
SMS_PROVIDER=vonage
VONAGE_API_KEY=your_api_key
VONAGE_API_SECRET=your_api_secret
VONAGE_FROM_NUMBER=YourBrand
```

## User Flows

### Login Flow

```javascript
// 1. User visits /login
GET /login
  → Kratos creates login flow
  → Returns flow UI with phone input

// 2. User submits phone
POST /login?flow={flowId}
  body: { phone: "+1234567890", method: "code" }
  → Kratos checks if identity exists
  
  // Case A: Identity exists
  → Kratos sends SMS with code
  → User enters code
  → POST /login with code
  → Success → Redirect to /dashboard
  
  // Case B: Identity doesn't exist
  → Error 4000007 (identity not found)
  → Redirect to /registration?phone=+1234567890
```

### Registration Flow

```javascript
// 1. User visits /registration (with pre-filled phone from login)
GET /registration?phone=+1234567890
  → Kratos creates registration flow
  → Returns flow UI with phone pre-filled

// 2. User confirms phone and submits
POST /registration?flow={flowId}
  body: { "traits.phone": "+1234567890", method: "code" }
  → Kratos creates identity
  → Returns continue_with: [{ action: "show_verification_ui" }]
  → Redirect to /verification

// 3. Verification
GET /verification?flow={flowId}
  → Kratos sends SMS with verification code
  → User enters code
  
POST /verification?flow={flowId}
  body: { code: "123456" }
  → Kratos verifies code
  → Success → Redirect to /dashboard
```

## Customization

### Adding Extra Fields to Identity

Edit `config/identity.schema.json`:

```json
{
  "properties": {
    "traits": {
      "properties": {
        "phone": { ... },
        "name": {
          "type": "object",
          "properties": {
            "first": { "type": "string" },
            "last": { "type": "string" }
          }
        },
        "email": {
          "type": "string",
          "format": "email"
        }
      },
      "required": ["phone"]
    }
  }
}
```

### Styling

Modify `ui/public/css/style.css` to match your brand:

```css
:root {
  --primary-color: #5469d4;  /* Your brand color */
  --primary-hover: #4355c4;
  /* ... */
}
```

### Customizing Messages

Edit `config/kratos.yml` to customize SMS templates and messages.

## Production Deployment

### Security Checklist

- [ ] Change all secrets in `kratos.yml`
- [ ] Use PostgreSQL instead of memory storage
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Use production SMS provider
- [ ] Set up rate limiting
- [ ] Configure session security
- [ ] Enable audit logging

### Helm Deployment

See `/workspace/charts/KratosAuth/README.md` for Kubernetes deployment.

```bash
helm install kratos-auth ./charts/KratosAuth \
  -f production-values.yaml \
  -n auth
```

## API Reference

### Kratos SDK Usage

```javascript
const { Configuration, FrontendApi } = require('@ory/client');

const kratos = new FrontendApi(
  new Configuration({
    basePath: 'http://localhost:4433',
    baseOptions: { withCredentials: true }
  })
);

// Create login flow
const flow = await kratos.createBrowserLoginFlow();

// Submit login
await kratos.updateLoginFlow({
  flow: flowId,
  updateLoginFlowBody: {
    method: 'code',
    identifier: '+1234567890'
  }
});
```

## Troubleshooting

### Issue: SMS not received

**Solution**: Check SMS service logs:

```bash
# In mock mode, code is printed to console
npm start  # Check terminal output

# In production, check provider credentials
echo $TWILIO_AUTH_TOKEN
```

### Issue: "Flow expired" error

**Solution**: Flows expire after 10 minutes. Redirect user to create new flow:

```javascript
if (error.response?.status === 410) {
  return res.redirect('/login');
}
```

### Issue: CORS errors

**Solution**: Add your frontend URL to Kratos config:

```yaml
serve:
  public:
    cors:
      enabled: true
      allowed_origins:
        - "http://your-frontend.com"
```

### Issue: Session not persisting

**Solution**: Ensure cookies are properly configured:

```yaml
session:
  cookie:
    domain: "your-domain.com"
    same_site: Lax
    persistent: true
```

## Testing

### Unit Tests

```bash
# Backend
cd backend
npm test

# UI
cd ui
npm test
```

### Integration Tests

```bash
# Start all services
docker-compose up

# Run tests
npm run test:integration
```

## References

- [Ory Kratos Documentation](https://www.ory.sh/docs/kratos)
- [Ory Kratos GitHub](https://github.com/ory/kratos)
- [Code-based Authentication](https://www.ory.sh/docs/kratos/passwordless/code)
- [Self-Service Flows](https://www.ory.sh/docs/kratos/self-service)

## License

Apache 2.0
