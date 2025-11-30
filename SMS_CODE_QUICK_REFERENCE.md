# SMS Code Submission - Quick Reference

## 🚀 Fastest Way: SDK Method

### Installation

```bash
npm install @ory/client
```

### Setup

```typescript
import { FrontendApi, Configuration } from "@ory/client"

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)
```

### The SDK Method You Need

#### For Registration:

```typescript
// ✅ THIS IS WHAT YOU NEED FOR REGISTRATION
await kratos.updateRegistrationFlow({
  flow: flowId,  // From createBrowserRegistrationFlow()
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",        // ← The SMS code
    traits: {
      phone: "+1234567890" // ← Same phone as before
    },
    csrf_token: csrfToken  // From flow.ui.nodes
  }
})
```

#### For Login:

```typescript
// ✅ THIS IS WHAT YOU NEED FOR LOGIN
await kratos.updateLoginFlow({
  flow: flowId,  // From createBrowserLoginFlow()
  updateLoginFlowBody: {
    method: "code",
    code: "123456",           // ← The SMS code
    identifier: "+1234567890", // ← Same phone as before
    csrf_token: csrfToken
  }
})
```

## 📱 Complete 2-Step Flow

### Step 1: Request SMS Code

```typescript
// Create flow
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// Request code to be sent
await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: {
      phone: "+1234567890"
    },
    csrf_token: getCsrfToken(flow)
  }
})
// SMS is sent to the phone number
```

### Step 2: Submit SMS Code

```typescript
// User receives SMS with code "123456"
// Submit the code
await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",  // ← The code from SMS
    traits: {
      phone: "+1234567890"
    },
    csrf_token: getCsrfToken(flow)
  }
})
// ✅ Done! User registered and phone verified
```

## 🔧 Helper Function

```typescript
function getCsrfToken(flow: any): string {
  return flow.ui.nodes.find(
    (node: any) => node.attributes.name === "csrf_token"
  )?.attributes.value || ""
}
```

## 📋 Full Example

```typescript
import { FrontendApi, Configuration } from "@ory/client"

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433",
    baseOptions: { withCredentials: true }
  })
)

async function registerWithSms(phoneNumber: string, code: string) {
  // Step 1: Create flow
  const { data: flow } = await kratos.createBrowserRegistrationFlow()
  
  // Step 2: Request SMS code
  await kratos.updateRegistrationFlow({
    flow: flow.id,
    updateRegistrationFlowBody: {
      method: "code",
      traits: { phone: phoneNumber },
      csrf_token: flow.ui.nodes.find(n => n.attributes.name === "csrf_token")
        ?.attributes.value
    }
  })
  
  // User receives SMS with code...
  
  // Step 3: Submit code
  const { data: result } = await kratos.updateRegistrationFlow({
    flow: flow.id,
    updateRegistrationFlowBody: {
      method: "code",
      code: code,
      traits: { phone: phoneNumber },
      csrf_token: flow.ui.nodes.find(n => n.attributes.name === "csrf_token")
        ?.attributes.value
    }
  })
  
  return result // Contains identity and session
}

// Usage
const result = await registerWithSms("+1234567890", "123456")
console.log("Registered!", result.identity)
console.log("Phone verified:", result.identity.verifiable_addresses[0].verified)
// Output: true
```

## 🌐 Raw API (No SDK)

```typescript
// Submit SMS code (raw fetch)
const response = await fetch(
  `http://localhost:4433/self-service/registration?flow=${flowId}`,
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify({
      method: "code",
      code: "123456",
      traits: { phone: "+1234567890" },
      csrf_token: csrfToken
    })
  }
)

const result = await response.json()
```

## ⚡ React Hook

```typescript
import { useState } from 'react'
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.REACT_APP_KRATOS_URL,
    baseOptions: { withCredentials: true }
  })
)

export function useSmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const initFlow = async () => {
    const { data } = await kratos.createBrowserRegistrationFlow()
    setFlow(data)
    return data
  }
  
  const requestCode = async (phoneNumber: string) => {
    setLoading(true)
    try {
      const { data } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          traits: { phone: phoneNumber },
          csrf_token: flow.ui.nodes.find(n => n.attributes.name === "csrf_token")
            ?.attributes.value
        }
      })
      setFlow(data)
      return data
    } finally {
      setLoading(false)
    }
  }
  
  const submitCode = async (phoneNumber: string, code: string) => {
    setLoading(true)
    try {
      const { data } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          code: code,
          traits: { phone: phoneNumber },
          csrf_token: flow.ui.nodes.find(n => n.attributes.name === "csrf_token")
            ?.attributes.value
        }
      })
      return data
    } finally {
      setLoading(false)
    }
  }
  
  return { flow, loading, initFlow, requestCode, submitCode }
}

// Usage in component
function RegisterForm() {
  const { initFlow, requestCode, submitCode } = useSmsRegistration()
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  
  useEffect(() => { initFlow() }, [])
  
  return (
    <>
      <input value={phone} onChange={e => setPhone(e.target.value)} />
      <button onClick={() => requestCode(phone)}>Send Code</button>
      
      <input value={code} onChange={e => setCode(e.target.value)} />
      <button onClick={() => submitCode(phone, code)}>Verify</button>
    </>
  )
}
```

## 🎯 Key Points

1. **SDK Method**: `kratos.updateRegistrationFlow()` or `kratos.updateLoginFlow()`
2. **Request Body**: Include `method: "code"`, `code: "123456"`, `traits/identifier`, and `csrf_token`
3. **Two Calls**: First to request SMS (without code), second to verify (with code)
4. **Same Phone**: Use same phone number in both calls
5. **CSRF Token**: Must include CSRF token from flow

## 🔗 Full Documentation

See [SUBMIT_SMS_CODE_SDK_GUIDE.md](SUBMIT_SMS_CODE_SDK_GUIDE.md) for:
- Complete React/Vue examples
- Error handling
- Resend code functionality
- SMS auto-fill for mobile
- Best practices
