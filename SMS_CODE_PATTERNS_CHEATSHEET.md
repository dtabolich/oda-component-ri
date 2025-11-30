# SMS Code Submission Patterns - Cheatsheet

## 🎯 The Pattern (Works for Both Registration and Login)

### The Golden Rule

**Always save and use the updated flow from each API call**

```typescript
// Step 1: Create flow
const { data: flow } = await kratos.create[Registration|Login]Flow()

// Step 2: Request code - SAVE RESPONSE ✅
const { data: updatedFlow } = await kratos.update[Registration|Login]Flow({
  flow: flow.id,
  ...
})

// Step 3: Submit code - USE UPDATED FLOW ✅
await kratos.update[Registration|Login]Flow({
  flow: updatedFlow.id,  // ← Use updated flow
  ...
})
```

## 📋 Registration vs Login Side-by-Side

### Registration Flow

```typescript
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

// ============================================
// REGISTRATION WITH SMS CODE
// ============================================

// 1. Initialize
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// 2. Request SMS code
const { data: updatedFlow } = await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: {                    // ← Use "traits"
      phone: "+1234567890"
    },
    csrf_token: getCsrfToken(flow)
  }
})

// 3. Submit SMS code
const { data: result } = await kratos.updateRegistrationFlow({
  flow: updatedFlow.id,          // ← Use updated flow
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: {                    // ← Use "traits"
      phone: "+1234567890"
    },
    csrf_token: getCsrfToken(updatedFlow)
  }
})

// Result: User registered + session created
console.log("Identity:", result.identity)
console.log("Session:", result.session)
```

### Login Flow

```typescript
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

// ============================================
// LOGIN WITH SMS CODE
// ============================================

// 1. Initialize
const { data: flow } = await kratos.createBrowserLoginFlow()

// 2. Request SMS code
const { data: updatedFlow } = await kratos.updateLoginFlow({
  flow: flow.id,
  updateLoginFlowBody: {
    method: "code",
    identifier: "+1234567890",   // ← Use "identifier"
    csrf_token: getCsrfToken(flow)
  }
})

// 3. Submit SMS code
const { data: result } = await kratos.updateLoginFlow({
  flow: updatedFlow.id,          // ← Use updated flow
  updateLoginFlowBody: {
    method: "code",
    code: "123456",
    identifier: "+1234567890",   // ← Use "identifier"
    csrf_token: getCsrfToken(updatedFlow)
  }
})

// Result: User logged in
console.log("Session:", result.session)
```

## 🔧 Helper Function (Use for Both)

```typescript
function getCsrfToken(flow: any): string {
  return flow.ui.nodes.find(
    (node: any) => node.attributes.name === "csrf_token"
  )?.attributes.value || ""
}
```

## 📊 Comparison Table

| Feature | Registration | Login |
|---------|--------------|-------|
| **Create Flow** | `createBrowserRegistrationFlow()` | `createBrowserLoginFlow()` |
| **Update Flow** | `updateRegistrationFlow()` | `updateLoginFlow()` |
| **Phone Field** | `traits: { phone }` | `identifier: phone` |
| **Request Body Type** | `UpdateRegistrationFlowBody` | `UpdateLoginFlowBody` |
| **Result** | `identity` + `session` | `session` only |
| **Error Message** | "registration code is invalid" | "login code is invalid" |

## ⚡ React Hook Pattern (Universal)

```typescript
function useKratosFlow<T>(
  flowType: 'registration' | 'login',
  kratos: FrontendApi
) {
  const [flow, setFlow] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const initialize = async () => {
    try {
      const { data } = flowType === 'registration'
        ? await kratos.createBrowserRegistrationFlow()
        : await kratos.createBrowserLoginFlow()
      
      setFlow(data)
      return data
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  const updateFlow = async (body: any) => {
    setLoading(true)
    try {
      const { data } = flowType === 'registration'
        ? await kratos.updateRegistrationFlow({
            flow: flow.id,
            updateRegistrationFlowBody: body
          })
        : await kratos.updateLoginFlow({
            flow: flow.id,
            updateLoginFlowBody: body
          })
      
      // ✅ Always update flow
      setFlow(data)
      return data
    } catch (err) {
      setError(err.response?.data?.ui?.messages?.[0]?.text || err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { flow, loading, error, initialize, updateFlow }
}

// Usage for Registration
const { flow, initialize, updateFlow } = useKratosFlow('registration', kratos)

// Usage for Login
const { flow, initialize, updateFlow } = useKratosFlow('login', kratos)
```

## 🎯 Complete Example (Choose Your Flow)

### Registration Example

```typescript
export function SmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")

  useEffect(() => {
    kratos.createBrowserRegistrationFlow()
      .then(({ data }) => setFlow(data))
  }, [])

  const requestCode = async () => {
    const { data: updated } = await kratos.updateRegistrationFlow({
      flow: flow.id,
      updateRegistrationFlowBody: {
        method: "code",
        traits: { phone },
        csrf_token: getCsrfToken(flow)
      }
    })
    setFlow(updated)  // ✅
    setStep("code")
  }

  const submitCode = async () => {
    await kratos.updateRegistrationFlow({
      flow: flow.id,  // Now using updated flow
      updateRegistrationFlowBody: {
        method: "code",
        code,
        traits: { phone },
        csrf_token: getCsrfToken(flow)
      }
    })
  }

  return (/* JSX */)
}
```

### Login Example

```typescript
export function SmsLogin() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")

  useEffect(() => {
    kratos.createBrowserLoginFlow()
      .then(({ data }) => setFlow(data))
  }, [])

  const requestCode = async () => {
    const { data: updated } = await kratos.updateLoginFlow({
      flow: flow.id,
      updateLoginFlowBody: {
        method: "code",
        identifier: phone,          // ← Different field
        csrf_token: getCsrfToken(flow)
      }
    })
    setFlow(updated)  // ✅
    setStep("code")
  }

  const submitCode = async () => {
    await kratos.updateLoginFlow({
      flow: flow.id,  // Now using updated flow
      updateLoginFlowBody: {
        method: "code",
        code,
        identifier: phone,          // ← Different field
        csrf_token: getCsrfToken(flow)
      }
    })
  }

  return (/* JSX */)
}
```

## 🚨 Common Mistakes

### ❌ Mistake 1: Not Saving Updated Flow

```typescript
// WRONG - Both flows
await kratos.update[Registration|Login]Flow({ ... })  // Response ignored!
await kratos.update[Registration|Login]Flow({ flow: flow.id, ... })  // Uses old flow
```

### ❌ Mistake 2: Wrong Field Name

```typescript
// WRONG - Using traits for login
updateLoginFlowBody: {
  traits: { phone }  // ❌
}

// CORRECT - Using identifier for login
updateLoginFlowBody: {
  identifier: phone  // ✅
}
```

### ❌ Mistake 3: Wrong Method Name

```typescript
// WRONG - Mixing methods
const { data: flow } = await kratos.createBrowserLoginFlow()
await kratos.updateRegistrationFlow({ ... })  // ❌ Wrong method!

// CORRECT - Matching methods
const { data: flow } = await kratos.createBrowserLoginFlow()
await kratos.updateLoginFlow({ ... })  // ✅ Correct method!
```

## ✅ Verification Checklist

After implementing, verify:

- [ ] You're using the correct `create` method for your flow type
- [ ] You're using the matching `update` method
- [ ] You're saving the response from first `update` call
- [ ] You're updating your state/variable with new flow
- [ ] You're using correct field (`traits` vs `identifier`)
- [ ] You're extracting CSRF token from current flow
- [ ] Phone format is E.164 (+1234567890)
- [ ] Code is 6 digits
- [ ] Flow state changes from `"choose_method"` to `"sent_email"`

## 🔍 Debug Template

```typescript
const requestCode = async () => {
  console.log("=== REQUEST CODE ===")
  console.log("Flow type:", "[registration|login]")
  console.log("Flow ID:", flow.id)
  console.log("Flow state:", flow.state)
  console.log("Phone:", phone)
  console.log("CSRF:", getCsrfToken(flow)?.substring(0, 20))
  
  const { data: updated } = await kratos.update[Registration|Login]Flow(...)
  
  console.log("=== AFTER REQUEST ===")
  console.log("Updated flow ID:", updated.id, "(should match)")
  console.log("Updated state:", updated.state, "(should be 'sent_email')")
  
  setFlow(updated)
}

const submitCode = async () => {
  console.log("=== SUBMIT CODE ===")
  console.log("Flow ID:", flow.id)
  console.log("Flow state:", flow.state, "(should be 'sent_email')")
  console.log("Code:", code)
  
  const { data: result } = await kratos.update[Registration|Login]Flow(...)
  
  console.log("=== SUCCESS ===")
  console.log("Result:", result)
}
```

## 🎓 Learning Path

1. **Start here**: [QUICK_FIX_INVALID_CODE.md](QUICK_FIX_INVALID_CODE.md)
2. **For login specifically**: [FIX_LOGIN_CODE_ERROR.md](FIX_LOGIN_CODE_ERROR.md)
3. **Full guide**: [SUBMIT_SMS_CODE_SDK_GUIDE.md](SUBMIT_SMS_CODE_SDK_GUIDE.md)
4. **Troubleshooting**: [TROUBLESHOOT_INVALID_CODE_ERROR.md](TROUBLESHOOT_INVALID_CODE_ERROR.md)

## 🎯 Quick Reference Card

```typescript
// Registration Pattern
const flow = await kratos.createBrowserRegistrationFlow()
const updated = await kratos.updateRegistrationFlow({ 
  flow: flow.id, 
  updateRegistrationFlowBody: { 
    method: "code", 
    traits: { phone } 
  }
})
await kratos.updateRegistrationFlow({ 
  flow: updated.id,  // ← Updated!
  updateRegistrationFlowBody: { 
    method: "code", 
    code, 
    traits: { phone } 
  }
})

// Login Pattern
const flow = await kratos.createBrowserLoginFlow()
const updated = await kratos.updateLoginFlow({ 
  flow: flow.id, 
  updateLoginFlowBody: { 
    method: "code", 
    identifier: phone  // ← identifier, not traits
  }
})
await kratos.updateLoginFlow({ 
  flow: updated.id,  // ← Updated!
  updateLoginFlowBody: { 
    method: "code", 
    code, 
    identifier: phone  // ← identifier, not traits
  }
})
```

Remember: **Same pattern, different fields!**
