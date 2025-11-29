# Visual Flow Guide: Passwordless Phone Authentication

## Complete User Journey

### Flow 1: New User (Identity Doesn't Exist)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 1: User tries to LOGIN                                       │
│  ────────────────────────────────                                  │
│                                                                     │
│  ┌────────────────────────────────────────────┐                    │
│  │  LOGIN PAGE                                │                    │
│  │  http://localhost:3000/login               │                    │
│  │                                            │                    │
│  │  [Phone Number Input]                      │                    │
│  │  +1234567890                               │                    │
│  │                                            │                    │
│  │  [Send Code Button]                        │                    │
│  └────────────────────────────────────────────┘                    │
│                       │                                             │
│                       ▼                                             │
│              User clicks "Send Code"                                │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Check if identity exists                       │       │
│  │  → Query database for phone: +1234567890                │       │
│  │  → Result: NOT FOUND ❌                                 │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  UI: Detect "identity not found" error                  │       │
│  │  → Error code: 4000007                                  │       │
│  │  → Action: Redirect to registration                     │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 2: Automatic REGISTRATION redirect                           │
│  ────────────────────────────────────────                          │
│                                                                     │
│  ┌────────────────────────────────────────────┐                    │
│  │  REGISTRATION PAGE                         │                    │
│  │  http://localhost:3000/registration        │                    │
│  │    ?phone=+1234567890                      │                    │
│  │                                            │                    │
│  │  [Phone Number Input]                      │                    │
│  │  +1234567890  ← PRE-FILLED!               │                    │
│  │                                            │                    │
│  │  [Continue Button]                         │                    │
│  └────────────────────────────────────────────┘                    │
│                       │                                             │
│                       ▼                                             │
│              User clicks "Continue"                                 │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Create new identity                            │       │
│  │  → Insert into database                                 │       │
│  │  → traits.phone = "+1234567890"                         │       │
│  │  → verifiable_addresses.verified = false                │       │
│  │  → Return: continue_with actions                        │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Return continue_with                           │       │
│  │  {                                                      │       │
│  │    "continue_with": [{                                 │       │
│  │      "action": "show_verification_ui",                 │       │
│  │      "flow": { "id": "verification-flow-id" }          │       │
│  │    }]                                                  │       │
│  │  }                                                      │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  UI: Detect continue_with action                        │       │
│  │  → Action: Redirect to verification                     │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 3: Phone VERIFICATION                                        │
│  ───────────────────────────                                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Initialize verification flow                   │       │
│  │  → Create verification flow                             │       │
│  │  → Trigger courier to send SMS                          │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  SMS SERVICE: Send verification code                    │       │
│  │  → Generate 6-digit code: 123456                        │       │
│  │  → Send via Twilio/AWS SNS/Vonage                       │       │
│  │  → (Mock mode: print to console)                        │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────┐                    │
│  │  VERIFICATION PAGE                         │                    │
│  │  http://localhost:3000/verification        │                    │
│  │                                            │                    │
│  │  Code sent to: +1234567890                 │                    │
│  │                                            │                    │
│  │  [Code Input]                              │                    │
│  │  [______]  ← 6 digits                     │                    │
│  │                                            │                    │
│  │  [Verify Button]                           │                    │
│  └────────────────────────────────────────────┘                    │
│                       │                                             │
│                       ▼                                             │
│              User enters code: 123456                               │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Verify code                                    │       │
│  │  → Check code matches                                   │       │
│  │  → Check not expired (< 15 minutes)                     │       │
│  │  → Mark verifiable_address as verified ✓                │       │
│  │  → Create session                                       │       │
│  │  → Set session cookie                                   │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────┐                    │
│  │  SUCCESS! Redirect to dashboard             │                    │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 4: User is LOGGED IN                                         │
│  ──────────────────────────                                        │
│                                                                     │
│  ┌────────────────────────────────────────────┐                    │
│  │  DASHBOARD                                 │                    │
│  │  http://localhost:3000/dashboard           │                    │
│  │                                            │                    │
│  │  Welcome!                    [Logout]      │                    │
│  │                                            │                    │
│  │  Your Profile                              │                    │
│  │  ────────────                              │                    │
│  │  Phone: +1234567890                        │                    │
│  │  Status: Verified ✓                        │                    │
│  │  User ID: abc123...                        │                    │
│  │                                            │                    │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Flow 2: Existing User (Identity Exists)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 1: User tries to LOGIN                                       │
│  ────────────────────────────────                                  │
│                                                                     │
│  ┌────────────────────────────────────────────┐                    │
│  │  LOGIN PAGE                                │                    │
│  │                                            │                    │
│  │  [Phone Number Input]                      │                    │
│  │  +1234567890                               │                    │
│  │                                            │                    │
│  │  [Send Code Button]                        │                    │
│  └────────────────────────────────────────────┘                    │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Check if identity exists                       │       │
│  │  → Query database for phone: +1234567890                │       │
│  │  → Result: FOUND ✓                                      │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Send login code                                │       │
│  │  → Trigger courier to send SMS                          │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  SMS SERVICE: Send login code                           │       │
│  │  → Generate code: 654321                                │       │
│  │  → Send to: +1234567890                                 │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────┐                    │
│  │  LOGIN PAGE (updated)                      │                    │
│  │                                            │                    │
│  │  Code sent to: +1234567890                 │                    │
│  │                                            │                    │
│  │  [Code Input]                              │                    │
│  │  [______]  ← 6 digits                     │                    │
│  │                                            │                    │
│  │  [Verify Button]                           │                    │
│  └────────────────────────────────────────────┘                    │
│                       │                                             │
│                       ▼                                             │
│              User enters code: 654321                               │
│                       │                                             │
│                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  KRATOS: Verify code                                    │       │
│  │  → Check code matches                                   │       │
│  │  → Create session                                       │       │
│  │  → Set session cookie                                   │       │
│  └─────────────────────────────────────────────────────────┘       │
│                       │                                             │
│                       ▼                                             │
│  ┌────────────────────────────────────────────┐                    │
│  │  SUCCESS! Redirect to dashboard             │                    │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
│  ┌────────────────────────────────────────────┐                    │
│  │  DASHBOARD - User is logged in             │                    │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Differences Between Flows

| Aspect | New User | Existing User |
|--------|----------|---------------|
| **Initial Check** | Identity NOT found | Identity found |
| **Action** | Redirect to registration | Send login code |
| **Phone Input** | Pre-filled in registration | Only entered once |
| **Steps** | Login → Registration → Verification → Dashboard | Login → Verification → Dashboard |
| **Verification Type** | Account verification | Login verification |
| **Database Operations** | INSERT identity | SELECT identity |

---

## Technical Flow Details

### 1. Login API Calls (New User)

```javascript
// 1. Create login flow
POST /self-service/login/browser
→ Returns: { id: "flow-123", ui: {...} }

// 2. Submit phone number
POST /self-service/login?flow=flow-123
Body: { method: "code", identifier: "+1234567890" }
→ Returns: Error 4000007 (identity not found)

// 3. UI catches error and redirects
→ Redirect to: /registration?phone=+1234567890
```

### 2. Registration API Calls

```javascript
// 1. Create registration flow
POST /self-service/registration/browser
→ Returns: { id: "flow-456", ui: {...} }

// 2. Submit registration
POST /self-service/registration?flow=flow-456
Body: { method: "code", traits: { phone: "+1234567890" } }
→ Returns: {
    continue_with: [{
      action: "show_verification_ui",
      flow: { id: "flow-789" }
    }]
  }

// 3. UI detects continue_with and redirects
→ Redirect to: /verification?flow=flow-789
```

### 3. Verification API Calls

```javascript
// 1. Get verification flow (SMS already sent)
GET /self-service/verification?flow=flow-789
→ Returns: { id: "flow-789", ui: {...} }

// 2. Submit verification code
POST /self-service/verification?flow=flow-789
Body: { method: "code", code: "123456" }
→ Returns: Success
→ Session cookie is set
→ Redirect to: /dashboard
```

---

## Console Output Examples

### SMS Service Console (Mock Mode)

```bash
==================================================
📱 MOCK SMS SENT
==================================================
To: +1234567890
Message: Your verification code is 123456
==================================================
🔑 VERIFICATION CODE: 123456
==================================================
```

### Kratos Console

```bash
time=2025-11-29 INFO: login flow initialized flow_id=flow-123
time=2025-11-29 INFO: identity not found identifier=+1234567890
time=2025-11-29 INFO: registration flow initialized flow_id=flow-456
time=2025-11-29 INFO: identity created id=abc-123 phone=+1234567890
time=2025-11-29 INFO: verification flow initialized flow_id=flow-789
time=2025-11-29 INFO: verification code sent to=+1234567890
time=2025-11-29 INFO: verification successful address=+1234567890
time=2025-11-29 INFO: session created session_id=session-xyz
```

---

## State Transitions

```
[User visits /login]
      │
      ▼
[Enter phone] ──────┐
      │             │
      ▼             │
[Identity check]    │
      │             │
   ┌──┴──┐          │
   │     │          │
Found  Not Found    │
   │     │          │
   │     └─────────────▶ [Registration]
   │                         │
   │                         ▼
   │                    [Create identity]
   │                         │
   │     ┌───────────────────┘
   │     │
   ▼     ▼
[Send code]
      │
      ▼
[Verify code]
      │
      ▼
[Create session]
      │
      ▼
[Dashboard]
```

---

## Session Management

### Cookie Structure

```
ory_kratos_session=<session-token>
Domain: localhost
Path: /
HttpOnly: true
Secure: true (in production)
SameSite: Lax
```

### Session Validation

```javascript
// Check if user is logged in
GET /sessions/whoami
Cookie: ory_kratos_session=<token>

// Response (logged in):
{
  "id": "session-xyz",
  "active": true,
  "identity": {
    "id": "abc-123",
    "traits": {
      "phone": "+1234567890"
    },
    "verifiable_addresses": [{
      "value": "+1234567890",
      "verified": true,
      "via": "sms"
    }]
  }
}

// Response (not logged in):
401 Unauthorized
```

---

## Error Handling

### Common Errors

| Error Code | Meaning | UI Action |
|------------|---------|-----------|
| 4000007 | Identity not found | Redirect to registration |
| 4000006 | Invalid credentials | Show error message |
| 410 | Flow expired | Create new flow |
| 403 | CSRF token invalid | Refresh page |
| 4000005 | Code invalid/expired | Show error, allow retry |

### Error Flow Example

```
User enters wrong code
      │
      ▼
POST /verification
      │
      ▼
Kratos returns error
      │
      ▼
UI shows error message
      │
      ▼
User can try again
      │
      ├─▶ Try again (same flow)
      └─▶ Resend code (new flow)
```

---

## Security Features Visualized

### CSRF Protection

```
1. Flow created
   ├─▶ Generate CSRF token
   └─▶ Include in hidden field

2. Form submitted
   ├─▶ Validate CSRF token
   ├─▶ Token valid? Continue
   └─▶ Token invalid? Error 403
```

### Code Expiration

```
Time: 00:00 → Code sent (123456)
Time: 00:05 → Code valid ✓
Time: 00:10 → Code valid ✓
Time: 00:15 → Code expires ✗
Time: 00:16 → New code needed
```

### Single-Use Codes

```
Code: 123456
      │
      ├─▶ First use: ✓ Success
      │
      └─▶ Second use: ✗ Invalid (already used)
```

---

## Quick Reference

### URLs
- **Login**: http://localhost:3000/login
- **Registration**: http://localhost:3000/registration
- **Verification**: http://localhost:3000/verification
- **Dashboard**: http://localhost:3000/dashboard

### Test Phone Numbers (Mock Mode)
- `+1234567890`
- `+14155552671`
- Any E.164 format

### Verification Codes
- **Length**: 6 digits
- **Lifespan**: 15 minutes
- **Usage**: Single-use
- **Location**: SMS Service console output
