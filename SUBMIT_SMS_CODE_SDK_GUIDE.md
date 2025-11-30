# How to Submit SMS Verification Code to Kratos - SDK Guide

This guide shows you how to submit a verification code received via SMS to Ory Kratos using the browser API and SDK.

## Overview

When a user receives an SMS code on their device, you need to:
1. Capture the code in your UI
2. Submit it to Kratos using the registration/login/verification flow
3. Handle the response (success or error)

## Table of Contents

- [Using Kratos SDK (TypeScript/JavaScript)](#using-kratos-sdk-typescriptjavascript)
- [Using Raw Browser API (Fetch/Axios)](#using-raw-browser-api-fetchaxios)
- [Complete React Example](#complete-react-example)
- [Complete Vue Example](#complete-vue-example)
- [Error Handling](#error-handling)
- [SMS Auto-Fill (Native Mobile)](#sms-auto-fill-native-mobile)

## Using Kratos SDK (TypeScript/JavaScript)

### Installation

```bash
npm install @ory/client
# or
yarn add @ory/client
```

### Setup SDK

```typescript
import { Configuration, FrontendApi } from "@ory/client"

const kratos = new FrontendApi(
  new Configuration({
    basePath: "http://localhost:4433", // Your Kratos public URL
    baseOptions: {
      withCredentials: true, // Important for session cookies
    },
  })
)
```

### Method 1: Registration Flow with SMS Code

#### Step 1: Initialize Registration Flow

```typescript
import { FrontendApi, UpdateRegistrationFlowBody } from "@ory/client"

async function initializeRegistration() {
  try {
    // Create registration flow
    const { data: flow } = await kratos.createBrowserRegistrationFlow()
    
    return flow
  } catch (error) {
    console.error("Failed to initialize registration:", error)
    throw error
  }
}
```

#### Step 2: Submit Phone Number (Request SMS Code)

```typescript
async function requestSmsCode(flowId: string, phoneNumber: string) {
  try {
    const updateBody: UpdateRegistrationFlowBody = {
      method: "code",
      traits: {
        phone: phoneNumber,  // e.g., "+1234567890"
      },
      csrf_token: getCsrfToken(flow), // Get from flow UI
    }
    
    // This will send SMS code to the phone number
    const { data: updatedFlow } = await kratos.updateRegistrationFlow({
      flow: flowId,
      updateRegistrationFlowBody: updateBody,
    })
    
    // Flow state will be "sent_email" (even for SMS, the state name is generic)
    console.log("SMS sent, flow state:", updatedFlow.state)
    
    return updatedFlow
  } catch (error) {
    console.error("Failed to send SMS code:", error)
    throw error
  }
}
```

#### Step 3: Submit SMS Code (Verify and Complete Registration)

```typescript
async function submitSmsCode(
  flowId: string, 
  phoneNumber: string, 
  code: string
) {
  try {
    const updateBody: UpdateRegistrationFlowBody = {
      method: "code",
      code: code,  // The 6-digit code received via SMS
      traits: {
        phone: phoneNumber,  // Same phone number as before
      },
      csrf_token: getCsrfToken(flow),
    }
    
    // Submit the code for verification
    const { data: result } = await kratos.updateRegistrationFlow({
      flow: flowId,
      updateRegistrationFlowBody: updateBody,
    })
    
    // Success! User is registered and phone is verified
    console.log("Registration complete!")
    console.log("Identity:", result.identity)
    console.log("Session:", result.session)
    
    // Check if phone is verified
    const phoneAddress = result.identity.verifiable_addresses?.find(
      addr => addr.via === "sms"
    )
    console.log("Phone verified:", phoneAddress?.verified) // true
    
    return result
  } catch (error) {
    if (error.response?.status === 400) {
      // Invalid code or flow error
      const flowError = error.response.data
      console.error("Verification failed:", flowError.ui.messages)
    }
    throw error
  }
}
```

### Method 2: Login Flow with SMS Code

#### Step 1: Initialize Login Flow

```typescript
async function initializeLogin() {
  try {
    const { data: flow } = await kratos.createBrowserLoginFlow()
    return flow
  } catch (error) {
    console.error("Failed to initialize login:", error)
    throw error
  }
}
```

#### Step 2: Submit Phone Number (Request SMS Code)

```typescript
async function requestLoginSmsCode(flowId: string, phoneNumber: string) {
  try {
    const updateBody = {
      method: "code",
      identifier: phoneNumber,  // Phone number to login with
      csrf_token: getCsrfToken(flow),
    }
    
    const { data: updatedFlow } = await kratos.updateLoginFlow({
      flow: flowId,
      updateLoginFlowBody: updateBody,
    })
    
    console.log("SMS code sent for login")
    return updatedFlow
  } catch (error) {
    console.error("Failed to send login SMS:", error)
    throw error
  }
}
```

#### Step 3: Submit SMS Code (Complete Login)

```typescript
async function submitLoginSmsCode(
  flowId: string,
  phoneNumber: string,
  code: string
) {
  try {
    const updateBody = {
      method: "code",
      code: code,
      identifier: phoneNumber,  // Same phone number
      csrf_token: getCsrfToken(flow),
    }
    
    const { data: result } = await kratos.updateLoginFlow({
      flow: flowId,
      updateLoginFlowBody: updateBody,
    })
    
    console.log("Login complete!")
    console.log("Session:", result.session)
    
    return result
  } catch (error) {
    console.error("Login failed:", error)
    throw error
  }
}
```

### Method 3: Verification Flow (Manual Phone Verification)

```typescript
async function initializeVerification() {
  const { data: flow } = await kratos.createBrowserVerificationFlow()
  return flow
}

async function requestVerificationSmsCode(flowId: string, phoneNumber: string) {
  const updateBody = {
    method: "code",
    phone: phoneNumber,
    csrf_token: getCsrfToken(flow),
  }
  
  const { data: updatedFlow } = await kratos.updateVerificationFlow({
    flow: flowId,
    updateVerificationFlowBody: updateBody,
  })
  
  return updatedFlow
}

async function submitVerificationSmsCode(flowId: string, code: string) {
  const updateBody = {
    method: "code",
    code: code,
    csrf_token: getCsrfToken(flow),
  }
  
  const { data: result } = await kratos.updateVerificationFlow({
    flow: flowId,
    updateVerificationFlowBody: updateBody,
  })
  
  console.log("Phone verified!")
  return result
}
```

## Using Raw Browser API (Fetch/Axios)

### Registration with SMS Code

```typescript
// Step 1: Initialize flow
const initResponse = await fetch(
  "http://localhost:4433/self-service/registration/browser",
  {
    credentials: "include", // Important for cookies
  }
)
const flow = await initResponse.json()

// Step 2: Request SMS code
const requestCodeResponse = await fetch(
  `http://localhost:4433/self-service/registration?flow=${flow.id}`,
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      method: "code",
      traits: {
        phone: "+1234567890",
      },
      csrf_token: flow.ui.nodes.find(n => n.attributes.name === "csrf_token")
        ?.attributes.value,
    }),
  }
)
const updatedFlow = await requestCodeResponse.json()

// Step 3: Submit SMS code
const submitCodeResponse = await fetch(
  `http://localhost:4433/self-service/registration?flow=${flow.id}`,
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      method: "code",
      code: "123456", // Code from SMS
      traits: {
        phone: "+1234567890",
      },
      csrf_token: updatedFlow.ui.nodes.find(n => n.attributes.name === "csrf_token")
        ?.attributes.value,
    }),
  }
)

if (submitCodeResponse.ok) {
  const result = await submitCodeResponse.json()
  console.log("Registration complete!", result)
} else {
  const error = await submitCodeResponse.json()
  console.error("Code verification failed:", error)
}
```

### Login with SMS Code

```typescript
// Step 1: Initialize login flow
const initResponse = await fetch(
  "http://localhost:4433/self-service/login/browser",
  { credentials: "include" }
)
const flow = await initResponse.json()

// Step 2: Request SMS code
const requestCodeResponse = await fetch(
  `http://localhost:4433/self-service/login?flow=${flow.id}`,
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      method: "code",
      identifier: "+1234567890", // Phone number
      csrf_token: getCsrfToken(flow),
    }),
  }
)

// Step 3: Submit SMS code
const submitCodeResponse = await fetch(
  `http://localhost:4433/self-service/login?flow=${flow.id}`,
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      method: "code",
      code: "123456", // Code from SMS
      identifier: "+1234567890",
      csrf_token: getCsrfToken(flow),
    }),
  }
)

const result = await submitCodeResponse.json()
```

## Complete React Example

### Registration Component

```typescript
import React, { useState, useEffect } from "react"
import { FrontendApi, Configuration } from "@ory/client"

const kratos = new FrontendApi(
  new Configuration({
    basePath: process.env.REACT_APP_KRATOS_PUBLIC_URL,
    baseOptions: {
      withCredentials: true,
    },
  })
)

export function SmsRegistration() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Initialize registration flow
  useEffect(() => {
    kratos.createBrowserRegistrationFlow()
      .then(({ data }) => setFlow(data))
      .catch(err => setError(err.message))
  }, [])

  // Get CSRF token from flow
  const getCsrfToken = () => {
    return flow?.ui.nodes.find(
      node => node.attributes.name === "csrf_token"
    )?.attributes.value
  }

  // Step 1: Submit phone number
  const handleSubmitPhone = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const { data } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          traits: {
            phone: phoneNumber,
          },
          csrf_token: getCsrfToken(),
        },
      })

      setFlow(data)
      setStep("code")
    } catch (err) {
      setError(err.response?.data?.ui?.messages?.[0]?.text || err.message)
    } finally {
      setLoading(false)
    }
  }

  // Step 2: Submit SMS code
  const handleSubmitCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const { data } = await kratos.updateRegistrationFlow({
        flow: flow.id,
        updateRegistrationFlowBody: {
          method: "code",
          code: code,
          traits: {
            phone: phoneNumber,
          },
          csrf_token: getCsrfToken(),
        },
      })

      // Success! User is registered and logged in
      console.log("Registration complete:", data)
      
      // Redirect to dashboard or home
      window.location.href = "/dashboard"
    } catch (err) {
      setError(
        err.response?.data?.ui?.messages?.[0]?.text || 
        "Invalid or expired code"
      )
    } finally {
      setLoading(false)
    }
  }

  if (!flow) {
    return <div>Loading...</div>
  }

  return (
    <div className="registration-container">
      <h2>Register with Phone Number</h2>

      {error && <div className="error">{error}</div>}

      {step === "phone" && (
        <form onSubmit={handleSubmitPhone}>
          <div>
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+1234567890"
              required
            />
            <small>Format: +[country code][number]</small>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send Code"}
          </button>
        </form>
      )}

      {step === "code" && (
        <form onSubmit={handleSubmitCode}>
          <div>
            <p>Enter the 6-digit code sent to {phoneNumber}</p>
            <label htmlFor="code">Verification Code</label>
            <input
              type="text"
              id="code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="123456"
              maxLength={6}
              pattern="\d{6}"
              required
              autoComplete="one-time-code"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Verifying..." : "Verify"}
          </button>

          <button
            type="button"
            onClick={() => setStep("phone")}
            disabled={loading}
          >
            Change Phone Number
          </button>
        </form>
      )}
    </div>
  )
}
```

### Login Component

```typescript
export function SmsLogin() {
  const [flow, setFlow] = useState(null)
  const [step, setStep] = useState<"phone" | "code">("phone")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    kratos.createBrowserLoginFlow()
      .then(({ data }) => setFlow(data))
      .catch(err => setError(err.message))
  }, [])

  const getCsrfToken = () => {
    return flow?.ui.nodes.find(
      node => node.attributes.name === "csrf_token"
    )?.attributes.value
  }

  const handleSubmitPhone = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const { data } = await kratos.updateLoginFlow({
        flow: flow.id,
        updateLoginFlowBody: {
          method: "code",
          identifier: phoneNumber,
          csrf_token: getCsrfToken(),
        },
      })

      setFlow(data)
      setStep("code")
    } catch (err) {
      setError(err.response?.data?.ui?.messages?.[0]?.text || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const { data } = await kratos.updateLoginFlow({
        flow: flow.id,
        updateLoginFlowBody: {
          method: "code",
          code: code,
          identifier: phoneNumber,
          csrf_token: getCsrfToken(),
        },
      })

      console.log("Login complete:", data)
      window.location.href = "/dashboard"
    } catch (err) {
      setError(
        err.response?.data?.ui?.messages?.[0]?.text || 
        "Invalid or expired code"
      )
    } finally {
      setLoading(false)
    }
  }

  // Similar JSX as registration...
}
```

## Complete Vue Example

```vue
<template>
  <div class="sms-registration">
    <h2>Register with Phone Number</h2>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- Step 1: Phone Number -->
    <form v-if="step === 'phone'" @submit.prevent="submitPhone">
      <div>
        <label for="phone">Phone Number</label>
        <input
          v-model="phoneNumber"
          type="tel"
          id="phone"
          placeholder="+1234567890"
          required
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Sending...' : 'Send Code' }}
      </button>
    </form>

    <!-- Step 2: Verification Code -->
    <form v-else-if="step === 'code'" @submit.prevent="submitCode">
      <p>Enter the code sent to {{ phoneNumber }}</p>
      <div>
        <label for="code">Verification Code</label>
        <input
          v-model="code"
          type="text"
          id="code"
          placeholder="123456"
          maxlength="6"
          pattern="\d{6}"
          autocomplete="one-time-code"
          required
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Verifying...' : 'Verify' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FrontendApi, Configuration } from '@ory/client'

const kratos = new FrontendApi(
  new Configuration({
    basePath: import.meta.env.VITE_KRATOS_PUBLIC_URL,
    baseOptions: {
      withCredentials: true,
    },
  })
)

const flow = ref(null)
const step = ref<'phone' | 'code'>('phone')
const phoneNumber = ref('')
const code = ref('')
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
    const { data } = await kratos.createBrowserRegistrationFlow()
    flow.value = data
  } catch (err) {
    error.value = err.message
  }
})

const getCsrfToken = () => {
  return flow.value?.ui.nodes.find(
    node => node.attributes.name === 'csrf_token'
  )?.attributes.value
}

const submitPhone = async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await kratos.updateRegistrationFlow({
      flow: flow.value.id,
      updateRegistrationFlowBody: {
        method: 'code',
        traits: {
          phone: phoneNumber.value,
        },
        csrf_token: getCsrfToken(),
      },
    })

    flow.value = data
    step.value = 'code'
  } catch (err) {
    error.value = err.response?.data?.ui?.messages?.[0]?.text || err.message
  } finally {
    loading.value = false
  }
}

const submitCode = async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await kratos.updateRegistrationFlow({
      flow: flow.value.id,
      updateRegistrationFlowBody: {
        method: 'code',
        code: code.value,
        traits: {
          phone: phoneNumber.value,
        },
        csrf_token: getCsrfToken(),
      },
    })

    console.log('Registration complete:', data)
    window.location.href = '/dashboard'
  } catch (err) {
    error.value = err.response?.data?.ui?.messages?.[0]?.text || 'Invalid code'
  } finally {
    loading.value = false
  }
}
</script>
```

## Error Handling

### Common Error Codes and Messages

```typescript
async function submitCodeWithErrorHandling(flowId: string, code: string, phone: string) {
  try {
    const result = await kratos.updateRegistrationFlow({
      flow: flowId,
      updateRegistrationFlowBody: {
        method: "code",
        code: code,
        traits: { phone },
        csrf_token: getCsrfToken(),
      },
    })
    return { success: true, data: result.data }
  } catch (error) {
    const status = error.response?.status
    const data = error.response?.data

    switch (status) {
      case 400:
        // Invalid code or flow error
        const messages = data?.ui?.messages || []
        const errorMsg = messages[0]?.text || "Invalid code"
        
        if (errorMsg.includes("expired")) {
          return { 
            success: false, 
            error: "Code expired. Please request a new code.",
            code: "CODE_EXPIRED"
          }
        } else if (errorMsg.includes("invalid")) {
          return { 
            success: false, 
            error: "Invalid code. Please try again.",
            code: "CODE_INVALID"
          }
        } else {
          return { 
            success: false, 
            error: errorMsg,
            code: "VALIDATION_ERROR"
          }
        }

      case 410:
        // Flow expired
        return {
          success: false,
          error: "Session expired. Please start over.",
          code: "FLOW_EXPIRED"
        }

      case 422:
        // Too many attempts
        return {
          success: false,
          error: "Too many attempts. Please request a new code.",
          code: "TOO_MANY_ATTEMPTS"
        }

      default:
        return {
          success: false,
          error: "An unexpected error occurred. Please try again.",
          code: "UNKNOWN_ERROR"
        }
    }
  }
}

// Usage
const result = await submitCodeWithErrorHandling(flowId, code, phoneNumber)
if (result.success) {
  console.log("Success!", result.data)
} else {
  console.error(result.error)
  // Handle specific error codes
  if (result.code === "FLOW_EXPIRED") {
    // Restart flow
    window.location.reload()
  } else if (result.code === "CODE_INVALID") {
    // Show error, allow retry
    setErrorMessage(result.error)
  }
}
```

## SMS Auto-Fill (Native Mobile)

### React Native Example

```typescript
import { useEffect } from 'react'
import { Platform } from 'react-native'
import SmsRetriever from 'react-native-sms-retriever'

export function useSmsAutoFill(onCodeReceived: (code: string) => void) {
  useEffect(() => {
    if (Platform.OS === 'android') {
      // Android SMS Retriever API
      const startSmsListener = async () => {
        try {
          const registered = await SmsRetriever.startSmsRetriever()
          if (registered) {
            SmsRetriever.addSmsListener(event => {
              const code = extractCodeFromMessage(event.message)
              if (code) {
                onCodeReceived(code)
                SmsRetriever.removeSmsListener()
              }
            })
          }
        } catch (error) {
          console.error('SMS Retriever error:', error)
        }
      }

      startSmsListener()

      return () => {
        SmsRetriever.removeSmsListener()
      }
    }
  }, [onCodeReceived])
}

function extractCodeFromMessage(message: string): string | null {
  // Extract 6-digit code from SMS
  const match = message.match(/\b\d{6}\b/)
  return match ? match[0] : null
}

// Usage in component
function SmsRegistration() {
  const [code, setCode] = useState('')

  useSmsAutoFill((extractedCode) => {
    setCode(extractedCode)
    // Auto-submit
    submitCode(extractedCode)
  })

  // ...rest of component
}
```

### iOS Example (Swift)

```swift
import UIKit

class SmsViewController: UIViewController, UITextFieldDelegate {
    @IBOutlet weak var codeTextField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Enable one-time code auto-fill
        if #available(iOS 12.0, *) {
            codeTextField.textContentType = .oneTimeCode
        }
        
        codeTextField.delegate = self
    }
    
    func textFieldDidChangeSelection(_ textField: UITextField) {
        if let code = textField.text, code.count == 6 {
            // Auto-submit when 6 digits entered
            submitCode(code)
        }
    }
}
```

## Best Practices

### 1. Code Input UX

```typescript
// Auto-focus on code input
useEffect(() => {
  if (step === 'code' && codeInputRef.current) {
    codeInputRef.current.focus()
  }
}, [step])

// Auto-submit when 6 digits entered
const handleCodeChange = (value: string) => {
  setCode(value)
  if (value.length === 6) {
    submitCode(value)
  }
}

// Digit-by-digit input boxes
function CodeInput({ onComplete }: { onComplete: (code: string) => void }) {
  const [digits, setDigits] = useState(['', '', '', '', '', ''])
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return // Only digits

    const newDigits = [...digits]
    newDigits[index] = value.slice(-1) // Only last character
    setDigits(newDigits)

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }

    // Auto-submit when complete
    if (newDigits.every(d => d) && index === 5) {
      onComplete(newDigits.join(''))
    }
  }

  return (
    <div className="code-input">
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={el => inputRefs.current[index] = el}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digit}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Backspace' && !digit && index > 0) {
              inputRefs.current[index - 1]?.focus()
            }
          }}
        />
      ))}
    </div>
  )
}
```

### 2. Resend Code

```typescript
const [canResend, setCanResend] = useState(false)
const [countdown, setCountdown] = useState(60)

useEffect(() => {
  if (step === 'code') {
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          setCanResend(true)
          clearInterval(timer)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }
}, [step])

const handleResend = async () => {
  setCanResend(false)
  setCountdown(60)
  await requestSmsCode(flow.id, phoneNumber)
}

// In JSX:
<button onClick={handleResend} disabled={!canResend}>
  {canResend ? 'Resend Code' : `Resend in ${countdown}s`}
</button>
```

### 3. Loading States

```typescript
const [submitting, setSubmitting] = useState(false)

const submitCode = async (code: string) => {
  setSubmitting(true)
  try {
    await kratos.updateRegistrationFlow(...)
  } finally {
    setSubmitting(false)
  }
}

// Show spinner
{submitting && <Spinner />}
```

## Summary

### Key SDK Methods

| Flow | SDK Method | Purpose |
|------|------------|---------|
| Registration | `createBrowserRegistrationFlow()` | Initialize |
| Registration | `updateRegistrationFlow()` | Submit phone/code |
| Login | `createBrowserLoginFlow()` | Initialize |
| Login | `updateLoginFlow()` | Submit phone/code |
| Verification | `createBrowserVerificationFlow()` | Initialize |
| Verification | `updateVerificationFlow()` | Submit phone/code |

### Request Body Structure

```typescript
// Step 1: Request code
{
  method: "code",
  traits: { phone: "+1234567890" },  // or identifier for login
  csrf_token: "..."
}

// Step 2: Submit code
{
  method: "code",
  code: "123456",
  traits: { phone: "+1234567890" },  // or identifier for login
  csrf_token: "..."
}
```

### Complete Flow

```
1. Initialize flow (createBrowser[Registration|Login]Flow)
   ↓
2. Submit phone (update[Registration|Login]Flow with phone)
   ↓
3. SMS sent (flow state changes to "sent_email")
   ↓
4. User receives SMS
   ↓
5. Submit code (update[Registration|Login]Flow with code)
   ↓
6. ✅ Success! Phone verified, user registered/logged in
```

For more details, see the [official Ory SDK documentation](https://www.ory.sh/docs/kratos/sdk).
