# Visual Guide: Code Method Auto-Verification

This document provides visual representations of how automatic verification works with the code method.

## Quick Visual: The Magic Moment

```
┌─────────────────────────────────────────────────────────────────┐
│                    BEFORE CODE SUBMISSION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Database: identity_verifiable_addresses                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ email: user@example.com                                   │ │
│  │ verified: FALSE          ❌                               │ │
│  │ status: pending                                           │ │
│  │ verified_at: NULL                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ User submits: code = "123456"
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  verifyAddress() function called   │
         │                                    │
         │  address.Verified = TRUE           │
         │  address.VerifiedAt = NOW()        │
         │  address.Status = "completed"      │
         └────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AFTER CODE SUBMISSION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Database: identity_verifiable_addresses                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ email: user@example.com                                   │ │
│  │ verified: TRUE           ✅                               │ │
│  │ status: completed                                         │ │
│  │ verified_at: 2024-11-30T10:05:23Z                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Complete Registration Flow Diagram

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     │ User wants to register
     ▼
┌─────────────────────────────┐
│ 1. GET /registration/api    │
│                             │
│ Response: flow object       │
│ - flow.id                   │
│ - flow.ui (form fields)     │
└─────────────┬───────────────┘
              │
              │ Frontend renders form
              │ User enters email: user@example.com
              ▼
┌─────────────────────────────────────────────┐
│ 2. POST /registration?flow={id}             │
│                                             │
│ Body:                                       │
│ {                                           │
│   "method": "code",                         │
│   "traits": {                               │
│     "email": "user@example.com"             │
│   }                                         │
│ }                                           │
└─────────────┬───────────────────────────────┘
              │
              ├─── Kratos validates email format
              ├─── Generates 6-digit code: "123456"
              ├─── Stores code in DB (hashed)
              │    - Expiry: NOW() + 15 minutes
              │    - Used: false
              │    - Flow ID: xxx
              │    - Address: user@example.com
              │
              ├─── Sends email via Courier
              │    Subject: "Verify your email"
              │    Body: "Your code is: 123456"
              │
              └─── Response: HTTP 400 (flow not complete)
                   {
                     "ui": { ... code input field ... },
                     "state": "sent_email"
                   }
                   │
                   │ Frontend renders code input
                   │ User checks email, gets: 123456
                   │ User enters code
                   ▼
┌─────────────────────────────────────────────┐
│ 3. POST /registration?flow={id}             │
│                                             │
│ Body:                                       │
│ {                                           │
│   "method": "code",                         │
│   "code": "123456",                         │
│   "traits": {                               │
│     "email": "user@example.com"             │
│   }                                         │
│ }                                           │
└─────────────┬───────────────────────────────┘
              │
              ├─── Kratos validates code
              │    ✅ Code matches (HMAC)
              │    ✅ Not expired
              │    ✅ Not used yet
              │
              ├─── 🔑 VERIFICATION HAPPENS 🔑
              │    verifyAddress() called:
              │      address.Verified = TRUE
              │      address.VerifiedAt = NOW()
              │      address.Status = "completed"
              │
              ├─── Creates identity in database
              │    {
              │      "id": "uuid",
              │      "traits": {"email": "user@example.com"},
              │      "verifiable_addresses": [{
              │        "value": "user@example.com",
              │        "verified": TRUE,  ✅
              │        "verified_at": "2024-11-30T10:05:23Z"
              │      }]
              │    }
              │
              ├─── Marks code as used
              │
              └─── Executes hooks (if configured)
                   - If "session" hook: creates session
                   - If "show_verification_ui": includes in continue_with
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 4. Response: HTTP 200 (success!)            │
│                                             │
│ {                                           │
│   "session": {                              │
│     "id": "session-uuid",                   │
│     "identity": {                           │
│       "id": "identity-uuid",                │
│       "traits": {                           │
│         "email": "user@example.com"         │
│       },                                    │
│       "verifiable_addresses": [{            │
│         "value": "user@example.com",        │
│         "verified": true  ✅                │
│       }]                                    │
│     }                                       │
│   }                                         │
│ }                                           │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌──────────────────────┐
│ User is logged in!   │
│ Email is verified!   │
└──────────────────────┘
```

## Side-by-Side Comparison

### Code Method (Passwordless)

```
┌─────────────────────┐
│ User                │
└──────┬──────────────┘
       │
       │ 1. "I want to register with user@example.com"
       ▼
┌─────────────────────┐
│ Kratos              │
├─────────────────────┤
│ "I'll send a code   │
│  to that email"     │
└──────┬──────────────┘
       │
       │ 2. Email sent with code: 123456
       ▼
┌─────────────────────┐
│ User's Email Inbox  │
├─────────────────────┤
│ 📧 Your code is:    │
│    123456           │
└──────┬──────────────┘
       │
       │ 3. User retrieves code
       ▼
┌─────────────────────┐
│ User                │
├─────────────────────┤
│ "Here's the code:   │
│  123456"            │
└──────┬──────────────┘
       │
       │ 4. Submits code
       ▼
┌─────────────────────────────────────┐
│ Kratos                              │
├─────────────────────────────────────┤
│ "Code is correct! ✅                │
│  You proved you own this email.     │
│  Marking as VERIFIED automatically" │
└──────┬──────────────────────────────┘
       │
       │ 5. Identity created with verified=true
       ▼
┌─────────────────────┐
│ Database            │
├─────────────────────┤
│ verified: TRUE ✅   │
│ verified_at: NOW    │
└─────────────────────┘

Total Steps: 2
Verification: ✅ AUTOMATIC
```

### Password Method

```
┌─────────────────────┐
│ User                │
└──────┬──────────────┘
       │
       │ 1. "I want to register with user@example.com"
       │    "My password is: SecurePass123"
       ▼
┌─────────────────────────────────────┐
│ Kratos                              │
├─────────────────────────────────────┤
│ "Password set.                      │
│  But I can't verify the email       │
│  because password ≠ proof of        │
│  email ownership"                   │
└──────┬──────────────────────────────┘
       │
       │ 2. Identity created with verified=false
       ▼
┌─────────────────────┐
│ Database            │
├─────────────────────┤
│ verified: FALSE ❌  │
└──────┬──────────────┘
       │
       │ 3. Now need separate verification
       ▼
┌─────────────────────┐
│ Kratos              │
├─────────────────────┤
│ "Sending            │
│  verification code" │
└──────┬──────────────┘
       │
       │ 4. Email sent with code: 654321
       ▼
┌─────────────────────┐
│ User's Email Inbox  │
├─────────────────────┤
│ 📧 Your code is:    │
│    654321           │
└──────┬──────────────┘
       │
       │ 5. User retrieves code
       ▼
┌─────────────────────┐
│ User                │
├─────────────────────┤
│ "Here's the code:   │
│  654321"            │
└──────┬──────────────┘
       │
       │ 6. Submits code to verification flow
       ▼
┌─────────────────────┐
│ Kratos              │
├─────────────────────┤
│ "Code correct! ✅   │
│  Now verified"      │
└──────┬──────────────┘
       │
       │ 7. Updates database
       ▼
┌─────────────────────┐
│ Database            │
├─────────────────────┤
│ verified: TRUE ✅   │
│ verified_at: NOW    │
└─────────────────────┘

Total Steps: 3 (register, verify, done)
Verification: ❌ MANUAL REQUIRED
```

## The Core Logic: verifyAddress() Function

```
┌────────────────────────────────────────────────────────────┐
│ Function: verifyAddress(ctx, identity, address, persistNow)│
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ Loop through all verifiable    │
        │ addresses in the identity      │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Find matching address          │
        │ - Same value (email/phone)     │
        │ - Same via (email/sms)         │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Is already verified?           │
        └────────────┬───────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
           YES               NO
            │                 │
            │                 ▼
            │    ┌─────────────────────────┐
            │    │ Set verified = TRUE     │
            │    ├─────────────────────────┤
            │    │ Set verified_at = NOW() │
            │    ├─────────────────────────┤
            │    │ Set status = "completed"│
            │    └────────────┬────────────┘
            │                 │
            │                 ▼
            │    ┌─────────────────────────┐
            │    │ persistNow == true?     │
            │    └────────────┬────────────┘
            │                 │
            │        ┌────────┴────────┐
            │        │                 │
            │       YES               NO
            │        │                 │
            │        ▼                 │
            │    ┌────────────────┐   │
            │    │ Save to DB now │   │
            │    │ (for login)    │   │
            │    └────────────────┘   │
            │                          │
            │                          ▼
            │                    ┌────────────────┐
            │                    │ Update in      │
            │                    │ memory only    │
            │                    │ (for regist.)  │
            │                    └────────────────┘
            │                          │
            └──────────────────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │ Return success │
                              └────────────────┘
```

## Database State Transitions

### Timeline View

```
Time: T0 (Registration Started)
┌─────────────────────────────────────────────┐
│ identity_verifiable_addresses               │
├─────────────────────────────────────────────┤
│ (empty - identity not created yet)          │
└─────────────────────────────────────────────┘

Time: T1 (Email Submitted, Code Sent)
┌─────────────────────────────────────────────┐
│ identity_registration_codes                 │
├─────────────────────────────────────────────┤
│ id: code-uuid                               │
│ address: user@example.com                   │
│ code_hmac: <hashed-123456>                  │
│ used_at: NULL                               │
│ expires_at: T1 + 15 minutes                 │
│ flow_id: flow-uuid                          │
└─────────────────────────────────────────────┘

Time: T2 (Code Submitted - VERIFICATION HAPPENS)
┌─────────────────────────────────────────────┐
│ BEFORE: in-memory identity object           │
├─────────────────────────────────────────────┤
│ verifiable_addresses: [{                    │
│   value: "user@example.com",                │
│   verified: false,                          │
│   verified_at: null,                        │
│   status: "pending"                         │
│ }]                                          │
└─────────────────────────────────────────────┘
                    │
                    │ verifyAddress() called
                    ▼
┌─────────────────────────────────────────────┐
│ AFTER: in-memory identity object            │
├─────────────────────────────────────────────┤
│ verifiable_addresses: [{                    │
│   value: "user@example.com",                │
│   verified: TRUE,              ← CHANGED    │
│   verified_at: T2,             ← CHANGED    │
│   status: "completed"          ← CHANGED    │
│ }]                                          │
└─────────────────────────────────────────────┘

Time: T3 (Identity Persisted to Database)
┌─────────────────────────────────────────────┐
│ identities                                  │
├─────────────────────────────────────────────┤
│ id: identity-uuid                           │
│ schema_id: default                          │
│ traits: {"email": "user@example.com"}       │
│ state: active                               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ identity_verifiable_addresses               │
├─────────────────────────────────────────────┤
│ id: address-uuid                            │
│ identity_id: identity-uuid                  │
│ value: user@example.com                     │
│ verified: TRUE                     ✅       │
│ verified_at: T2                    ✅       │
│ status: completed                  ✅       │
│ via: email                                  │
│ created_at: T3                              │
│ updated_at: T3                              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ identity_registration_codes                 │
├─────────────────────────────────────────────┤
│ id: code-uuid                               │
│ address: user@example.com                   │
│ code_hmac: <hashed-123456>                  │
│ used_at: T2                        ✅       │
│ expires_at: T1 + 15 minutes                 │
│ flow_id: flow-uuid                          │
└─────────────────────────────────────────────┘
```

## Security: Why This Works

```
┌───────────────────────────────────────────────────────────┐
│           WHY CODE METHOD PROVES OWNERSHIP                │
└───────────────────────────────────────────────────────────┘

   Alice                    Kratos                  Email Server
     │                        │                          │
     │ 1. Register with       │                          │
     │    alice@example.com   │                          │
     ├───────────────────────>│                          │
     │                        │                          │
     │                        │ 2. Generate code: 123456 │
     │                        │    Send to email         │
     │                        ├─────────────────────────>│
     │                        │                          │
     │                                                    │
     │ 3. Alice checks her email inbox                   │
     │<───────────────────────────────────────────────────┤
     │    "Your code is: 123456"                         │
     │                                                    │
     │ 4. Submit code         │                          │
     ├───────────────────────>│                          │
     │                        │                          │
     │                        │ 5. Verify code matches   │
     │                        │    ✅ Code correct       │
     │                        │                          │
     │                        │ 6. REASONING:            │
     │                        │    - Code was sent to    │
     │                        │      alice@example.com   │
     │                        │    - Only owner of that  │
     │                        │      inbox can get code  │
     │                        │    - Alice submitted     │
     │                        │      correct code        │
     │                        │    - Therefore: Alice    │
     │                        │      owns the email!     │
     │                        │                          │
     │                        │ 7. Mark as VERIFIED ✅   │
     │                        │                          │
     │ 8. Success!            │                          │
     │<───────────────────────┤                          │
     │    verified = true     │                          │
     │                        │                          │


COMPARE WITH PASSWORD METHOD:

   Bob                      Kratos
     │                        │
     │ 1. Register with       │
     │    victim@example.com  │  ← Bob can type ANY email!
     │    Password: xyz123    │
     ├───────────────────────>│
     │                        │
     │                        │ 2. Create account
     │                        │    verified = FALSE ❌
     │                        │
     │                        │ REASONING:
     │                        │   - Bob typed an email
     │                        │   - Bob set a password
     │                        │   - But... did Bob prove
     │                        │     he owns the email?
     │                        │   - NO! Anyone can type
     │                        │     any email address
     │                        │
     │                        │ 3. Must send verification
     │                        │    code separately
     │                        │
```

## Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              CODE METHOD AUTO-VERIFICATION                  │
│                                                             │
│  User Submits Email                                         │
│         ↓                                                   │
│  Code Sent to Email ────────┐                              │
│         ↓                    │ Possession Factor            │
│  User Retrieves Code        │ (Proves Ownership)           │
│         ↓                    │                              │
│  User Submits Code ─────────┘                              │
│         ↓                                                   │
│  ✅ EMAIL VERIFIED AUTOMATICALLY                            │
│                                                             │
│  Why? Because:                                              │
│  • Code was sent TO the email being verified                │
│  • Only the owner can access that email inbox               │
│  • Correct code submission = proof of ownership             │
│  • Kratos immediately marks address as verified             │
│                                                             │
│  Database State:                                            │
│  • verified: TRUE                                           │
│  • verified_at: <current timestamp>                         │
│  • status: completed                                        │
│                                                             │
│  No additional verification flow needed!                    │
└─────────────────────────────────────────────────────────────┘
```

## Key Takeaway

The code method's automatic verification is **not a shortcut** - it's a **cryptographically sound proof of ownership**. The moment the user submits the correct code, they've proven they own the email/phone, and Kratos immediately reflects this in the database by setting `verified=true`.

This is why passwordless authentication is both more secure (possession factor) and more convenient (fewer steps) than traditional password-based authentication without verification.
