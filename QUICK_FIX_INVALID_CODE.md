# Quick Fix: "Code is invalid or already been used"

## 🎯 The Problem

You're probably doing this:

```typescript
// ❌ THIS IS THE BUG
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// Send SMS
await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: { phone: "+1234567890" }
  }
})

// Submit code - using SAME flow variable
await kratos.updateRegistrationFlow({
  flow: flow.id,  // ❌ WRONG - using original flow
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: { phone: "+1234567890" }
  }
})
// Error: "code is invalid or already been used"
```

## ✅ The Fix

Do this instead:

```typescript
// ✅ THIS IS CORRECT
const { data: flow } = await kratos.createBrowserRegistrationFlow()

// Send SMS - SAVE THE RESPONSE
const { data: updatedFlow } = await kratos.updateRegistrationFlow({
  flow: flow.id,
  updateRegistrationFlowBody: {
    method: "code",
    traits: { phone: "+1234567890" }
  }
})

// Submit code - use UPDATED flow
await kratos.updateRegistrationFlow({
  flow: updatedFlow.id,  // ✅ CORRECT - using updated flow
  updateRegistrationFlowBody: {
    method: "code",
    code: "123456",
    traits: { phone: "+1234567890" },
    csrf_token: updatedFlow.ui.nodes.find(n => n.attributes.name === "csrf_token")?.attributes.value
  }
})
```

## 🔑 Key Points

1. **Save the response** from the first `updateRegistrationFlow` call
2. **Use the updated flow** for the second call
3. **Update your state** if using React/Vue

## 📋 Copy-Paste Solution

```typescript
const [flow, setFlow] = useState(null)

// Initialize
useEffect(() => {
  kratos.createBrowserRegistrationFlow()
    .then(({ data }) => setFlow(data))
}, [])

// Request SMS
const requestCode = async () => {
  const { data: updatedFlow } = await kratos.updateRegistrationFlow({
    flow: flow.id,
    updateRegistrationFlowBody: {
      method: "code",
      traits: { phone: phoneNumber },
      csrf_token: getCsrfToken(flow)
    }
  })
  
  // ✅ CRITICAL: Update the flow
  setFlow(updatedFlow)
}

// Submit code
const submitCode = async () => {
  const { data: result } = await kratos.updateRegistrationFlow({
    flow: flow.id,  // Now using the updated flow
    updateRegistrationFlowBody: {
      method: "code",
      code: code,
      traits: { phone: phoneNumber },
      csrf_token: getCsrfToken(flow)
    }
  })
  // Success!
}
```

## 🚀 Test It

Add this debugging to see if it's working:

```typescript
const requestCode = async () => {
  console.log("BEFORE - Flow ID:", flow.id)
  console.log("BEFORE - Flow state:", flow.state)
  
  const { data: updatedFlow } = await kratos.updateRegistrationFlow(...)
  
  console.log("AFTER - Flow ID:", updatedFlow.id)
  console.log("AFTER - Flow state:", updatedFlow.state)
  
  // They should be:
  // - Same ID
  // - State changed from "choose_method" to "sent_email"
  
  setFlow(updatedFlow)
}
```

See [TROUBLESHOOT_INVALID_CODE_ERROR.md](TROUBLESHOOT_INVALID_CODE_ERROR.md) for full details.
