# Fix: "The login code is invalid or has already been used"

## 🚨 Same Issue, Different Flow

You're hitting the same bug in the **login flow** that you had in registration.

## ❌ What You're Probably Doing (Login)

```typescript
// Create login flow
const { data: flow } = await kratos.createBrowserLoginFlow()

// Submit phone number (request SMS)
await kratos.updateLoginFlow({
  flow: flow.id,
  updateLoginFlowBody: {
    method: "code",
    identifier: "+1234567890"
  }
})

// Submit code - using SAME flow variable
await kratos.updateLoginFlow({
  flow: flow.id,  // ❌ WRONG - using original flow
  updateLoginFlowBody: {
    method: "code",
    code: "123456",
    identifier: "+1234567890"
  }
})
// Error: "login code is invalid or has already been used"
```

## ✅ The Fix for Login

```typescript
// Create login flow
const { data: flow } = await kratos.createBrowserLoginFlow()

// Submit phone number - SAVE THE RESPONSE
const { data: updatedFlow } = await kratos.updateLoginFlow({
  flow: flow.id,
  updateLoginFlowBody: {
    method: "code",
    identifier: "+1234567890",
    csrf_token: getCsrfToken(flow)
  }
})

// Submit code - use UPDATED flow
const { data: result } = await kratos.updateLoginFlow({
  flow: updatedFlow.id,  // ✅ CORRECT - using updated flow
  updateLoginFlowBody: {
    method: "code",
    code: "123456",
    identifier: "+1234567890",
    csrf_token: getCsrfToken(updatedFlow)  // ✅ Updated CSRF too
  }
})

console.log("Login successful!", result.session)
```

## 🔧 Complete Working Login Component

```typescript
import { useState, useEffect } from 'react'
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.REACT_APP_KRATOS_URL || "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

export function SmsLogin() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Initialize login flow on mount
  useEffect(() => {
    kratos.createBrowserLoginFlow()
      .then(({ data }) => {
        console.log("✅ Login flow created:", data.id)
        setFlow(data)
      })
      .catch(err => {
        console.error("❌ Failed to create login flow:", err)
        setError("Failed to initialize login")
      })
  }, [])

  const getCsrfToken = () => {
    return flow?.ui.nodes.find(
      node => node.attributes.name === "csrf_token"
    )?.attributes.value
  }

  // Step 1: Request SMS code
  const handleRequestCode = async () => {
    setLoading(true)
    setError("")

    try {
      console.log("📱 Requesting SMS code for:", phoneNumber)
      console.log("📋 Using flow ID:", flow.id)
      console.log("📋 Flow state before:", flow.state)

      // ✅ CRITICAL: Save the updated flow
      const { data: updatedFlow } = await kratos.updateLoginFlow({
        flow: flow.id,
        updateLoginFlowBody: {
          method: "code",
          identifier: phoneNumber,
          csrf_token: getCsrfToken()
        }
      })

      console.log("✅ SMS sent!")
      console.log("📋 Updated flow ID:", updatedFlow.id)
      console.log("📋 Flow state after:", updatedFlow.state)

      // ✅ CRITICAL: Update the flow state
      setFlow(updatedFlow)
      setStep("code")
    } catch (err) {
      console.error("❌ Error requesting SMS:", err)
      const errorMsg = err.response?.data?.ui?.messages?.[0]?.text
      setError(errorMsg || "Failed to send SMS")
    } finally {
      setLoading(false)
    }
  }

  // Step 2: Submit SMS code
  const handleSubmitCode = async () => {
    setLoading(true)
    setError("")

    try {
      console.log("🔐 Verifying login code:", code)
      console.log("📋 Using flow ID:", flow.id)
      console.log("📋 Flow state:", flow.state)

      const { data: result } = await kratos.updateLoginFlow({
        flow: flow.id,  // Now this is the updated flow
        updateLoginFlowBody: {
          method: "code",
          code: code,
          identifier: phoneNumber,
          csrf_token: getCsrfToken()
        }
      })

      console.log("✅ Login successful!")
      console.log("Session:", result.session)

      // Redirect to dashboard
      window.location.href = "/dashboard"
    } catch (err) {
      console.error("❌ Error verifying code:", err)

      const errorMsg = err.response?.data?.ui?.messages?.[0]?.text
      setError(errorMsg || "Invalid code")

      // If code already used or flow expired, restart
      if (errorMsg?.includes("already been used") || errorMsg?.includes("invalid")) {
        if (window.confirm("Code invalid. Start over?")) {
          window.location.reload()
        }
      }
    } finally {
      setLoading(false)
    }
  }

  if (!flow) {
    return <div>Loading...</div>
  }

  return (
    <div className="sms-login">
      <h2>Login with Phone</h2>

      {error && (
        <div className="error" style={{ 
          padding: '10px', 
          background: '#fee', 
          color: '#c00',
          marginBottom: '10px'
        }}>
          {error}
        </div>
      )}

      {step === "phone" && (
        <div>
          <label htmlFor="phone">Phone Number</label>
          <input
            id="phone"
            type="tel"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="+1234567890"
            disabled={loading}
          />
          <button 
            onClick={handleRequestCode} 
            disabled={loading || !phoneNumber}
          >
            {loading ? "Sending..." : "Send Code"}
          </button>
        </div>
      )}

      {step === "code" && (
        <div>
          <p>Enter the code sent to {phoneNumber}</p>
          <label htmlFor="code">Verification Code</label>
          <input
            id="code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456"
            maxLength={6}
            autoComplete="one-time-code"
            disabled={loading}
          />
          <button 
            onClick={handleSubmitCode} 
            disabled={loading || code.length !== 6}
          >
            {loading ? "Verifying..." : "Login"}
          </button>
          <button 
            onClick={() => setStep("phone")} 
            disabled={loading}
          >
            Change Number
          </button>
        </div>
      )}

      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
        <details>
          <summary>Debug Info</summary>
          <pre>{JSON.stringify({
            flowId: flow?.id,
            state: flow?.state,
            step,
            phone: phoneNumber,
            codeLength: code.length
          }, null, 2)}</pre>
        </details>
      </div>
    </div>
  )
}
```

## 🔑 Key Differences: Login vs Registration

| Aspect | Registration | Login |
|--------|-------------|-------|
| **Flow Method** | `createBrowserRegistrationFlow()` | `createBrowserLoginFlow()` |
| **Update Method** | `updateRegistrationFlow()` | `updateLoginFlow()` |
| **Phone Field** | `traits: { phone }` | `identifier: phone` |
| **Error Message** | "registration code is invalid" | "login code is invalid" |
| **Result** | Creates identity + session | Returns existing session |

## 📊 Side-by-Side Comparison

### Registration Flow

```typescript
// Create
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// Request code
const { data: updated } = await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: { phone: "+1234567890" },  // ← traits
    csrf_token: getCsrf()
  }
})

// Submit code
await kratos.updateRegistrationFlow({
  flow: updated.id,
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: { phone: "+1234567890" },  // ← traits
    csrf_token: getCsrf()
  }
})
```

### Login Flow

```typescript
// Create
const { data: flow } = await kratos.createBrowserLoginFlow()

// Request code
const { data: updated } = await kratos.updateLoginFlow({
  flow: flow.id,
  updateLoginFlowBody: {
    method: "code",
    identifier: "+1234567890",  // ← identifier (not traits)
    csrf_token: getCsrf()
  }
})

// Submit code
await kratos.updateLoginFlow({
  flow: updated.id,
  updateLoginFlowBody: {
    method: "code",
    code: "123456",
    identifier: "+1234567890",  // ← identifier (not traits)
    csrf_token: getCsrf()
  }
})
```

## 🔍 Debugging Your Login Flow

Add this logging to see what's happening:

```typescript
const handleRequestCode = async () => {
  console.log("=== BEFORE REQUEST CODE ===")
  console.log("Flow ID:", flow.id)
  console.log("Flow state:", flow.state)
  console.log("CSRF token:", getCsrfToken()?.substring(0, 20) + "...")
  
  const { data: updatedFlow } = await kratos.updateLoginFlow(...)
  
  console.log("=== AFTER REQUEST CODE ===")
  console.log("Flow ID:", updatedFlow.id, "(should be same)")
  console.log("Flow state:", updatedFlow.state, "(should be 'sent_email')")
  console.log("CSRF token:", getCsrfToken(updatedFlow)?.substring(0, 20) + "...")
  
  setFlow(updatedFlow)
}

const handleSubmitCode = async () => {
  console.log("=== SUBMITTING CODE ===")
  console.log("Flow ID:", flow.id)
  console.log("Flow state:", flow.state)
  console.log("Code:", code)
  console.log("Phone:", phoneNumber)
  
  const { data: result } = await kratos.updateLoginFlow(...)
  
  console.log("=== LOGIN SUCCESS ===")
  console.log("Session ID:", result.session.id)
  console.log("Identity ID:", result.session.identity.id)
}
```

## 🎯 Quick Checklist

Before submitting the code, verify:

- [ ] You saved the response from first `updateLoginFlow` call
- [ ] You updated your state/variable with the new flow
- [ ] You're using `flow.id` from the UPDATED flow
- [ ] You're getting CSRF token from the UPDATED flow
- [ ] The flow state changed to `"sent_email"`
- [ ] You're using `identifier` not `traits` for login
- [ ] Phone number format is correct (+1234567890)
- [ ] Code is 6 digits

## 🔧 Class-Based Alternative

If you prefer a class-based approach:

```typescript
class LoginFlowManager {
  private currentFlow: any = null
  private kratos: FrontendApi

  constructor(kratosUrl: string) {
    this.kratos = new FrontendApi(
      new Configuration({
        basePath: kratosUrl,
        baseOptions: { withCredentials: true }
      })
    )
  }

  async initialize() {
    const { data } = await this.kratos.createBrowserLoginFlow()
    this.currentFlow = data
    console.log("Login flow initialized:", data.id)
    return data
  }

  async requestSmsCode(phoneNumber: string) {
    console.log("Requesting SMS for:", phoneNumber)
    
    const { data: updatedFlow } = await this.kratos.updateLoginFlow({
      flow: this.currentFlow.id,
      updateLoginFlowBody: {
        method: "code",
        identifier: phoneNumber,
        csrf_token: this.getCsrfToken()
      }
    })

    // ✅ Always update current flow
    this.currentFlow = updatedFlow
    console.log("SMS sent, flow state:", updatedFlow.state)
    
    return updatedFlow
  }

  async submitCode(phoneNumber: string, code: string) {
    console.log("Submitting code:", code)
    
    const { data: result } = await this.kratos.updateLoginFlow({
      flow: this.currentFlow.id,  // Uses latest flow
      updateLoginFlowBody: {
        method: "code",
        code: code,
        identifier: phoneNumber,
        csrf_token: this.getCsrfToken()
      }
    })

    console.log("Login successful!")
    return result
  }

  private getCsrfToken(): string {
    return this.currentFlow?.ui.nodes.find(
      (node: any) => node.attributes.name === "csrf_token"
    )?.attributes.value || ""
  }
}

// Usage
const loginFlow = new LoginFlowManager("http://localhost:4433")
await loginFlow.initialize()
await loginFlow.requestSmsCode("+1234567890")
// User receives SMS...
const result = await loginFlow.submitCode("+1234567890", "123456")
```

## 🚨 Common Mistakes

### Mistake 1: Not saving updated flow

```typescript
// ❌ WRONG
await kratos.updateLoginFlow({ ... })  // Response thrown away!
await kratos.updateLoginFlow({ flow: flow.id, ... })  // Using old flow
```

```typescript
// ✅ CORRECT
const { data: updated } = await kratos.updateLoginFlow({ ... })
setFlow(updated)  // Save it!
await kratos.updateLoginFlow({ flow: updated.id, ... })
```

### Mistake 2: Using traits instead of identifier

```typescript
// ❌ WRONG - This is for registration
updateLoginFlowBody: {
  method: "code",
  traits: { phone: "+1234567890" }  // Wrong field!
}
```

```typescript
// ✅ CORRECT - This is for login
updateLoginFlowBody: {
  method: "code",
  identifier: "+1234567890"  // Correct field!
}
```

### Mistake 3: Reusing same flow for multiple attempts

```typescript
// ❌ WRONG
const flow = await createLoginFlow()
await requestCode(flow)  // First attempt
// ... fails ...
await requestCode(flow)  // Second attempt - flow is broken!
```

```typescript
// ✅ CORRECT
const flow = await createLoginFlow()
const updated = await requestCode(flow)
// ... fails ...
// Restart with new flow
const newFlow = await createLoginFlow()
await requestCode(newFlow)
```

## 📱 Testing It

### Test 1: Check Flow Updates

```typescript
console.log("Before:", flow.id)
const { data: updated } = await kratos.updateLoginFlow(...)
console.log("After:", updated.id)
console.log("Are they equal?", flow.id === updated.id)  // Should be true
console.log("State changed?", flow.state !== updated.state)  // Should be true
```

### Test 2: Manual curl Test

```bash
# Create login flow
FLOW=$(curl -s http://localhost:4433/self-service/login/api | jq -r '.id')
echo "Flow: $FLOW"

# Request SMS
curl -X POST "http://localhost:4433/self-service/login?flow=$FLOW" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","identifier":"+1234567890"}' | jq

# Check MailSlurper for code
# Then submit code (use SAME flow ID!)
curl -X POST "http://localhost:4433/self-service/login?flow=$FLOW" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","code":"123456","identifier":"+1234567890"}' | jq
```

## 📚 Related Docs

- [QUICK_FIX_INVALID_CODE.md](QUICK_FIX_INVALID_CODE.md) - General fix
- [TROUBLESHOOT_INVALID_CODE_ERROR.md](TROUBLESHOOT_INVALID_CODE_ERROR.md) - Detailed troubleshooting
- [SUBMIT_SMS_CODE_SDK_GUIDE.md](SUBMIT_SMS_CODE_SDK_GUIDE.md) - Complete SDK guide

## Summary

**For login flows**:
1. Use `createBrowserLoginFlow()` / `updateLoginFlow()`
2. Use `identifier` field (not `traits`)
3. Save and use the updated flow after requesting code
4. Same principle as registration, different methods/fields

The fix is the same: **Always use the updated flow from the previous call!**
