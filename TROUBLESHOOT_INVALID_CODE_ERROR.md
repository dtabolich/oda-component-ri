# Troubleshooting: "The registration code is invalid or has already been used"

This error occurs when submitting an SMS/email code to Kratos. Here are the most common causes and solutions.

## 🔍 Common Causes

1. **Flow was already used/completed** (most common)
2. **Code was already submitted once**
3. **Flow expired** (default: 1 hour)
4. **Wrong flow ID** being used
5. **CSRF token mismatch**
6. **Code copied incorrectly**

## 🚨 Most Common Issue: Reusing the Same Flow

### ❌ WRONG - Reusing Flow

```typescript
// DON'T DO THIS
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// First submission - sends SMS
await kratos.updateRegistrationFlow({ flow: flow.id, ... })

// User gets code "123456"

// Second submission - tries to verify code
await kratos.updateRegistrationFlow({ 
  flow: flow.id,  // ❌ Using original flow.id
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: { phone: "+1234567890" },
    csrf_token: getCsrfToken(flow)  // ❌ Using original CSRF token
  }
})
// Error: "code is invalid or has already been used"
```

### ✅ CORRECT - Use Updated Flow

```typescript
// Step 1: Create flow
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// Step 2: Request SMS code - SAVE THE RESPONSE
const { data: updatedFlow } = await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: { phone: "+1234567890" },
    csrf_token: getCsrfToken(flow)
  }
})

// Step 3: Submit code - USE UPDATED FLOW
const { data: result } = await kratos.updateRegistrationFlow({
  flow: updatedFlow.id,  // ✅ Use updated flow
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: { phone: "+1234567890" },
    csrf_token: getCsrfToken(updatedFlow)  // ✅ Use updated CSRF token
  }
})
```

## 🔧 Solution 1: Track Flow State Properly

### React Component - Correct Pattern

```typescript
import { useState, useEffect } from 'react'
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

export function SmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [code, setCode] = useState("")
  const [step, setStep] = useState<"phone" | "code">("phone")

  // Initialize flow on mount
  useEffect(() => {
    kratos.createBrowserRegistrationFlow()
      .then(({ data }) => {
        console.log("Initial flow created:", data.id)
        setFlow(data)
      })
  }, [])

  const getCsrfToken = () => {
    return flow?.ui.nodes.find(
      node => node.attributes.name === "csrf_token"
    )?.attributes.value
  }

  const handleSendCode = async () => {
    try {
      console.log("Requesting SMS code with flow:", flow.id)
      
      // ✅ Save the updated flow
      const { data: updatedFlow } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          traits: { phone: phoneNumber },
          csrf_token: getCsrfToken()
        }
      })
      
      console.log("SMS sent, updated flow:", updatedFlow.id)
      console.log("Flow state:", updatedFlow.state)
      
      // ✅ CRITICAL: Update the flow state
      setFlow(updatedFlow)
      setStep("code")
    } catch (error) {
      console.error("Error sending SMS:", error)
    }
  }

  const handleVerifyCode = async () => {
    try {
      console.log("Verifying code with flow:", flow.id)
      console.log("Flow state before verification:", flow.state)
      
      // ✅ Use the current (updated) flow
      const { data: result } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          code: code,
          traits: { phone: phoneNumber },
          csrf_token: getCsrfToken()
        }
      })
      
      console.log("Registration complete!", result)
      // Success!
    } catch (error) {
      console.error("Error verifying code:", error)
      
      // Check if flow expired
      if (error.response?.status === 410) {
        alert("Session expired. Starting over...")
        window.location.reload()
      }
    }
  }

  if (!flow) return <div>Loading...</div>

  return (
    <div>
      {step === "phone" && (
        <>
          <input 
            value={phoneNumber} 
            onChange={e => setPhoneNumber(e.target.value)}
            placeholder="+1234567890"
          />
          <button onClick={handleSendCode}>Send Code</button>
        </>
      )}

      {step === "code" && (
        <>
          <input 
            value={code} 
            onChange={e => setCode(e.target.value)}
            placeholder="123456"
            maxLength={6}
          />
          <button onClick={handleVerifyCode}>Verify Code</button>
        </>
      )}
    </div>
  )
}
```

## 🔧 Solution 2: Always Use Latest Flow

```typescript
class RegistrationFlowManager {
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
    const { data } = await this.kratos.createBrowserRegistrationFlow()
    this.currentFlow = data
    return data
  }

  async requestSmsCode(phoneNumber: string) {
    if (!this.currentFlow) {
      throw new Error("Flow not initialized")
    }

    const { data: updatedFlow } = await this.kratos.updateRegistrationFlow({
      flow: this.currentFlow.id,
      updateRegistrationFlowBody: {
        method: "code",
        traits: { phone: phoneNumber },
        csrf_token: this.getCsrfToken()
      }
    })

    // ✅ Always update the flow
    this.currentFlow = updatedFlow
    return updatedFlow
  }

  async submitCode(phoneNumber: string, code: string) {
    if (!this.currentFlow) {
      throw new Error("Flow not initialized")
    }

    const { data: result } = await this.kratos.updateRegistrationFlow({
      flow: this.currentFlow.id,  // ✅ Uses latest flow
      updateRegistrationFlowBody: {
        method: "code",
        code: code,
        traits: { phone: phoneNumber },
        csrf_token: this.getCsrfToken()
      }
    })

    return result
  }

  private getCsrfToken(): string {
    return this.currentFlow?.ui.nodes.find(
      (node: any) => node.attributes.name === "csrf_token"
    )?.attributes.value || ""
  }
}

// Usage
const flowManager = new RegistrationFlowManager("http://localhost:4433")
await flowManager.initialize()
await flowManager.requestSmsCode("+1234567890")
// User receives SMS...
await flowManager.submitCode("+1234567890", "123456")
```

## 🔧 Solution 3: Check Flow State

```typescript
async function debugFlow(flow: any) {
  console.log("=== Flow Debug Info ===")
  console.log("Flow ID:", flow.id)
  console.log("Flow State:", flow.state)
  console.log("Flow Expires At:", flow.expires_at)
  console.log("Flow Active:", flow.active)
  
  // Check if flow is expired
  const expiresAt = new Date(flow.expires_at)
  const now = new Date()
  const isExpired = expiresAt < now
  
  console.log("Is Expired:", isExpired)
  console.log("Time until expiry:", Math.floor((expiresAt - now) / 1000), "seconds")
  
  // Check for error messages
  if (flow.ui?.messages?.length > 0) {
    console.log("Messages:", flow.ui.messages)
  }
  
  console.log("===================")
}

// Usage
const { data: flow } = await kratos.createBrowserRegistrationFlow()
debugFlow(flow)

const { data: updatedFlow } = await kratos.updateRegistrationFlow(...)
debugFlow(updatedFlow)  // Should show state: "sent_email"
```

## 🔧 Solution 4: Handle Flow Expiration

```typescript
async function submitCodeWithRetry(
  kratos: FrontendApi,
  flowId: string,
  phoneNumber: string,
  code: string,
  getCsrfToken: () => string
) {
  try {
    const { data: result } = await kratos.updateRegistrationFlow({
      flow: flowId,
      updateRegistrationFlowBody: {
        method: "code",
        code: code,
        traits: { phone: phoneNumber },
        csrf_token: getCsrfToken()
      }
    })
    return { success: true, data: result }
  } catch (error) {
    const status = error.response?.status

    if (status === 410) {
      // Flow expired - need to restart
      return {
        success: false,
        error: "Flow expired. Please start over.",
        shouldRestart: true
      }
    } else if (status === 400) {
      const messages = error.response?.data?.ui?.messages || []
      const errorText = messages[0]?.text || "Invalid code"
      
      if (errorText.includes("already been used")) {
        return {
          success: false,
          error: "Code already used. Request a new code.",
          shouldRequestNewCode: true
        }
      } else if (errorText.includes("invalid")) {
        return {
          success: false,
          error: "Invalid code. Please check and try again.",
          canRetry: true
        }
      }
    }

    return {
      success: false,
      error: error.message || "Unknown error"
    }
  }
}

// Usage
const result = await submitCodeWithRetry(kratos, flow.id, phone, code, getCsrfToken)
if (!result.success) {
  if (result.shouldRestart) {
    // Restart entire flow
    window.location.reload()
  } else if (result.shouldRequestNewCode) {
    // Request new code
    setStep("phone")
  } else if (result.canRetry) {
    // Show error, let user try again
    setError(result.error)
  }
}
```

## 🔧 Solution 5: Reset Flow When Code Already Used

```typescript
function SmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [error, setError] = useState("")

  const resetFlow = async () => {
    console.log("Resetting flow...")
    const { data: newFlow } = await kratos.createBrowserRegistrationFlow()
    setFlow(newFlow)
    setError("")
    setStep("phone")
    setCode("")
  }

  const handleVerifyCode = async () => {
    try {
      const { data: result } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          code: code,
          traits: { phone: phoneNumber },
          csrf_token: getCsrfToken()
        }
      })
      // Success!
    } catch (error) {
      const errorMsg = error.response?.data?.ui?.messages?.[0]?.text || ""
      
      if (errorMsg.includes("already been used") || errorMsg.includes("invalid")) {
        setError("Code invalid or already used. Starting over...")
        // Reset the entire flow
        await resetFlow()
      } else {
        setError(errorMsg)
      }
    }
  }

  return (
    <div>
      {error && (
        <div className="error">
          {error}
          <button onClick={resetFlow}>Start Over</button>
        </div>
      )}
      {/* rest of component */}
    </div>
  )
}
```

## 🐛 Debugging Checklist

Run through these checks:

### 1. Log Flow IDs

```typescript
console.log("Initial flow ID:", flow.id)

const { data: updatedFlow } = await kratos.updateRegistrationFlow(...)
console.log("Updated flow ID:", updatedFlow.id)

// ❓ Are they the same?
// ✅ They should be the same ID
// ❌ If different, something is wrong
```

### 2. Check Flow State

```typescript
console.log("Flow state:", flow.state)
// Should be:
// - "choose_method" initially
// - "sent_email" after requesting code
// - "passed_challenge" after successful verification
```

### 3. Verify CSRF Token

```typescript
console.log("CSRF token:", getCsrfToken())
// Should be a long string
// ❌ If undefined/null, flow is corrupted
```

### 4. Check Code Format

```typescript
console.log("Code being submitted:", code)
console.log("Code length:", code.length)
console.log("Code is numeric:", /^\d+$/.test(code))
// Should be: "123456", length 6, all digits
```

### 5. Check Phone Number Format

```typescript
console.log("Phone number:", phoneNumber)
// Should be in E.164 format: +1234567890
// NOT: (123) 456-7890 or 123-456-7890
```

### 6. Inspect Full Error

```typescript
catch (error) {
  console.log("=== ERROR DEBUG ===")
  console.log("Status:", error.response?.status)
  console.log("Data:", JSON.stringify(error.response?.data, null, 2))
  console.log("Messages:", error.response?.data?.ui?.messages)
  console.log("==================")
}
```

## 💡 Quick Fix: Start Fresh

If you're stuck, the fastest solution is to restart the flow:

```typescript
// Clear everything and start over
async function startFresh() {
  // Create brand new flow
  const { data: newFlow } = await kratos.createBrowserRegistrationFlow()
  setFlow(newFlow)
  setPhoneNumber("")
  setCode("")
  setStep("phone")
  setError("")
  
  console.log("Started fresh with new flow:", newFlow.id)
}

// Call this if you get the error
<button onClick={startFresh}>Start Over</button>
```

## 🎯 Working Example (Copy-Paste Ready)

```typescript
import { useState, useEffect } from 'react'
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.REACT_APP_KRATOS_URL || "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

export function WorkingSmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Initialize on mount
  useEffect(() => {
    initFlow()
  }, [])

  const initFlow = async () => {
    try {
      const { data } = await kratos.createBrowserRegistrationFlow()
      console.log("✅ Flow created:", data.id)
      setFlow(data)
    } catch (err) {
      setError("Failed to initialize")
    }
  }

  const getCsrf = () => 
    flow?.ui.nodes.find(n => n.attributes.name === "csrf_token")?.attributes.value

  const requestCode = async () => {
    setLoading(true)
    setError("")
    
    try {
      console.log("📱 Requesting SMS to:", phone)
      console.log("📋 Using flow ID:", flow.id)
      
      const { data: updated } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          traits: { phone },
          csrf_token: getCsrf()
        }
      })
      
      console.log("✅ SMS sent, new state:", updated.state)
      console.log("📋 Flow ID after update:", updated.id)
      
      // ✅ CRITICAL: Save updated flow
      setFlow(updated)
      setStep("code")
    } catch (err) {
      console.error("❌ Error requesting SMS:", err)
      setError(err.response?.data?.ui?.messages?.[0]?.text || "Failed to send SMS")
    } finally {
      setLoading(false)
    }
  }

  const verifyCode = async () => {
    setLoading(true)
    setError("")
    
    try {
      console.log("🔐 Verifying code:", code)
      console.log("📋 Using flow ID:", flow.id)
      console.log("📋 Flow state:", flow.state)
      
      const { data: result } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          code,
          traits: { phone },
          csrf_token: getCsrf()
        }
      })
      
      console.log("✅ Registration complete!", result)
      
      // Check verification
      const verified = result.identity.verifiable_addresses?.[0]?.verified
      console.log("📱 Phone verified:", verified)
      
      // Redirect or show success
      alert("Registration successful!")
      window.location.href = "/dashboard"
    } catch (err) {
      console.error("❌ Error verifying code:", err)
      
      const errorMsg = err.response?.data?.ui?.messages?.[0]?.text || "Verification failed"
      setError(errorMsg)
      
      // If code already used or invalid, offer to restart
      if (errorMsg.includes("already been used") || errorMsg.includes("invalid")) {
        if (window.confirm("Code invalid. Start over?")) {
          initFlow()
          setStep("phone")
          setCode("")
        }
      }
    } finally {
      setLoading(false)
    }
  }

  if (!flow) return <div>Loading...</div>

  return (
    <div>
      <h2>Register with Phone</h2>
      
      {error && (
        <div style={{ color: 'red', padding: '10px', background: '#fee' }}>
          {error}
          <button onClick={initFlow}>Restart</button>
        </div>
      )}

      {step === "phone" && (
        <div>
          <input
            type="tel"
            value={phone}
            onChange={e => setPhone(e.target.value)}
            placeholder="+1234567890"
            disabled={loading}
          />
          <button onClick={requestCode} disabled={loading || !phone}>
            {loading ? "Sending..." : "Send Code"}
          </button>
        </div>
      )}

      {step === "code" && (
        <div>
          <p>Enter code sent to {phone}</p>
          <input
            type="text"
            value={code}
            onChange={e => setCode(e.target.value)}
            placeholder="123456"
            maxLength={6}
            disabled={loading}
            autoComplete="one-time-code"
          />
          <button onClick={verifyCode} disabled={loading || code.length !== 6}>
            {loading ? "Verifying..." : "Verify"}
          </button>
          <button onClick={() => setStep("phone")} disabled={loading}>
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
            phone,
            codeLength: code.length
          }, null, 2)}</pre>
        </details>
      </div>
    </div>
  )
}
```

## 🔍 Still Having Issues?

### Check Kratos Logs

```bash
docker logs <kratos-container> | grep -A 5 "registration"
```

### Inspect Network Tab

1. Open browser DevTools → Network
2. Filter by "registration"
3. Look at:
   - Request payload (is flow ID correct?)
   - Response (what's the error message?)
   - Response headers (check Set-Cookie)

### Test with curl

```bash
# Create flow
FLOW=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')
echo "Flow ID: $FLOW"

# Request code
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","traits":{"phone":"+1234567890"}}'

# Get code from logs/MailSlurper

# Submit code (use same flow ID!)
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW" \
  -H "Content-Type: application/json" \
  -d '{"method":"code","code":"123456","traits":{"phone":"+1234567890"}}'
```

## Summary: The Fix

**The most common issue**: Not using the updated flow after requesting the code.

```typescript
// ❌ WRONG
const flow = await createFlow()
await requestCode(flow.id)  // This returns updated flow
await submitCode(flow.id)   // Still using original flow ID

// ✅ CORRECT  
const flow = await createFlow()
const updatedFlow = await requestCode(flow.id)  // Save the return
await submitCode(updatedFlow.id)  // Use updated flow ID
```

**Always**:
1. Save the response from `updateRegistrationFlow`
2. Use the updated flow for the next call
3. Update your state/variable with the new flow

This should fix your issue!
