# Implementation Guide: Ory Kratos Passwordless Phone Authentication

This guide explains the implementation details of the browser-based passwordless phone authentication flow.

## Table of Contents

1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Flow Implementation](#flow-implementation)
4. [Code Structure](#code-structure)
5. [Integration Guide](#integration-guide)

## Overview

This implementation follows the Ory Kratos 25.0.4 documentation for browser-based flows with passwordless authentication using the `code` method.

### Key Features

- **Passwordless**: No passwords required, only phone numbers
- **Browser-based**: Full server-side rendering with proper session handling
- **Automatic flow transitions**: Seamlessly redirect from login to registration
- **Phone verification**: SMS-based verification after registration
- **Production-ready**: Includes proper error handling, security, and scalability

## Key Concepts

### 1. Self-Service Flows

Kratos uses self-service flows for all user interactions:

- **Login Flow**: Authenticate existing users
- **Registration Flow**: Create new identities
- **Verification Flow**: Verify contact information (phone)
- **Recovery Flow**: Account recovery (optional)

Each flow has two phases:
1. **Initialization**: Browser requests flow from Kratos
2. **Submission**: User submits form data to complete flow

### 2. Code Method (Passwordless)

The `code` method enables passwordless authentication:

```yaml
selfservice:
  methods:
    code:
      passwordless_enabled: true
      config:
        lifespan: 15m
```

How it works:
1. User provides identifier (phone number)
2. Kratos sends a one-time code via SMS
3. User enters code to authenticate

### 3. Identity Schema

The identity schema defines what information is stored:

```json
{
  "traits": {
    "phone": {
      "type": "string",
      "format": "tel",
      "ory.sh/kratos": {
        "credentials": {
          "code": {
            "identifier": true,
            "via": "sms"
          }
        }
      }
    }
  }
}
```

Key annotations:
- `identifier: true` - Use phone as login identifier
- `via: "sms"` - Send codes via SMS

### 4. Continue With Transitions

Kratos 25.0.4 introduces `continue_with` actions for flow transitions:

```json
{
  "continue_with": [
    {
      "action": "show_verification_ui",
      "flow": {
        "id": "flow-id-here"
      }
    }
  ]
}
```

This enables automatic redirect from registration to verification.

## Flow Implementation

### Login Flow

#### Step 1: Initialize Login Flow

```javascript
// GET /login
const response = await kratos.createBrowserLoginFlow({
  returnTo: req.query.return_to,
  cookie: req.header('cookie'),
});

// Redirect to /login?flow={flow.id}
res.redirect(`/login?flow=${response.data.id}`);
```

#### Step 2: Retrieve Flow

```javascript
// GET /login?flow={flowId}
const flow = await kratos.getLoginFlow({
  id: flowId,
  cookie: req.header('cookie'),
});

// Render form with flow data
res.render('login', { flow });
```

#### Step 3: Submit Phone Number

```html
<form method="POST" action="/login?flow={flowId}">
  <input name="phone" type="tel" />
  <input name="method" type="hidden" value="code" />
  <input name="csrf_token" type="hidden" value="{token}" />
  <button type="submit">Send Code</button>
</form>
```

```javascript
// POST /login?flow={flowId}
try {
  const response = await kratos.updateLoginFlow({
    flow: flowId,
    updateLoginFlowBody: {
      method: 'code',
      identifier: phone,
      csrf_token: csrf_token,
    },
  });
  
  // Flow updated, now show code input
  res.redirect(`/login?flow=${flowId}`);
} catch (error) {
  // Check if identity doesn't exist
  if (error.response?.data?.ui?.messages?.[0]?.id === 4000007) {
    // Redirect to registration with phone
    res.redirect(`/registration?phone=${encodeURIComponent(phone)}`);
  }
}
```

#### Step 4: Submit Code

```html
<form method="POST" action="/login?flow={flowId}">
  <input name="code" type="text" maxlength="6" />
  <input name="method" type="hidden" value="code" />
  <button type="submit">Verify</button>
</form>
```

```javascript
// POST /login?flow={flowId}
const response = await kratos.updateLoginFlow({
  flow: flowId,
  updateLoginFlowBody: {
    method: 'code',
    code: code,
  },
});

// Success - session cookie is set
res.redirect('/dashboard');
```

### Registration Flow

#### Step 1: Initialize Registration

```javascript
// GET /registration?phone=+1234567890
const response = await kratos.createBrowserRegistrationFlow({
  returnTo: req.query.return_to,
  cookie: req.header('cookie'),
});

res.redirect(`/registration?flow=${response.data.id}&phone=${phone}`);
```

#### Step 2: Submit Registration

```html
<form method="POST" action="/registration?flow={flowId}">
  <input name="traits.phone" type="tel" value="{prefilledPhone}" />
  <input name="method" type="hidden" value="code" />
  <button type="submit">Register</button>
</form>
```

```javascript
// POST /registration?flow={flowId}
const response = await kratos.updateRegistrationFlow({
  flow: flowId,
  updateRegistrationFlowBody: {
    method: 'code',
    traits: {
      phone: phone,
    },
  },
});

// Check for continue_with
if (response.data.continue_with) {
  const verificationAction = response.data.continue_with.find(
    action => action.action === 'show_verification_ui'
  );
  
  if (verificationAction) {
    // Redirect to verification flow
    res.redirect(`/verification?flow=${verificationAction.flow.id}`);
  }
}
```

### Verification Flow

#### Step 1: Display Verification

```javascript
// GET /verification?flow={flowId}
const flow = await kratos.getVerificationFlow({
  id: flowId,
  cookie: req.header('cookie'),
});

// Kratos automatically sends SMS code
res.render('verification', { flow });
```

#### Step 2: Submit Code

```javascript
// POST /verification?flow={flowId}
await kratos.updateVerificationFlow({
  flow: flowId,
  updateVerificationFlowBody: {
    method: 'code',
    code: code,
  },
});

// Success - phone is verified
res.redirect('/dashboard');
```

## Code Structure

### UI Service (`/ui`)

```
ui/
├── index.js                    # Express server setup
├── routes/
│   ├── kratos.js              # Kratos flow handlers
│   └── health.js              # Health check
├── views/
│   ├── login.ejs              # Login page
│   ├── registration.ejs       # Registration page
│   ├── verification.ejs       # Verification page
│   └── dashboard.ejs          # Protected page
└── public/
    ├── css/style.css          # Styles
    └── js/main.js             # Client-side JS
```

Key files:

**index.js** - Express server with session management
**routes/kratos.js** - Handles all Kratos flows
**views/*.ejs** - EJS templates for each page

### SMS Service (`/backend`)

```
backend/
├── index.js                    # Express server
└── services/
    └── sms.js                  # SMS provider abstraction
```

**services/sms.js** - Abstraction layer supporting:
- Twilio
- AWS SNS
- Vonage
- Mock (development)

### Configuration (`/config`)

**kratos.yml** - Main Kratos configuration
**identity.schema.json** - Identity schema definition

## Integration Guide

### Integrating with Your Application

#### Option 1: Proxy Setup

Use the UI service as an authentication proxy:

```nginx
# nginx.conf
location /auth {
  proxy_pass http://kratos-ui:3000;
  proxy_set_header Cookie $http_cookie;
}

location /api/kratos {
  proxy_pass http://kratos:4433;
}
```

Your app checks session:

```javascript
async function checkAuth(req, res, next) {
  try {
    const response = await fetch('http://kratos:4433/sessions/whoami', {
      headers: { cookie: req.header('cookie') }
    });
    
    if (response.ok) {
      req.user = await response.json();
      next();
    } else {
      res.redirect('/auth/login');
    }
  } catch (error) {
    res.redirect('/auth/login');
  }
}
```

#### Option 2: Custom UI

Build your own UI using the Kratos SDK:

```javascript
import { Configuration, FrontendApi } from '@ory/client';

const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.KRATOS_PUBLIC_URL,
    baseOptions: { withCredentials: true }
  })
);

// Your custom login component
async function handleLogin(phone) {
  // Create flow
  const flow = await kratos.createBrowserLoginFlow();
  
  // Submit phone
  await kratos.updateLoginFlow({
    flow: flow.data.id,
    updateLoginFlowBody: {
      method: 'code',
      identifier: phone
    }
  });
  
  // Show code input...
}
```

#### Option 3: Embedded UI

Embed the authentication pages in an iframe or modal:

```html
<iframe 
  src="http://auth.example.com/login" 
  id="auth-frame"
  style="width: 100%; height: 600px; border: none;"
></iframe>

<script>
  // Listen for authentication success
  window.addEventListener('message', (event) => {
    if (event.data.type === 'auth-success') {
      window.location.reload();
    }
  });
</script>
```

### Session Management

#### Check Current Session

```javascript
// In your application
app.use(async (req, res, next) => {
  try {
    const response = await fetch(`${KRATOS_PUBLIC_URL}/sessions/whoami`, {
      headers: { cookie: req.header('cookie') }
    });
    
    if (response.ok) {
      req.kratosSession = await response.json();
    }
  } catch (error) {
    req.kratosSession = null;
  }
  next();
});
```

#### Protect Routes

```javascript
function requireAuth(req, res, next) {
  if (!req.kratosSession) {
    return res.redirect('/login');
  }
  next();
}

app.get('/dashboard', requireAuth, (req, res) => {
  res.render('dashboard', {
    user: req.kratosSession.identity
  });
});
```

### SMS Provider Setup

#### Twilio

1. Sign up: https://www.twilio.com
2. Get credentials from console
3. Configure:

```bash
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

#### AWS SNS

1. Enable SNS in AWS Console
2. Create IAM user with `sns:Publish` permission
3. Configure:

```bash
SMS_PROVIDER=aws-sns
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAxxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
```

#### Vonage

1. Sign up: https://www.vonage.com
2. Get API credentials
3. Configure:

```bash
SMS_PROVIDER=vonage
VONAGE_API_KEY=xxxxx
VONAGE_API_SECRET=xxxxx
VONAGE_FROM_NUMBER=YourBrand
```

## Security Best Practices

1. **Use HTTPS in production** - All communication should be encrypted
2. **Secure secrets** - Use environment variables or secret management
3. **Rate limiting** - Prevent SMS abuse with rate limiting
4. **CSRF protection** - Always validate CSRF tokens
5. **Session security** - Configure secure, httpOnly cookies
6. **Input validation** - Validate phone numbers before processing
7. **Error handling** - Don't leak sensitive information in errors

## Troubleshooting

### Flow expired errors

Flows have a 10-minute lifespan. Handle expiration:

```javascript
try {
  await kratos.getLoginFlow({ id: flowId });
} catch (error) {
  if (error.response?.status === 410) {
    // Flow expired, create new one
    return res.redirect('/login');
  }
}
```

### CSRF token errors

Always include CSRF token in forms:

```javascript
const csrfToken = flow.ui.nodes.find(
  n => n.attributes.name === 'csrf_token'
)?.attributes.value;
```

### Cookie not set

Ensure `withCredentials: true` and proper CORS:

```javascript
const kratos = new FrontendApi(
  new Configuration({
    basePath: 'http://kratos:4433',
    baseOptions: {
      withCredentials: true  // Important!
    }
  })
);
```

## Testing

### Manual Testing

1. Start services: `docker-compose up`
2. Visit http://localhost:3000
3. Try login with `+1234567890`
4. Check SMS service logs for code
5. Complete verification

### Automated Testing

```javascript
// Example test with Playwright
test('login flow', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="phone"]', '+1234567890');
  await page.click('button[type="submit"]');
  
  // Get code from SMS service logs
  const code = await getCodeFromLogs();
  await page.fill('input[name="code"]', code);
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL('/dashboard');
});
```

## References

- [Ory Kratos Docs](https://www.ory.sh/docs/kratos)
- [Code-based Auth](https://www.ory.sh/docs/kratos/passwordless/code)
- [Browser Flows](https://www.ory.sh/docs/kratos/self-service/flows)
- [Continue With](https://www.ory.sh/docs/kratos/self-service/flows/continue-with)
