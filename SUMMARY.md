# Summary: Ory Kratos Identity Creation and Verification

This document provides a comprehensive summary of the investigation into Ory Kratos (v25.4.0) regarding passwordless login and verification.

## Key Findings

### 1. Can Kratos Create Identities During Passwordless Login?

**❌ NO** - Ory Kratos does NOT automatically create identities during the login flow.

- **Login and Registration are separate flows** in Kratos
- The login flow requires that an identity already exists
- If an identity doesn't exist during login, it returns an error (`NewNoCodeAuthnCredentials`)
- There is no built-in mechanism to auto-create identities during login

**Workaround**: Handle "account not found" errors in your application and redirect users to the registration flow.

### 2. How Verification Works with Code Method

**✅ Automatic Verification** - When using the code method for registration:

1. User submits email/phone
2. Kratos sends a verification code
3. User enters the code
4. **Kratos automatically verifies the address** when the code is correct
5. The address is marked as `verified: true` in the database

This means **you don't need a separate verification step** for code-based registration - it's built into the registration process.

## Configuration Files Provided

This workspace now contains complete examples:

1. **KRATOS_VERIFICATION_SETUP.md** - Comprehensive guide on adding verification to registration
2. **VERIFICATION_HOOKS_QUICK_REFERENCE.md** - Quick reference for hooks and their effects
3. **kratos-verification-example.yml** - Complete Kratos configuration with verification
4. **identity.schema.json** - Example identity schema with verification extensions
5. **docker-compose.verification-example.yml** - Docker setup for testing
6. **README_VERIFICATION_TESTING.md** - Testing guide with curl commands

## Recommended Configuration

### For Passwordless Registration (Code Method)

```yaml
selfservice:
  flows:
    verification:
      enabled: true
      use: code
    
    registration:
      after:
        code:
          hooks:
            - hook: session  # Simple: user is verified and logged in
    
    login:
      after:
        code:
          hooks:
            - hook: require_verified_address  # Optional: extra security

  methods:
    code:
      passwordless_enabled: true  # Enables both login AND registration
      enabled: true
      config:
        lifespan: 15m
```

### Identity Schema

```json
{
  "email": {
    "type": "string",
    "format": "email",
    "ory.sh/kratos": {
      "credentials": {
        "code": {
          "identifier": true,
          "via": "email"
        }
      },
      "verification": {
        "via": "email"
      }
    }
  }
}
```

## Understanding the Hooks

### Registration Hooks

| Hook | What It Does | When to Use |
|------|--------------|-------------|
| `session` | Creates authenticated session | User logs in after registration |
| `show_verification_ui` | Shows verification success UI | Want to show custom verification page |
| None | No automatic login | User must login manually |

### Login Hooks

| Hook | What It Does | When to Use |
|------|--------------|-------------|
| `require_verified_address` | Blocks unverified users | Production apps requiring verified users |
| None | Allows any user to login | Not recommended |

## Important Insights

### 1. Code Method = Automatic Verification

When you use the code method for registration:
- ✅ The act of entering the correct code verifies the address
- ✅ No separate verification flow needed
- ✅ Address is marked verified in the database immediately

### 2. Verification vs. Code Method

- **Code Method**: Built-in verification through code entry
- **Verification Flow**: Separate flow for verifying addresses after the fact
- **Use Both**: Enable verification flow for manual verification when needed

### 3. Hook Order Matters

```yaml
hooks:
  - hook: show_verification_ui  # Executes first
  - hook: session               # Executes second
```

For best UX with code method: Use `session` hook only (simplest path).

### 4. Password vs. Code Registration

| Method | Verification | Recommended Hooks |
|--------|--------------|-------------------|
| Code | ✅ Automatic | `session` |
| Password | ❌ Manual needed | `show_verification_ui` |

## Getting Started

### Quick Start (5 minutes)

1. **Start the test environment**:
   ```bash
   docker-compose -f docker-compose.verification-example.yml up -d
   ```

2. **Open MailSlurper** to view codes: http://localhost:4436

3. **Test registration**:
   ```bash
   # Get flow
   FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')
   
   # Submit email
   curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
     -H "Content-Type: application/json" \
     -d '{"method":"code","traits":{"email":"test@example.com","accepted_tos":true}}'
   
   # Check MailSlurper for code, then submit it
   curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
     -H "Content-Type: application/json" \
     -d '{"method":"code","code":"123456","traits":{"email":"test@example.com","accepted_tos":true}}'
   ```

4. **Verify the identity**:
   ```bash
   curl -s http://localhost:4434/admin/identities | jq '.[] | {id, email: .traits.email, verified: .verifiable_addresses[0].verified}'
   ```

## Common Scenarios

### Scenario 1: Simple Passwordless App

**Goal**: Users register with email, get verified, and log in automatically.

**Config**:
```yaml
registration:
  after:
    code:
      hooks:
        - hook: session

methods:
  code:
    passwordless_enabled: true
```

**Result**: Streamlined UX, user verified and logged in one go.

### Scenario 2: Mixed Authentication (Password + Code)

**Goal**: Support both password and passwordless login with verification.

**Config**:
```yaml
registration:
  after:
    password:
      hooks:
        - hook: show_verification_ui
    code:
      hooks:
        - hook: session

login:
  after:
    password:
      hooks:
        - hook: require_verified_address
    code:
      hooks:
        - hook: require_verified_address

methods:
  password:
    enabled: true
  code:
    passwordless_enabled: true
```

**Result**: Password users must verify before login, code users auto-verified.

### Scenario 3: Maximum Security

**Goal**: All users must verify, no exceptions.

**Config**:
```yaml
registration:
  after:
    password:
      hooks:
        - hook: show_verification_ui
        # No session hook - user must verify before logging in
    code:
      hooks:
        - hook: session  # Code method auto-verifies

login:
  after:
    password:
      hooks:
        - hook: require_verified_address
    code:
      hooks:
        - hook: require_verified_address

security:
  account_enumeration:
    mitigate: true  # Prevent account enumeration attacks
```

**Result**: Maximum security, all users verified before full access.

## Production Checklist

Before deploying to production:

- [ ] Change all secrets in configuration
- [ ] Configure production SMTP/SMS provider
- [ ] Disable `leak_sensitive_values` in logs
- [ ] Enable account enumeration mitigation
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Configure proper CORS settings
- [ ] Customize email/SMS templates
- [ ] Set appropriate code lifespans
- [ ] Test recovery flow
- [ ] Set up monitoring and alerting
- [ ] Review security settings
- [ ] Test all flows in staging environment

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Your Application                   │
│          (Frontend + Backend Integration)            │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ API Calls
                  │
┌─────────────────▼───────────────────────────────────┐
│                  Ory Kratos                          │
│  ┌─────────────────────────────────────────────┐    │
│  │  Registration Flow (Code Method)            │    │
│  │  1. User submits email                      │    │
│  │  2. Code sent to email                      │    │
│  │  3. User enters code                        │    │
│  │  4. ✅ Email verified automatically          │    │
│  │  5. Hooks execute (session, etc.)           │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Login Flow                                 │    │
│  │  1. User enters email                       │    │
│  │  2. Code sent to email                      │    │
│  │  3. User enters code                        │    │
│  │  4. ✅ Login successful (if verified)        │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Verification Flow (Manual)                 │    │
│  │  1. User requests verification              │    │
│  │  2. Code sent to email                      │    │
│  │  3. User enters code                        │    │
│  │  4. ✅ Address verified                      │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ SMTP/SMS
                   │
┌──────────────────▼───────────────────────────────────┐
│         Courier (Email/SMS Service)                  │
│  - Sends verification codes                          │
│  - Sends recovery codes                              │
│  - Sends welcome emails                              │
└──────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **No Auto-Creation During Login**: Kratos doesn't create identities during login - use registration flow
2. **Code Method Auto-Verifies**: Code-based registration automatically verifies addresses
3. **Use Verification Flow**: Enable for manual verification and better UX
4. **Hooks Control Behavior**: Configure hooks to control session creation and verification UI
5. **Security First**: Use `require_verified_address` hook on login for production apps

## Next Steps

1. Review the provided configuration examples
2. Set up the test environment using Docker Compose
3. Test the registration flow with different hook configurations
4. Implement frontend to handle the flows
5. Customize email templates for your brand
6. Deploy to staging for testing
7. Deploy to production with proper security settings

## Support and Resources

- **Official Documentation**: https://www.ory.sh/docs/kratos
- **GitHub Repository**: https://github.com/ory/kratos
- **Community Slack**: https://slack.ory.sh
- **GitHub Discussions**: https://github.com/ory/kratos/discussions

## License

This documentation is provided as-is. Ory Kratos is licensed under Apache License 2.0.
