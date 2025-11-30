# Ory Kratos Identity Creation and Verification - Complete Guide

This repository contains comprehensive documentation about Ory Kratos (v25.4.0) identity management, passwordless authentication, and verification.

## 📚 Documentation Files

### Core Answers

1. **[SUMMARY.md](SUMMARY.md)** - Executive summary answering the main questions:
   - Can Kratos create identities during passwordless login? (No)
   - How does verification work with the code method?
   - Quick configuration examples

### Deep Dive on Auto-Verification

2. **[CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md](CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md)** - **START HERE for understanding auto-verification**
   - Detailed explanation with actual source code
   - Shows the exact functions that perform verification
   - Database schema and field changes
   - Security implications and why it works
   - Comparison with password method

3. **[VISUAL_VERIFICATION_FLOW.md](VISUAL_VERIFICATION_FLOW.md)** - Visual diagrams
   - Complete flow diagrams
   - Side-by-side comparisons
   - Database state transitions
   - Security reasoning visualized

4. **[TEST_AUTO_VERIFICATION.md](TEST_AUTO_VERIFICATION.md)** - Practical testing guide
   - 10 different tests to observe verification in action
   - SQL queries to watch database changes
   - Timing tests proving instant verification
   - Proof that it really happens automatically

### Configuration Guides

5. **[KRATOS_VERIFICATION_SETUP.md](KRATOS_VERIFICATION_SETUP.md)** - Complete setup guide
   - How to configure verification in Kratos
   - Identity schema setup
   - Courier configuration
   - Common scenarios and use cases

6. **[VERIFICATION_HOOKS_QUICK_REFERENCE.md](VERIFICATION_HOOKS_QUICK_REFERENCE.md)** - Quick reference
   - Hook combinations and their effects
   - When to use each hook
   - Configuration examples
   - Best practices

### Ready-to-Use Files

7. **[kratos-verification-example.yml](kratos-verification-example.yml)** - Complete Kratos config
   - Production-ready configuration
   - Verification enabled
   - Both code and password methods

8. **[identity.schema.json](identity.schema.json)** - Identity schema example
   - Email and phone verification
   - Code credentials configuration
   - TOS acceptance field

9. **[docker-compose.verification-example.yml](docker-compose.verification-example.yml)** - Docker setup
   - Kratos + PostgreSQL + MailSlurper
   - Ready to test immediately
   - Pre-configured for verification testing

10. **[README_VERIFICATION_TESTING.md](README_VERIFICATION_TESTING.md)** - Testing guide
    - How to use the Docker setup
    - API testing with curl
    - Common troubleshooting

## 🎯 Quick Start

### Understanding Auto-Verification (5 minutes)

Read these in order:
1. [CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md](CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md) - Understand how it works
2. [VISUAL_VERIFICATION_FLOW.md](VISUAL_VERIFICATION_FLOW.md) - See the flow visually

### Testing It Yourself (10 minutes)

```bash
# 1. Start the test environment
docker-compose -f docker-compose.verification-example.yml up -d

# 2. Open MailSlurper to view codes
open http://localhost:4436

# 3. Run a test registration
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","traits":{"email":"test@example.com","accepted_tos":true}}'

# Check MailSlurper for code, then submit it
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","code":"123456","traits":{"email":"test@example.com","accepted_tos":true}}' \
  | jq '.identity.verifiable_addresses[0] | {email: .value, verified, verified_at}'
```

You'll see:
```json
{
  "email": "test@example.com",
  "verified": true,
  "verified_at": "2024-11-30T10:05:23.456789Z"
}
```

**That's the auto-verification in action!** ✨

### Implementing in Your App (30 minutes)

1. Read: [KRATOS_VERIFICATION_SETUP.md](KRATOS_VERIFICATION_SETUP.md)
2. Copy: [kratos-verification-example.yml](kratos-verification-example.yml) and [identity.schema.json](identity.schema.json)
3. Customize for your needs
4. Test with [README_VERIFICATION_TESTING.md](README_VERIFICATION_TESTING.md)

## 🔑 Key Findings

### Question 1: Can Kratos Create Identities During Login?

**❌ NO** - Kratos does NOT automatically create identities during the login flow.

- Login requires an existing identity
- Registration is a separate flow
- No auto-registration feature

**Solution**: Handle "account not found" errors and redirect to registration.

### Question 2: How Does Verification Work with Code Method?

**✅ AUTOMATIC** - The code method automatically verifies addresses during registration.

**Why?**
1. Code is sent to the email/phone being verified
2. User proves ownership by submitting the correct code
3. Kratos immediately marks the address as verified

**The Magic Moment:**

```go
// From: selfservice/strategy/code/strategy_registration.go
// When user submits correct code:

// Step 4: Verify the address
if err := s.verifyAddress(ctx, i, Address{
    To:  registrationCode.Address,      // email where code was sent
    Via: registrationCode.AddressType,   // email or sms
}, false); err != nil {
    return err
}

// This function sets:
address.Verified = true
address.VerifiedAt = time.Now()
address.Status = "completed"
```

**Database Before:**
```json
{
  "email": "user@example.com",
  "verified": false,
  "verified_at": null,
  "status": "pending"
}
```

**Database After:**
```json
{
  "email": "user@example.com",
  "verified": true,
  "verified_at": "2024-11-30T10:05:23Z",
  "status": "completed"
}
```

## 📊 Method Comparison

| Method | Verification | When | Why |
|--------|--------------|------|-----|
| **Code (Passwordless)** | ✅ Automatic | During registration | Code proves ownership |
| **Password** | ❌ Manual | After registration | Password doesn't prove email ownership |

## 🎨 Visual Flow

### Code Method (2 Steps, Auto-Verified)

```
User enters email → Code sent → User enters code → ✅ VERIFIED → Logged in
```

### Password Method (3 Steps, Manual Verification)

```
User sets password → Account created (unverified) → Verification email sent → 
User enters code → ✅ VERIFIED
```

## 🔧 Configuration Examples

### Simplest Passwordless Setup

```yaml
selfservice:
  flows:
    registration:
      after:
        code:
          hooks:
            - hook: session  # User verified and logged in automatically
    verification:
      enabled: true
      use: code
  methods:
    code:
      passwordless_enabled: true
```

### With Verification Success Page

```yaml
selfservice:
  flows:
    registration:
      after:
        code:
          hooks:
            - hook: show_verification_ui  # Show success page
            - hook: session                # Then log in
    verification:
      enabled: true
      use: code
      after:
        default_browser_return_url: /welcome
  methods:
    code:
      passwordless_enabled: true
```

### Maximum Security (Mixed Methods)

```yaml
selfservice:
  flows:
    registration:
      after:
        password:
          hooks:
            - hook: show_verification_ui  # Password users must verify
        code:
          hooks:
            - hook: session  # Code users auto-verified
    login:
      after:
        password:
          hooks:
            - hook: require_verified_address  # Block unverified logins
        code:
          hooks:
            - hook: require_verified_address
    verification:
      enabled: true
      use: code
  methods:
    password:
      enabled: true
    code:
      passwordless_enabled: true
security:
  account_enumeration:
    mitigate: true
```

## 🧪 Proving Auto-Verification

### Quick Database Test

```bash
# Register with code method
# ... (get code from email, submit it)

# Check database
docker exec -it <postgres-container> psql -U kratos -d kratos -c "
  SELECT 
    value,
    verified,
    status,
    verified_at
  FROM identity_verifiable_addresses 
  WHERE value = 'user@example.com';
"
```

**Result:**
```
value             | verified | status    | verified_at
------------------+----------+-----------+-------------------------
user@example.com  | t        | completed | 2024-11-30 10:05:23.456
```

**Proof**: `verified` is `true` immediately after registration!

## 📖 Documentation Structure

```
.
├── README.md (you are here)
│
├── Core Understanding
│   ├── SUMMARY.md
│   ├── CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md ⭐
│   ├── VISUAL_VERIFICATION_FLOW.md
│   └── TEST_AUTO_VERIFICATION.md
│
├── Configuration Guides
│   ├── KRATOS_VERIFICATION_SETUP.md
│   ├── VERIFICATION_HOOKS_QUICK_REFERENCE.md
│   └── README_VERIFICATION_TESTING.md
│
└── Ready-to-Use Files
    ├── kratos-verification-example.yml
    ├── identity.schema.json
    └── docker-compose.verification-example.yml
```

## 🎓 Learning Path

### Beginner (Just Starting)
1. Read [SUMMARY.md](SUMMARY.md)
2. Look at [VISUAL_VERIFICATION_FLOW.md](VISUAL_VERIFICATION_FLOW.md)
3. Try [docker-compose.verification-example.yml](docker-compose.verification-example.yml)

### Intermediate (Implementing)
1. Read [KRATOS_VERIFICATION_SETUP.md](KRATOS_VERIFICATION_SETUP.md)
2. Use [VERIFICATION_HOOKS_QUICK_REFERENCE.md](VERIFICATION_HOOKS_QUICK_REFERENCE.md)
3. Copy [kratos-verification-example.yml](kratos-verification-example.yml) and [identity.schema.json](identity.schema.json)
4. Test with [README_VERIFICATION_TESTING.md](README_VERIFICATION_TESTING.md)

### Advanced (Deep Understanding)
1. Read [CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md](CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md)
2. Run tests from [TEST_AUTO_VERIFICATION.md](TEST_AUTO_VERIFICATION.md)
3. Review Kratos source code on GitHub

## 🚀 Production Checklist

Before deploying:

- [ ] Review [KRATOS_VERIFICATION_SETUP.md](KRATOS_VERIFICATION_SETUP.md) production section
- [ ] Change all secrets in configuration
- [ ] Configure production SMTP/SMS provider
- [ ] Disable `leak_sensitive_values` in logs
- [ ] Enable `account_enumeration.mitigate`
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Configure proper CORS settings
- [ ] Customize email/SMS templates
- [ ] Test all flows in staging
- [ ] Set up monitoring and alerting

## 🤔 Common Questions

### Q: Why doesn't Kratos create identities during login?

**A**: Security and architecture. Login is for authentication (proving who you are), registration is for creating accounts. Mixing them would:
- Create security vulnerabilities
- Enable account enumeration attacks
- Break the clear separation of concerns

### Q: Is auto-verification secure?

**A**: Yes! It's based on **proof of possession**:
- Code sent to the address being verified
- Only the owner can access that address
- Submitting correct code = proof of ownership
- Time-limited and one-time use

More secure than password (knowledge factor) because it's a possession factor.

### Q: Can I disable auto-verification?

**A**: No, it's fundamental to how the code method works. If you don't want it, use the password method with separate verification flow.

### Q: What about SMS?

**A**: Same automatic verification! Works for:
- Email codes
- SMS codes  
- Any channel that supports code delivery

### Q: Does this work for login too?

**A**: Yes! Login with code method also verifies addresses (useful for 2FA).

## 📚 Additional Resources

- [Ory Kratos Documentation](https://www.ory.sh/docs/kratos)
- [GitHub Repository](https://github.com/ory/kratos)
- [Community Slack](https://slack.ory.sh)
- [GitHub Discussions](https://github.com/ory/kratos/discussions)

## 🏆 Best Practices

1. **Use code method for passwordless**: Simpler, more secure, auto-verified
2. **Enable verification flow**: For manual verification when needed
3. **Use hooks wisely**: `session` hook for code, `show_verification_ui` for password
4. **Enable account enumeration mitigation** in production
5. **Test thoroughly**: Use the provided test guides
6. **Monitor**: Set up alerts for failed verification attempts

## 📝 License

This documentation is provided as-is. Ory Kratos is licensed under Apache License 2.0.

---

**Need help?** Start with [SUMMARY.md](SUMMARY.md) for quick answers, or [CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md](CODE_METHOD_AUTO_VERIFICATION_EXPLAINED.md) for deep understanding.

**Want to test?** Use [docker-compose.verification-example.yml](docker-compose.verification-example.yml) and follow [README_VERIFICATION_TESTING.md](README_VERIFICATION_TESTING.md).

**Ready to implement?** Follow [KRATOS_VERIFICATION_SETUP.md](KRATOS_VERIFICATION_SETUP.md) and use [VERIFICATION_HOOKS_QUICK_REFERENCE.md](VERIFICATION_HOOKS_QUICK_REFERENCE.md) for quick lookups.
