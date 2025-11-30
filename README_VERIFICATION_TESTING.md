# Testing Ory Kratos Verification Setup

This guide helps you quickly test the Ory Kratos verification configuration.

## Quick Start

### 1. Start the Services

```bash
# Make sure you have the configuration files in the current directory
docker-compose -f docker-compose.verification-example.yml up -d
```

This starts:
- **Ory Kratos** (ports 4433 public, 4434 admin)
- **PostgreSQL** (port 5432)
- **MailSlurper** (port 4436) - Email catcher for viewing verification codes

### 2. Access MailSlurper

Open http://localhost:4436 in your browser to see emails that Kratos sends.

### 3. Test Registration Flow

#### Option A: Using curl

**Step 1: Initialize registration flow**

```bash
curl -s -X GET http://localhost:4433/self-service/registration/api | jq
```

Save the `flow.id` from the response.

**Step 2: Submit email for registration**

```bash
FLOW_ID="<flow-id-from-step-1>"

curl -s -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {
      "email": "test@example.com",
      "accepted_tos": true
    }
  }' | jq
```

**Step 3: Check MailSlurper for the code**

Go to http://localhost:4436 and check the email for the verification code.

**Step 4: Submit the code**

```bash
curl -s -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {
      "email": "test@example.com",
      "accepted_tos": true
    }
  }' | jq
```

You should receive a response with a session token and the identity.

#### Option B: Using Ory CLI

Install the Ory CLI:

```bash
bash <(curl https://raw.githubusercontent.com/ory/meta/master/install.sh) -b . ory
sudo mv ./ory /usr/local/bin/
```

Perform registration:

```bash
ory auth registration --project http://localhost:4433
```

### 4. Verify the Identity

Check if the email was verified:

```bash
# Get all identities
curl -s http://localhost:4434/admin/identities | jq

# Get specific identity
IDENTITY_ID="<identity-id-from-above>"
curl -s http://localhost:4434/admin/identities/$IDENTITY_ID | jq '.verifiable_addresses'
```

Look for `"verified": true` in the verifiable addresses.

## Testing Different Scenarios

### Scenario 1: Test Code Registration (Passwordless)

Update `kratos-verification-example.yml`:

```yaml
registration:
  after:
    code:
      hooks:
        - hook: session  # User is logged in after registration
```

**Expected behavior**: 
1. User submits email
2. Code is sent
3. User enters code
4. Email is verified automatically
5. Session is created
6. User is logged in

### Scenario 2: Test with Verification UI

Update `kratos-verification-example.yml`:

```yaml
registration:
  after:
    code:
      hooks:
        - hook: show_verification_ui
        - hook: session
```

**Expected behavior**:
1. User submits email
2. Code is sent
3. User enters code
4. Email is verified automatically
5. `continue_with` array includes `show_verification_ui` action
6. Session is created

The response will include:

```json
{
  "continue_with": [
    {
      "action": "show_verification_ui",
      "flow": {
        "id": "...",
        "url": "http://localhost:4455/verification?flow=..."
      }
    }
  ],
  "session": { ... }
}
```

### Scenario 3: Test Login with Verification Requirement

First, register a user with password (unverified):

```bash
# 1. Get registration flow
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

# 2. Register with password
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "password",
    "password": "SecurePassword123!",
    "traits": {
      "email": "unverified@example.com",
      "accepted_tos": true
    }
  }'
```

Now update config to require verification:

```yaml
login:
  after:
    password:
      hooks:
        - hook: require_verified_address
```

Try to login:

```bash
# 1. Get login flow
LOGIN_FLOW_ID=$(curl -s http://localhost:4433/self-service/login/api | jq -r '.id')

# 2. Attempt login
curl -X POST "http://localhost:4433/self-service/login?flow=$LOGIN_FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "password",
    "identifier": "unverified@example.com",
    "password": "SecurePassword123!"
  }' | jq
```

**Expected**: Login should fail or return a `continue_with` array with verification required.

## Viewing Verification Codes

### Method 1: MailSlurper UI

1. Open http://localhost:4436
2. View emails sent by Kratos
3. Find the verification code in the email body

### Method 2: Kratos Logs

Since we enabled `LOG_LEAK_SENSITIVE_VALUES=true` (dev only!), codes appear in logs:

```bash
docker-compose -f docker-compose.verification-example.yml logs -f kratos | grep "code"
```

### Method 3: Database

```bash
# Connect to PostgreSQL
docker exec -it <postgres-container-id> psql -U kratos

# View registration codes
SELECT * FROM identity_registration_codes;

# View login codes
SELECT * FROM identity_login_codes;

# View verification codes
SELECT * FROM identity_verification_codes;
```

## Common API Calls

### Create Identity (Admin API)

```bash
curl -X POST http://localhost:4434/admin/identities \
  -H "Content-Type: application/json" \
  -d '{
    "schema_id": "default",
    "traits": {
      "email": "admin-created@example.com",
      "accepted_tos": true
    },
    "verifiable_addresses": [
      {
        "value": "admin-created@example.com",
        "verified": true,
        "via": "email",
        "status": "completed"
      }
    ]
  }'
```

### List All Identities

```bash
curl -s http://localhost:4434/admin/identities | jq
```

### Get Specific Identity

```bash
curl -s http://localhost:4434/admin/identities/<identity-id> | jq
```

### Update Identity Verification Status

```bash
curl -X PATCH http://localhost:4434/admin/identities/<identity-id> \
  -H "Content-Type: application/json" \
  -d '{
    "schema_id": "default",
    "traits": {
      "email": "user@example.com",
      "accepted_tos": true
    },
    "verifiable_addresses": [
      {
        "value": "user@example.com",
        "verified": true,
        "via": "email",
        "status": "completed"
      }
    ]
  }'
```

### Delete Identity

```bash
curl -X DELETE http://localhost:4434/admin/identities/<identity-id>
```

### Initialize Verification Flow (Manual)

```bash
curl -s http://localhost:4433/self-service/verification/api | jq
```

### Submit Verification

```bash
FLOW_ID="<verification-flow-id>"

# Step 1: Submit email
curl -X POST "http://localhost:4433/self-service/verification?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "code"
  }' | jq

# Step 2: Submit code (check MailSlurper for code)
curl -X POST "http://localhost:4433/self-service/verification?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "123456",
    "method": "code"
  }' | jq
```

## Troubleshooting

### Issue: Emails not appearing in MailSlurper

**Check**:
1. Is MailSlurper running? `docker-compose ps`
2. Check Kratos logs: `docker-compose logs kratos`
3. Verify courier config points to MailSlurper:
   ```yaml
   courier:
     smtp:
       connection_uri: smtp://mailslurper:1025
   ```

### Issue: "Code not found" error

**Check**:
1. Code might have expired (default 15 minutes)
2. Code might have been used already (one-time use)
3. Flow might have expired
4. Check database for codes: `SELECT * FROM identity_registration_codes WHERE used_at IS NULL;`

### Issue: Registration flow expired

**Solution**: Restart the flow by getting a new flow ID.

### Issue: Verification not happening

**Check**:
1. Identity schema has `verification.via` extension
2. Verification flow is enabled: `verification.enabled: true`
3. Courier is properly configured
4. Check Kratos logs for errors

## Stopping Services

```bash
docker-compose -f docker-compose.verification-example.yml down

# Remove volumes (delete all data)
docker-compose -f docker-compose.verification-example.yml down -v
```

## Next Steps

1. **Implement Frontend**: Build a UI that handles the flows
2. **Customize Templates**: Modify email templates for your brand
3. **Add SMS**: Configure SMS provider for phone verification
4. **Production Config**: 
   - Use proper secrets
   - Disable `leak_sensitive_values`
   - Configure proper SMTP
   - Enable account enumeration mitigation
   - Set up proper CORS

## Resources

- [Ory Kratos Documentation](https://www.ory.sh/docs/kratos)
- [Self-Service Flows](https://www.ory.sh/docs/kratos/self-service)
- [Verification Flow](https://www.ory.sh/docs/kratos/self-service/flows/verify-email-account-activation)
- [Code Method](https://www.ory.sh/docs/kratos/passwordless)
- [Identity Schema](https://www.ory.sh/docs/kratos/manage-identities/identity-schema)
