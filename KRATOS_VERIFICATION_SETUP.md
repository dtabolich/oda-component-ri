# How to Add Verification to Registration in Ory Kratos

This guide explains how to leverage Ory Kratos's built-in verification functionality for the registration flow, particularly with passwordless (code) authentication.

## Overview

Ory Kratos provides two main approaches for verification during registration:

1. **Automatic verification during code registration** - The code itself verifies the address
2. **Post-registration verification flow** - Redirect users to a verification UI after registration

## Understanding How Code Method Works

When using the `code` method for registration, **the address is automatically verified** when the user enters the correct code. This happens in the `registrationVerifyCode` function which calls `verifyAddress()` to mark the email/phone as verified.

However, you may still want to use verification hooks for better UX or additional verification requirements.

## Configuration Steps

### 1. Update Your Kratos Configuration File

Add verification configuration to your `kratos.yml`:

```yaml
selfservice:
  flows:
    # Enable verification flow
    verification:
      enabled: true
      use: code  # Use 'code' for OTP, or 'link' for email links
      ui_url: http://127.0.0.1:4455/verification  # Your verification UI
      after:
        default_browser_return_url: http://127.0.0.1:4455/welcome

    # Configure registration with verification hooks
    registration:
      ui_url: http://127.0.0.1:4455/registration
      lifespan: 10m
      after:
        # Configure hooks for different methods
        code:
          hooks:
            - hook: show_verification_ui  # Redirects to verification UI
            - hook: session               # Creates session for user
        password:
          hooks:
            - hook: show_verification_ui
            - hook: session

    # Configure login to require verified addresses
    login:
      ui_url: http://127.0.0.1:4455/login
      after:
        code:
          hooks:
            - hook: require_verified_address  # Prevents login with unverified address
        password:
          hooks:
            - hook: require_verified_address

  # Enable code method for passwordless
  methods:
    code:
      passwordless_enabled: true  # Enables BOTH login and registration with code
      enabled: true
      config:
        lifespan: 1h
        max_submissions: 5
    password:
      enabled: true
```

### 2. Update Your Identity Schema

Your identity schema must include the `verification` extension for the email/phone field:

```json
{
  "$id": "https://your-domain.com/identity.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Person",
  "type": "object",
  "properties": {
    "traits": {
      "type": "object",
      "properties": {
        "email": {
          "type": "string",
          "format": "email",
          "title": "Your E-Mail",
          "minLength": 3,
          "ory.sh/kratos": {
            "credentials": {
              "password": {
                "identifier": true
              },
              "code": {
                "identifier": true,
                "via": "email"
              }
            },
            "verification": {
              "via": "email"
            },
            "recovery": {
              "via": "email"
            }
          }
        },
        "phone": {
          "type": "string",
          "format": "tel",
          "title": "Phone Number",
          "ory.sh/kratos": {
            "credentials": {
              "code": {
                "identifier": true,
                "via": "sms"
              }
            },
            "verification": {
              "via": "sms"
            }
          }
        }
      },
      "required": ["email"],
      "additionalProperties": false
    }
  }
}
```

### 3. Configure Courier for Sending Codes

Configure the courier to send verification codes via email or SMS:

```yaml
courier:
  smtp:
    connection_uri: smtps://user:password@smtp.example.com:465/
    from_address: noreply@example.com
    from_name: Your App Name
  
  # For SMS (optional)
  sms:
    enabled: true
    request_config:
      url: https://api.your-sms-provider.com/send
      method: POST
      headers:
        Authorization: Bearer your-api-key
      body: |
        {
          "to": "{{ .To }}",
          "message": "Your verification code is: {{ .VerificationCode }}"
        }
```

## Available Hooks

### Post-Registration Hooks

| Hook | Description | Use Case |
|------|-------------|----------|
| `session` | Creates an authenticated session | User is logged in after registration |
| `show_verification_ui` | Redirects to verification UI | Show verification screen after registration |
| `web_hook` | Calls external webhook | Trigger external systems |

### Post-Login Hooks

| Hook | Description | Use Case |
|------|-------------|----------|
| `require_verified_address` | Requires verified address to login | Block unverified users from logging in |
| `session` | Creates authenticated session | Standard login behavior |
| `web_hook` | Calls external webhook | Trigger external systems |

## How Verification Works with Code Method

### Registration Flow with Code Method

1. **User submits registration form** with email/phone
2. **Kratos sends verification code** to the provided email/phone
3. **User enters the code** in the registration form
4. **Kratos verifies the code** and automatically:
   - Marks the address as verified (`verified: true`, `verified_at: timestamp`)
   - Creates the identity
5. **Post-registration hooks execute**:
   - If `show_verification_ui` is configured, user is redirected to verification UI
   - If `session` is configured, a session is created

### Important Notes about Code Method

- **Automatic Verification**: When using the code method for registration, the address is **automatically verified** when the user successfully enters the code. You don't need a separate verification flow.
  
- **show_verification_ui Hook**: This is useful if you want to:
  - Show a "verification successful" message
  - Collect additional information post-verification
  - Have a consistent UX across different registration methods

## Login with Verification Requirement

### Using `require_verified_address` Hook

This hook ensures users cannot login without verifying their address:

```yaml
selfservice:
  flows:
    login:
      after:
        code:
          hooks:
            - hook: require_verified_address
        password:
          hooks:
            - hook: require_verified_address
```

**Behavior**:
- If address is not verified, login fails
- User receives a `continue_with` response containing `show_verification_ui` action
- Frontend should redirect to verification UI

### Legacy Behavior Flag

```yaml
feature_flags:
  legacy_require_verified_login_error: false  # Default: false
```

- `true`: Returns a form error (old behavior)
- `false`: Returns `continue_with` array with verification flow (recommended)

## Example: Complete Registration Flow with Code

### Step 1: Initialize Registration Flow

```bash
curl -X GET http://localhost:4433/self-service/registration/browser
```

### Step 2: Submit Email (First Step)

```bash
curl -X POST http://localhost:4433/self-service/registration?flow=<flow_id> \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {
      "email": "user@example.com"
    }
  }'
```

Response: Flow state changes to `email_sent`

### Step 3: Submit Code (Second Step)

```bash
curl -X POST http://localhost:4433/self-service/registration?flow=<flow_id> \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {
      "email": "user@example.com"
    }
  }'
```

Response: Identity is created with verified email, hooks execute

### Step 4: Handle Continue With

If `show_verification_ui` hook is configured, response includes:

```json
{
  "continue_with": [
    {
      "action": "show_verification_ui",
      "flow": {
        "id": "verification-flow-id",
        "url": "http://localhost:4455/verification?flow=verification-flow-id"
      }
    }
  ],
  "session": {
    "id": "session-id",
    "active": true,
    "identity": { ... }
  }
}
```

## Common Scenarios

### Scenario 1: Passwordless with Automatic Verification

**Goal**: Users register with email/code, get automatically verified, and logged in.

**Config**:
```yaml
selfservice:
  flows:
    registration:
      after:
        code:
          hooks:
            - hook: session  # Just create session, no verification UI needed
    verification:
      enabled: true
      use: code
  methods:
    code:
      passwordless_enabled: true
```

**Result**: Email is verified during registration, user is logged in immediately.

### Scenario 2: Show Verification Success Page

**Goal**: Show a "verification successful" page after registration.

**Config**:
```yaml
selfservice:
  flows:
    registration:
      after:
        code:
          hooks:
            - hook: show_verification_ui
            - hook: session
    verification:
      enabled: true
      use: code
      after:
        default_browser_return_url: http://localhost:4455/welcome
```

**Result**: User sees verification UI, then redirected to welcome page.

### Scenario 3: Require Verification Before Login

**Goal**: Prevent unverified users from logging in.

**Config**:
```yaml
selfservice:
  flows:
    registration:
      after:
        password:
          hooks:
            - hook: show_verification_ui  # Show verification UI after registration
    login:
      after:
        password:
          hooks:
            - hook: require_verified_address  # Block unverified logins
    verification:
      enabled: true
      use: code
```

**Result**: Users must verify before they can login.

## Frontend Implementation

Your frontend should handle the `continue_with` array:

```typescript
const handleRegistrationResponse = (response) => {
  if (response.continue_with) {
    for (const action of response.continue_with) {
      if (action.action === 'show_verification_ui') {
        // Redirect to verification UI
        window.location.href = action.flow.url;
        return;
      }
    }
  }
  
  // Default: redirect to dashboard
  window.location.href = '/dashboard';
};
```

## Testing Verification

### Using Kratos in Development Mode

Set up a mail catcher like [MailSlurper](http://mailslurper.com/) or use Kratos's built-in courier logs:

```yaml
courier:
  smtp:
    connection_uri: smtp://localhost:1025
log:
  level: debug
  leak_sensitive_values: true  # Shows codes in logs (dev only!)
```

## Summary

For passwordless registration with code method:

1. ✅ **The code itself verifies the address** - No separate verification needed
2. ✅ Use `show_verification_ui` hook if you want a verification success page
3. ✅ Use `require_verified_address` on login to enforce verification
4. ✅ Enable verification flow for manual verification if needed
5. ✅ Configure your identity schema with verification extensions

The key insight: **Code method registration automatically verifies the address when the code is entered correctly**. The verification hooks are optional and mainly for UX purposes.
