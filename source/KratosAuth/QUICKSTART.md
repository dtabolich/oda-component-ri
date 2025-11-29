# Quick Start Guide

Get up and running with passwordless phone authentication in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local development)
- A phone number to test with

## Option 1: Docker Compose (Recommended)

### 1. Start All Services

```bash
cd /workspace/source/KratosAuth
docker-compose up
```

This starts:
- PostgreSQL (database)
- Kratos (authentication server)
- SMS Service (mock mode - prints codes to console)
- UI Service (web interface)

### 2. Open Browser

Visit http://localhost:3000

### 3. Test the Flow

#### Test Login → Registration Flow

1. Click "Login" or visit http://localhost:3000/login
2. Enter a phone number: `+1234567890`
3. Click "Send Code"
4. Since this identity doesn't exist, you'll be redirected to registration
5. Confirm the phone number and click "Continue"
6. You'll be redirected to verification
7. Check the SMS Service console output for the verification code:

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

8. Enter the code (e.g., `123456`)
9. You're now logged in and can see the dashboard!

#### Test Login with Existing Identity

1. Logout (click "Logout" button)
2. Try to login again with the same phone number: `+1234567890`
3. This time, you'll be sent directly to verification (no registration)
4. Check console for the new code
5. Enter the code
6. You're logged in!

## Option 2: Local Development

### 1. Start Kratos with Docker

```bash
cd /workspace/source/KratosAuth/config

docker run --rm -it \
  -p 4433:4433 \
  -p 4434:4434 \
  -v $(pwd):/etc/config/kratos \
  oryd/kratos:v1.0.4 \
  serve all --config /etc/config/kratos/kratos.yml
```

### 2. Start SMS Service

```bash
cd /workspace/source/KratosAuth/backend
npm install
npm start
```

### 3. Start UI Service

```bash
cd /workspace/source/KratosAuth/ui
npm install
npm start
```

### 4. Test

Open http://localhost:3000 and follow the flow above.

## Understanding the Flow

### What Happens During Login

```
User enters phone → Kratos checks if identity exists
│
├─ Identity exists:
│  └─ Send SMS code → User verifies → Login success
│
└─ Identity doesn't exist:
   └─ Redirect to registration → Create identity → Send SMS → Verify → Login success
```

### Key URLs

- **UI**: http://localhost:3000
- **Kratos Public API**: http://localhost:4433
- **Kratos Admin API**: http://localhost:4434
- **SMS Service**: http://localhost:4436

### Console Output

Watch these terminals:

1. **SMS Service Terminal** - Shows all SMS messages and codes
2. **Kratos Terminal** - Shows authentication flow logs
3. **UI Terminal** - Shows web requests

## Common Test Scenarios

### Scenario 1: New User Registration

```
1. Visit /login
2. Enter new phone: +1555123456
3. → Redirected to /registration?phone=+1555123456
4. Confirm phone
5. → Redirected to /verification
6. Get code from console
7. Enter code
8. → Logged in at /dashboard
```

### Scenario 2: Existing User Login

```
1. Visit /login
2. Enter existing phone: +1234567890
3. Get code from console
4. Enter code
5. → Logged in at /dashboard
```

### Scenario 3: Phone Verification Status

```
1. Register new user
2. Check dashboard - shows "Unverified"
3. Click "Verify now"
4. Enter verification code
5. Dashboard now shows "Verified ✓"
```

## Viewing the Data

### Check Kratos Database

```bash
# Using docker-compose
docker-compose exec postgres psql -U kratos -d kratos

# List identities
SELECT id, traits FROM identities;

# Check verifiable addresses
SELECT * FROM identity_verifiable_addresses;
```

### Using Kratos Admin API

```bash
# List all identities
curl http://localhost:4434/admin/identities

# Get specific identity
curl http://localhost:4434/admin/identities/{identity-id}
```

## Customization Quick Tips

### Change SMS Message

Edit `/workspace/source/KratosAuth/config/kratos.yml`:

```yaml
courier:
  templates:
    verification_code:
      subject: "Your Verification Code"
      body: |
        Hello! Your code is: {{ .Code }}
```

### Change UI Styling

Edit `/workspace/source/KratosAuth/ui/public/css/style.css`:

```css
:root {
  --primary-color: #your-color;  /* Change this */
}
```

### Add More Identity Fields

Edit `/workspace/source/KratosAuth/config/identity.schema.json`:

```json
{
  "traits": {
    "properties": {
      "phone": { ... },
      "email": {
        "type": "string",
        "format": "email",
        "title": "Email Address"
      }
    }
  }
}
```

## Next Steps

1. ✅ You've tested the basic flow
2. 📖 Read the [Implementation Guide](IMPLEMENTATION_GUIDE.md) for details
3. 🚀 Deploy to Kubernetes using the [Helm Chart](../../charts/KratosAuth/)
4. 🔐 Set up production SMS provider (Twilio, AWS SNS, or Vonage)
5. 🎨 Customize the UI to match your brand

## Troubleshooting

### Issue: SMS code not showing

**Check SMS service is running:**

```bash
curl http://localhost:4436/health
```

**Check logs:**

```bash
docker-compose logs sms-service
```

### Issue: "Flow expired" error

Flows expire after 10 minutes. Just refresh the page to start a new flow.

### Issue: Database connection error

**Check PostgreSQL is running:**

```bash
docker-compose ps postgres
```

**Check Kratos can connect:**

```bash
docker-compose logs kratos | grep -i database
```

### Issue: Can't access UI

**Check all services are running:**

```bash
docker-compose ps
```

Expected output:
```
NAME                STATUS
kratos-auth-ui-1           running
kratos-auth-kratos-1       running
kratos-auth-sms-service-1  running
kratos-auth-postgres-1     running
```

## Production Checklist

Before deploying to production:

- [ ] Change all secrets in configuration
- [ ] Set up real SMS provider (Twilio/AWS SNS/Vonage)
- [ ] Use PostgreSQL (not memory storage)
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and alerts
- [ ] Review rate limiting settings
- [ ] Test thoroughly with real phone numbers

## Help & Resources

- [Full Documentation](README.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Helm Chart README](../../charts/KratosAuth/README.md)
- [Ory Kratos Docs](https://www.ory.sh/docs/kratos)

## Example Phone Numbers for Testing

In mock mode, any phone number works:

- `+1234567890`
- `+14155552671`
- `+447700900123`
- `+33123456789`

Just make sure to use E.164 format (starting with `+` and country code).

---

**Ready to go?** Run `docker-compose up` and visit http://localhost:3000! 🚀
