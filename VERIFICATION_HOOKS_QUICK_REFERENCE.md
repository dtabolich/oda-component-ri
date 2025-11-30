# Ory Kratos Verification Hooks - Quick Reference

## Hook Combinations for Registration

### For Code Method (Passwordless)

**Remember**: Code method **automatically verifies** the email/phone when the code is entered correctly.

| Hooks | Behavior | Use Case |
|-------|----------|----------|
| `- session` | ✅ Address verified<br>✅ User logged in<br>❌ No verification UI shown | **Recommended**: Clean UX, user is verified and logged in immediately |
| `- show_verification_ui`<br>`- session` | ✅ Address verified<br>✅ User logged in<br>✅ Verification UI shown | Show "verification successful" page for better UX |
| No hooks | ✅ Address verified<br>❌ User NOT logged in<br>❌ No verification UI | User must login manually after registration |

### For Password Method

| Hooks | Behavior | Use Case |
|-------|----------|----------|
| `- session` | ❌ Address NOT verified<br>✅ User logged in | **Not recommended**: User not verified but can access app |
| `- show_verification_ui`<br>`- session` | ❌ Address NOT verified<br>✅ User logged in<br>✅ Verification UI shown | User can verify email after registration |
| `- show_verification_ui` | ❌ Address NOT verified<br>❌ User NOT logged in<br>✅ Verification UI shown | User must verify before being logged in |

## Hook Combinations for Login

### Requiring Verification

| Hooks | Behavior | Use Case |
|-------|----------|----------|
| `- require_verified_address` | ❌ Blocks unverified users from logging in<br>✅ Shows verification UI in `continue_with` | **Recommended**: Enforce verification before login |
| No hooks | ✅ Allows login regardless of verification status | Not recommended for production |

## Configuration Examples

### Example 1: Passwordless Only (Recommended)

```yaml
selfservice:
  flows:
    registration:
      after:
        code:
          hooks:
            - hook: session
    login:
      after:
        code:
          hooks:
            - hook: require_verified_address
    verification:
      enabled: true
      use: code
  methods:
    code:
      passwordless_enabled: true
```

**Result**: 
- Registration with code automatically verifies and logs user in
- Login requires verification (extra safety, though code registration already verified)

### Example 2: Password + Code with Verification

```yaml
selfservice:
  flows:
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
    verification:
      enabled: true
      use: code
  methods:
    password:
      enabled: true
    code:
      passwordless_enabled: true
```

**Result**:
- Password registration: User shown verification UI, must verify to login later
- Code registration: User verified and logged in automatically
- Both login methods require verified address

### Example 3: All Methods with Strict Verification

```yaml
selfservice:
  flows:
    registration:
      after:
        password:
          hooks:
            - hook: show_verification_ui
            # Note: No session hook, user must verify before logging in
        code:
          hooks:
            - hook: show_verification_ui  # Optional: show success page
            - hook: session
    login:
      after:
        password:
          hooks:
            - hook: require_verified_address
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
```

**Result**:
- Password users MUST verify before they can login
- Code users are verified during registration and logged in
- Maximum security: all login attempts require verified address

## Flow Diagrams

### Code Registration Flow (with session hook)

```
User enters email → Code sent → User enters code → ✅ Email verified → ✅ Session created → Logged in
```

### Code Registration Flow (with show_verification_ui + session)

```
User enters email → Code sent → User enters code → ✅ Email verified → Verification UI shown → ✅ Session created → Logged in
```

### Password Registration Flow (with show_verification_ui hook)

```
User sets password → ✅ Session created → Verification UI shown → User enters code → ✅ Email verified → Logged in
```

### Login with require_verified_address

```
User attempts login → Is email verified?
  ├─ Yes → ✅ Login successful
  └─ No  → ❌ Login blocked → Show verification UI
```

## Key Insights

### ✅ Code Method Auto-Verification

The code method **automatically verifies** the address when the user successfully enters the code during registration. This is built into the strategy and happens at this line:

```go
// Step 4: Verify the address
if err := s.verifyAddress(ctx, i, Address{
    To:  registrationCode.Address,
    Via: registrationCode.AddressType,
}, false); err != nil {
    return err
}
```

### 🎯 When to Use show_verification_ui Hook

Use `show_verification_ui` hook when:
- You want to show a "verification successful" message
- You have a custom onboarding flow after verification
- You want consistent UX across password and code registration methods
- You need to collect additional information post-verification

**Don't use it** when:
- You want the fastest, most streamlined registration (just use `session` hook)
- You're only using code method and don't need extra UI

### 🔒 When to Use require_verified_address Hook

Use `require_verified_address` hook when:
- You need to block unverified users from logging in
- Regulatory compliance requires email/phone verification
- You want to prevent fake account creation
- Your app has sensitive data requiring verified users

### ⚠️ Hook Order Matters

Hooks execute in the order they're listed:

```yaml
hooks:
  - hook: show_verification_ui  # Executes first
  - hook: session               # Executes second
```

For registration:
1. If `show_verification_ui` is first, user sees verification UI
2. Then `session` creates the session (user is logged in)
3. After both hooks complete, user continues to the app

### 🔑 Security Best Practices

1. **Always enable verification** for production apps
2. **Use require_verified_address** on login for sensitive applications
3. **For code method**: The `session` hook alone is usually sufficient
4. **For password method**: Always use `show_verification_ui` or require verification before login
5. **Enable account enumeration mitigation** in production:
   ```yaml
   security:
     account_enumeration:
       mitigate: true
   ```

## Troubleshooting

### Issue: Verification UI not showing after registration

**Check**:
1. Is `show_verification_ui` hook configured?
2. Is verification flow enabled?
3. Is your frontend handling `continue_with` array?

### Issue: Users can't login after code registration

**Check**:
1. Is `require_verified_address` hook configured on login?
2. Code method should automatically verify - check if verification happened
3. Check identity in database: `verifiable_addresses[].verified` should be `true`

### Issue: Verification code not sent

**Check**:
1. Is courier configured correctly?
2. Check logs: `log.leak_sensitive_values: true` (dev only) to see codes
3. Is identity schema configured with `verification.via` extension?
4. For SMS: Is SMS courier configured?

## Testing Verification

### Check if Address is Verified

Query the identity via Admin API:

```bash
curl http://localhost:4434/admin/identities/<identity_id> | jq '.verifiable_addresses'
```

Look for:
```json
{
  "verifiable_addresses": [
    {
      "value": "user@example.com",
      "verified": true,
      "verified_at": "2024-11-30T12:00:00Z",
      "status": "completed",
      "via": "email"
    }
  ]
}
```

### Manual Verification via Admin API

Force verify an address:

```bash
curl -X PATCH http://localhost:4434/admin/identities/<identity_id> \
  -H "Content-Type: application/json" \
  -d '{
    "schema_id": "default",
    "state": "active",
    "verifiable_addresses": [
      {
        "value": "user@example.com",
        "verified": true,
        "via": "email"
      }
    ]
  }'
```

## Summary Table

| Scenario | Code Registration Hooks | Login Hooks | Verification Enabled |
|----------|------------------------|-------------|---------------------|
| Fastest UX | `session` | None | Optional |
| With success page | `show_verification_ui`, `session` | None | Required |
| Maximum security | `show_verification_ui`, `session` | `require_verified_address` | Required |
| Password-based | `show_verification_ui` | `require_verified_address` | Required |

For most passwordless applications: Use `session` hook only on code registration, and enable verification flow for manual verification if needed.
