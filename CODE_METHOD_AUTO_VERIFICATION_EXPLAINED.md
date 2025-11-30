# How Code Method Automatically Verifies Addresses - Deep Dive

## Executive Summary

When using the `code` method for registration in Ory Kratos, **the address is automatically verified when the user enters the correct code**. This happens because:

1. The code is sent to the email/phone that needs to be verified
2. Only the owner of that email/phone can retrieve the code
3. Successfully entering the code proves ownership
4. Kratos immediately marks the address as verified in the database

This is **fundamentally different from password registration**, where the user sets a password without proving they own the email address.

## The Code That Does It

### Step 1: Registration Code Verification Function

Located in `selfservice/strategy/code/strategy_registration.go`, lines 271-349:

```go
func (s *Strategy) registrationVerifyCode(ctx context.Context, f *registration.Flow, 
    p *updateRegistrationFlowWithCodeMethod, i *identity.Identity) (err error) {
    
    // Step 1: Validate the code submitted by user
    if len(p.Code) == 0 {
        return errors.WithStack(schema.NewRequiredError("#/code", "code"))
    }
    
    // Step 2: Re-validate identity traits
    cred, _, err := s.validateAndGetCredentialsFromTraits(ctx, i, p.Traits)
    if err != nil {
        return err
    }
    
    // Step 3: Attempt to use the code (checks if code is valid, not expired, not used)
    registrationCode, err := s.deps.RegistrationCodePersister().UseRegistrationCode(
        ctx, f.ID, p.Code, cred.Identifiers...)
    if err != nil {
        if errors.Is(err, ErrCodeNotFound) {
            return errors.WithStack(schema.NewRegistrationCodeInvalid())
        }
        return errors.WithStack(err)
    }
    
    // Step 4: 🔑 THIS IS WHERE VERIFICATION HAPPENS 🔑
    // The code was valid, so we mark the address as verified
    if err := s.verifyAddress(ctx, i, Address{
        To:  registrationCode.Address,      // The email/phone the code was sent to
        Via: registrationCode.AddressType,   // email or sms
    }, false); err != nil {
        return err
    }
    
    // Step 5: Update flow state to indicate completion
    f.SetState(flow.NextState(f.GetState()))
    
    return nil
}
```

### Step 2: The verifyAddress Function

Located in `selfservice/strategy/code/strategy_login.go`, lines 518-546:

```go
func (s *Strategy) verifyAddress(ctx context.Context, i *identity.Identity, 
    verified Address, persistNow bool) error {
    
    // Loop through all verifiable addresses in the identity
    for idx := range i.VerifiableAddresses {
        address := &i.VerifiableAddresses[idx]
        
        // Skip if already verified
        if address.Verified {
            continue
        }
        
        // Find the matching address
        if verified.To != address.Value || string(verified.Via) != address.Via {
            continue
        }
        
        // 🔑 MARK AS VERIFIED 🔑
        address.Verified = true
        address.VerifiedAt = pointerx.Ptr(sqlxx.NullTime(time.Now().UTC()))
        address.Status = identity.VerifiableAddressStatusCompleted
        
        // Persist to database if requested (for login, not registration)
        if persistNow {
            if err := s.deps.PrivilegedIdentityPool().UpdateVerifiableAddress(
                ctx, address, "verified", "verified_at", "status"); 
                errors.Is(err, sqlcon.ErrNoRows) {
                // During registration, address doesn't exist yet, so skip
                s.deps.Logger().WithError(err).Warnf(
                    "Could not update verifiable address for identity %s.", i.ID)
                continue
            } else if err != nil {
                return err
            }
        }
        
        // Update the in-memory identity object
        i.VerifiableAddresses[idx] = *address
        break
    }
    
    return nil
}
```

## What Gets Stored in the Database

### VerifiableAddress Structure

From `identity/identity_verification.go`:

```go
type VerifiableAddress struct {
    ID         uuid.UUID               `json:"id" db:"id"`
    Value      string                  `json:"value" db:"value"`           // e.g., "user@example.com"
    Verified   bool                    `json:"verified" db:"verified"`      // ✅ SET TO TRUE
    Via        string                  `json:"via" db:"via"`                // "email" or "sms"
    Status     VerifiableAddressStatus `json:"status" db:"status"`          // ✅ SET TO "completed"
    VerifiedAt *sqlxx.NullTime         `json:"verified_at" db:"verified_at"` // ✅ SET TO CURRENT TIME
    CreatedAt  time.Time               `json:"created_at" db:"created_at"`
    UpdatedAt  time.Time               `json:"updated_at" db:"updated_at"`
    IdentityID uuid.UUID               `json:"-" db:"identity_id"`
}
```

### Before Code Verification

```json
{
  "id": "uuid-123",
  "value": "user@example.com",
  "verified": false,
  "via": "email",
  "status": "pending",
  "verified_at": null,
  "created_at": "2024-11-30T10:00:00Z",
  "updated_at": "2024-11-30T10:00:00Z",
  "identity_id": "identity-uuid"
}
```

### After Code Verification

```json
{
  "id": "uuid-123",
  "value": "user@example.com",
  "verified": true,          // ✅ CHANGED
  "via": "email",
  "status": "completed",     // ✅ CHANGED
  "verified_at": "2024-11-30T10:05:23.456Z",  // ✅ CHANGED
  "created_at": "2024-11-30T10:00:00Z",
  "updated_at": "2024-11-30T10:05:23.456Z",   // ✅ CHANGED
  "identity_id": "identity-uuid"
}
```

## Complete Flow Visualization

### Code Method Registration Flow (Step-by-Step)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User Initiates Registration                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /registration with email
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Kratos Creates Registration Code                       │
│                                                                 │
│  • Validates email format                                       │
│  • Generates random 6-digit code                                │
│  • Stores code in database (hashed)                            │
│  • Code expires in 15 minutes (configurable)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Kratos Sends Code via Courier                          │
│                                                                 │
│  • Sends email: "Your code is: 123456"                         │
│  • User receives code in their inbox                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ User retrieves code from email
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: User Submits Code                                      │
│                                                                 │
│  POST /registration with:                                       │
│  {                                                              │
│    "method": "code",                                            │
│    "code": "123456",                                            │
│    "traits": { "email": "user@example.com" }                   │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Kratos Validates Code                                  │
│                                                                 │
│  registrationVerifyCode() function:                             │
│  • Checks code matches (HMAC comparison)                       │
│  • Checks code not expired                                     │
│  • Checks code not already used                                │
│  • Marks code as used                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Code is valid ✅
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 🔑 AUTOMATIC VERIFICATION HAPPENS HERE 🔑               │
│                                                                 │
│  verifyAddress() function called:                               │
│  • Sets address.Verified = true                                │
│  • Sets address.VerifiedAt = NOW()                             │
│  • Sets address.Status = "completed"                           │
│                                                                 │
│  WHY? User proved ownership by:                                │
│  1. Having access to the email inbox                           │
│  2. Retrieving the code                                        │
│  3. Submitting the correct code                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Identity Created with Verified Address                 │
│                                                                 │
│  Database record:                                               │
│  {                                                              │
│    "id": "uuid",                                                │
│    "traits": { "email": "user@example.com" },                  │
│    "verifiable_addresses": [{                                   │
│      "value": "user@example.com",                              │
│      "verified": true,        ✅                                │
│      "verified_at": "2024-11-30T10:05:23Z",  ✅                 │
│      "status": "completed"    ✅                                │
│    }]                                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Post-Registration Hooks Execute                        │
│                                                                 │
│  If configured with "session" hook:                             │
│  • Session created                                              │
│  • User is logged in                                            │
│  • Session token returned                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Comparison: Code vs. Password Registration

### Code Method (Auto-Verification)

```
User Submits Email
      │
      ├── Code Sent to Email
      │
      ├── User Enters Code ─────► Proves Email Ownership
      │                           (Can only get code if they own email)
      │
      └── ✅ Address Marked as VERIFIED
          └── Identity Created with verified=true
```

### Password Method (No Auto-Verification)

```
User Submits Email + Password
      │
      ├── NO code sent
      │
      ├── User sets password ──────► Does NOT prove email ownership
      │                              (Anyone can type any email)
      │
      └── ❌ Address Marked as UNVERIFIED
          ├── Identity created with verified=false
          │
          └── Separate verification flow needed:
              ├── Verification code sent
              ├── User must enter code
              └── Then marked as verified
```

## Why This Matters: Security Implications

### The Code Method is Inherently Secure

The code method provides **proof of ownership** because:

1. **Possession Factor**: Code is sent to the email/phone
2. **Only the Owner Can Access**: To get the code, you must have access to that email/phone
3. **Time-Limited**: Code expires (default 15 minutes)
4. **One-Time Use**: Code can only be used once
5. **Cryptographically Secure**: Code is randomly generated and HMAC-verified

### Password Method Lacks Proof of Ownership

Password registration **does not prove ownership** because:

1. **No Possession Factor**: Anyone can type any email address
2. **No Verification**: Password doesn't prove you own the email
3. **Attack Vector**: Attackers can register with victim's email
4. **Requires Separate Step**: Must send verification email after registration

## Code Example: Watching Verification Happen

### Database Query Before Code Submission

```sql
SELECT 
  id, 
  value, 
  verified, 
  status, 
  verified_at 
FROM identity_verifiable_addresses 
WHERE value = 'user@example.com';
```

**Result**:
```
id                  | value             | verified | status  | verified_at
--------------------+-------------------+----------+---------+-------------
uuid-123            | user@example.com  | false    | pending | NULL
```

### User Submits Code

```bash
curl -X POST http://localhost:4433/self-service/registration?flow=$FLOW_ID \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {
      "email": "user@example.com"
    }
  }'
```

### Database Query After Code Submission

```sql
SELECT 
  id, 
  value, 
  verified, 
  status, 
  verified_at 
FROM identity_verifiable_addresses 
WHERE value = 'user@example.com';
```

**Result**:
```
id        | value            | verified | status    | verified_at
----------+------------------+----------+-----------+-------------------------
uuid-123  | user@example.com | TRUE     | completed | 2024-11-30 10:05:23.456
```

### 🎯 Notice What Changed

1. `verified`: `false` → `true`
2. `status`: `pending` → `completed`
3. `verified_at`: `NULL` → `2024-11-30 10:05:23.456`

This happens **automatically** in the `verifyAddress()` function!

## Execution Call Stack

Here's the exact sequence of function calls during code verification:

```
1. HTTP POST /self-service/registration?flow=xxx
   ↓
2. Strategy.Register()
   ↓
3. Strategy.registrationVerifyCode()
   ↓
4. RegistrationCodePersister.UseRegistrationCode()
   • Validates code
   • Marks code as used
   • Returns the code details (including address it was sent to)
   ↓
5. Strategy.verifyAddress()  ← 🔑 VERIFICATION HAPPENS HERE
   • Sets Verified = true
   • Sets VerifiedAt = NOW()
   • Sets Status = completed
   ↓
6. RegistrationFlowPersister.UpdateRegistrationFlow()
   • Updates flow state to "passed_challenge"
   ↓
7. Registration hooks execute
   • session hook creates session (if configured)
   • show_verification_ui hook redirects (if configured)
   ↓
8. Identity persisted to database with verified address
```

## Comparison with Login Flow

### Registration vs. Login Verification

| Aspect | Registration | Login |
|--------|-------------|-------|
| **When called** | During `registrationVerifyCode()` | During `loginVerifyCode()` |
| **persistNow parameter** | `false` | `true` |
| **Why?** | Identity not yet persisted | Identity already exists |
| **Effect** | In-memory only, saved later | Immediately saved to DB |

Both call the **same** `verifyAddress()` function!

```go
// Registration calls it like this:
s.verifyAddress(ctx, i, Address{
    To:  registrationCode.Address,
    Via: registrationCode.AddressType,
}, false)  // ← false = don't persist now, will persist with identity

// Login calls it like this:
s.verifyAddress(ctx, i, Address{
    To:  loginCode.Address,
    Via: loginCode.AddressType,
}, true)  // ← true = persist immediately
```

## Real-World Example with Logs

### Enable Sensitive Logging (Dev Only!)

```yaml
log:
  level: debug
  leak_sensitive_values: true  # ONLY FOR DEVELOPMENT
```

### Kratos Log Output During Registration

```
[2024-11-30 10:00:00] INFO  Registration flow created flow_id=abc123
[2024-11-30 10:00:05] INFO  Registration code created code=123456 email=user@example.com expires=2024-11-30T10:15:00Z
[2024-11-30 10:00:05] INFO  Sending registration code email to=user@example.com
[2024-11-30 10:05:20] INFO  Received registration submission flow_id=abc123
[2024-11-30 10:05:20] DEBUG Validating registration code code=123456
[2024-11-30 10:05:20] DEBUG Code is valid, marking as used
[2024-11-30 10:05:20] INFO  Verifying address address=user@example.com via=email
[2024-11-30 10:05:20] DEBUG Setting verified=true, verified_at=2024-11-30T10:05:20Z, status=completed
[2024-11-30 10:05:20] INFO  Address verified successfully ✅
[2024-11-30 10:05:21] INFO  Creating identity with verified address
[2024-11-30 10:05:21] INFO  Executing post-registration hooks hooks=[session]
[2024-11-30 10:05:21] INFO  Registration completed successfully
```

## Key Architectural Design Decisions

### Why Automatic Verification Makes Sense

1. **Proof of Ownership**: The code proves the user owns the address
2. **User Experience**: One less step for users
3. **Security**: Time-limited, one-time codes are secure
4. **Consistency**: Same flow for email and SMS
5. **Simplicity**: No separate verification flow needed

### Why Password Doesn't Auto-Verify

1. **No Proof**: Password doesn't prove email ownership
2. **Attack Vector**: Prevents email bombing attacks
3. **Best Practice**: Industry standard requires email verification
4. **Compliance**: Some regulations require verified contact info

## Summary Table

| Feature | Code Method | Password Method |
|---------|-------------|-----------------|
| **Verification** | ✅ Automatic | ❌ Manual required |
| **When verified** | During registration | After registration |
| **Proof of ownership** | ✅ Yes (via code) | ❌ No |
| **User steps** | 2 (email → code) | 3 (email+password → verify email → code) |
| **Database state** | `verified: true` immediately | `verified: false` until manual verification |
| **Security** | High (possession factor) | Lower without verification |
| **Use case** | Passwordless/OTP apps | Traditional password apps |

## Frequently Asked Questions

### Q: Can I disable auto-verification for code method?

**A**: No, it's built into the code method. The code proving ownership IS the verification. If you don't want this behavior, use password method with separate verification.

### Q: What if someone intercepts the code?

**A**: The code:
- Expires in 15 minutes (configurable)
- Is one-time use only
- Requires HTTPS in production
- Is cryptographically secure

### Q: Can I require additional verification even with code method?

**A**: The code method already provides verification. However, you can:
- Use `show_verification_ui` hook to show verification success page
- Use `require_verified_address` hook on login (extra safety)
- Add webhooks for additional validation

### Q: Does this work for SMS too?

**A**: Yes! The same automatic verification happens for:
- Email codes
- SMS codes
- Any channel that supports code delivery

### Q: What about login with code method?

**A**: Login also marks addresses as verified:
- If using code for 2FA, it verifies the address
- The same `verifyAddress()` function is called
- Difference: `persistNow=true` (immediate DB update)

## Conclusion

The code method's automatic verification is a **core security feature**, not a configuration option. It works because:

1. **The code is sent to the address being verified**
2. **Only the owner can retrieve the code**
3. **Submitting the correct code proves ownership**
4. **Kratos marks the address as verified immediately**

This is fundamentally different from password registration, where verification must happen separately because a password doesn't prove you own the email address.

The implementation is elegant: one `verifyAddress()` function used by both registration and login flows, with automatic verification happening at the moment the correct code is entered.
