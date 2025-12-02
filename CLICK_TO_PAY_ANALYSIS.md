# Click to Pay: Protocol Analysis & Product Requirements

**Date:** December 2, 2025  
**Purpose:** Technical analysis and product feature requirements for Click to Pay integration

---

## Executive Summary

Click to Pay is an industry-standard digital checkout solution developed by EMVCo (owned by Visa, Mastercard, American Express, Discover, JCB, and UnionPay) that enables secure, one-click online payments across merchants without requiring separate digital wallets or repeated card entry.

**Key Value Propositions:**
- Guest checkout experience with security of tokenization
- Cross-merchant card recognition (shop once, use everywhere)
- Reduced cart abandonment through streamlined checkout
- PCI DSS compliance through tokenized card data
- Mobile-optimized with biometric authentication support

---

## 1. Protocol Overview

### 1.1 What is Click to Pay?

Click to Pay (formerly known as Secure Remote Commerce or SRC) is:
- **Open Standard**: Specification managed by EMVCo
- **Network Agnostic**: Works across all major card networks
- **Token-Based**: Uses EMV payment tokens, not raw card data
- **Consumer-Centric**: Single enrollment works across all participating merchants
- **Device Independent**: Works on desktop, mobile web, and in-app

### 1.2 Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Consumer Layer                        │
│  - Single enrollment (email/phone + card verification)  │
│  - Biometric authentication (face/fingerprint)          │
│  - Multi-card management                                │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Merchant Integration                    │
│  - SDK/API integration (JavaScript/Native)              │
│  - Brand recognition (Click to Pay button)              │
│  - Checkout flow embedding                              │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              Digital Payment Application (DPA)           │
│  - Card network providers (Visa, Mastercard, etc.)      │
│  - Issuer authentication                                │
│  - Token provisioning & management                      │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Payment Processing                     │
│  - Gateway/processor integration                        │
│  - EMV token to authorization                           │
│  - Fraud detection & risk management                    │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Technical Architecture

**Key Technical Elements:**
- **EMV Payment Tokens**: Network-level tokens that replace PAN
- **Digital Card Artifacts**: Tokenized card representation with limited data
- **Consumer Profile**: Email/phone identifier linked to enrolled cards
- **Device Binding**: Optional device fingerprinting for enhanced security
- **SCA Ready**: Supports Strong Customer Authentication (EU PSD2 compliant)

---

## 2. Card Network Support

### 2.1 Network-Specific Implementations

#### **Visa**
- **Brand Name**: Click to Pay (powered by Visa)
- **Service**: Visa Checkout evolution
- **Token Type**: Visa Token Service (VTS)
- **Launch**: Fully operational since 2019
- **Key Features**:
  - Visa Secure (3DS 2.0) integration
  - Risk-based authentication
  - Account Updater service integration
  - Global availability in 100+ countries

#### **Mastercard**
- **Brand Name**: Click to Pay (powered by Mastercard)
- **Service**: Successor to Masterpass
- **Token Type**: Mastercard Digital Enablement Service (MDES)
- **Launch**: Production since 2019
- **Key Features**:
  - Mastercard Identity Check (3DS 2.0)
  - Token cryptogram generation
  - Automatic Billing Updater
  - EMV 3-D Secure support

#### **American Express**
- **Brand Name**: Click to Pay (American Express)
- **Service**: Amex Express Checkout integration
- **Token Type**: Amex Token Service
- **Launch**: 2020 rollout
- **Key Features**:
  - SafeKey authentication
  - Member benefits integration
  - Closed-loop optimization

#### **Discover**
- **Brand Name**: Click to Pay (Discover)
- **Service**: Native DPA provider
- **Launch**: 2020+
- **Key Features**:
  - ProtectBuy integration
  - Network-level tokenization

### 2.2 Issuer Support

**Major Global Issuers Supporting Click to Pay:**
- JPMorgan Chase
- Bank of America
- Wells Fargo
- Citi
- Capital One
- U.S. Bank
- HSBC
- Barclays
- Santander
- BNP Paribas
- Many regional and community banks

**Note**: Issuer support is growing rapidly. Estimated 70-80% of US credit/debit cards are eligible as of 2025.

---

## 3. Merchant Integration Flow

### 3.1 Integration Models

#### **Model 1: Direct Integration (SDK)**
Merchant embeds Click to Pay JavaScript SDK directly on checkout page.

```javascript
// Pseudocode example
<script src="https://cdn.clicktopay.com/sdk/v1/clicktopay.js"></script>

<script>
  ClickToPay.init({
    merchantId: 'YOUR_MERCHANT_ID',
    environment: 'production',
    dpaTransactionOptions: {
      transactionAmount: {
        total: '99.99',
        currency: 'USD'
      }
    }
  });

  // Check if user has enrolled cards
  ClickToPay.isRecognized().then(function(recognized) {
    if (recognized) {
      // Show Click to Pay button
      showClickToPayButton();
    }
  });

  // Handle Click to Pay checkout
  function handleClickToPay() {
    ClickToPay.checkout().then(function(result) {
      // Receive encrypted payment token
      submitPayment(result.encryptedCard);
    });
  }
</script>
```

#### **Model 2: Payment Gateway Integration**
Merchant's gateway provider (Stripe, Adyen, Braintree, etc.) handles Click to Pay.

**Gateway Partners Supporting Click to Pay:**
- Stripe
- Adyen
- Braintree (PayPal)
- Worldpay
- Global Payments
- Fiserv (First Data)
- Chase Merchant Services
- Cybersource (Visa)

#### **Model 3: E-commerce Platform Integration**
Platform-level integration (Shopify, Magento, WooCommerce).

### 3.2 Typical Merchant Flow

```
1. Page Load
   ├─> SDK initialization
   ├─> Consumer recognition check (via cookie/profile)
   └─> Display appropriate checkout options

2. Consumer Recognition
   ├─> Recognized: Show Click to Pay button with card hints
   └─> Not Recognized: Show "Enroll with Click to Pay" option

3. Click to Pay Button Click
   ├─> Open Click to Pay modal/overlay
   ├─> Display enrolled cards (last 4 digits, brand logo)
   ├─> Consumer selects card
   └─> Authentication challenge (if required)

4. Authentication (Context-Dependent)
   ├─> Low Risk: Auto-approve
   ├─> Medium Risk: Device/email verification
   └─> High Risk: Biometric/OTP via issuer

5. Token Delivery
   ├─> SDK receives EMV payment token + cryptogram
   ├─> Token passed to merchant backend
   └─> Additional shipping/billing data included (if available)

6. Payment Processing
   ├─> Merchant submits token to payment gateway
   ├─> Gateway detokenizes and authorizes with issuer
   └─> Return authorization result to merchant

7. Order Completion
   └─> Merchant fulfills order
```

### 3.3 Consumer Enrollment Flow

```
First-Time User at ANY Merchant:
1. Consumer enters email/phone at checkout
2. Click to Pay checks for existing profile
3. If new:
   ├─> Consumer enters card details
   ├─> Card issuer verifies (may send OTP)
   ├─> Card is tokenized and enrolled
   └─> Profile created with email/phone + cards

4. Subsequent Visits (Same or Different Merchant):
   ├─> Consumer identified by email/phone
   ├─> Enrolled cards available automatically
   └─> Can add additional cards at any time
```

---

## 4. Key Functionality & Features

### 4.1 Consumer Features

| Feature | Description |
|---------|-------------|
| **Universal Profile** | Single enrollment works across all merchants |
| **Multi-Card Wallet** | Store multiple cards from any issuer |
| **Auto-Fill** | Shipping and billing addresses saved |
| **Card Management** | Add, remove, set default cards |
| **Security** | Biometric auth, device binding, fraud monitoring |
| **Guest Checkout** | No separate account creation required |
| **Cross-Device** | Access enrolled cards on any device |

### 4.2 Merchant Benefits

| Benefit | Impact |
|---------|--------|
| **Increased Conversion** | 10-30% reduction in cart abandonment |
| **Faster Checkout** | 30-50% faster than manual card entry |
| **Reduced PCI Scope** | Token-based, no card data on merchant servers |
| **Higher Approval Rates** | Network tokens have higher auth rates |
| **Account Updater Built-In** | Tokens auto-update on card reissue |
| **Mobile Optimized** | Native biometric support |
| **Brand Trust** | Industry-standard security mark |

### 4.3 Security Features

- **EMV Tokenization**: PAN never exposed to merchant
- **Cryptographic Validation**: Each transaction has unique cryptogram
- **Strong Customer Authentication**: 3DS 2.0 integrated
- **Risk-Based Auth**: Frictionless for low-risk transactions
- **Device Binding**: Optional enhanced security
- **Fraud Monitoring**: Network-level fraud detection
- **Data Minimization**: Only necessary data shared with merchant

### 4.4 Data Exchange

**Consumer Data Available to Merchant:**
- Payment token (not PAN)
- Token expiry date
- Card brand
- Card type (credit/debit)
- Last 4 digits
- Consumer name
- Billing address (if consented)
- Shipping address (if consented)
- Email/phone (consumer identifier)

**NOT Available to Merchant:**
- Full card number (PAN)
- CVV
- Any consumer data across merchants (privacy protected)

---

## 5. Product Feature Requirements

### 5.1 Core Integration Requirements

#### **Phase 1: Basic Implementation**

**Must-Have:**
1. **SDK Integration**
   - Embed Click to Pay JavaScript SDK on checkout page
   - Initialize with merchant credentials
   - Handle SDK lifecycle (load, ready, error states)

2. **Consumer Recognition**
   - Implement consumer lookup (email/phone)
   - Display Click to Pay button when consumer recognized
   - Handle non-recognized consumers (show enrollment option)

3. **Payment Token Handling**
   - Receive EMV token from Click to Pay SDK
   - Securely transmit token to backend
   - Submit token to payment gateway for authorization

4. **UI/UX Components**
   - Click to Pay button (per brand guidelines)
   - Card selection modal/interface
   - Loading/processing states
   - Error messaging

5. **Backend Services**
   - Merchant registration with DPA providers
   - API endpoints for token processing
   - Integration with existing payment gateway
   - Transaction logging and reconciliation

#### **Phase 2: Enhanced Features**

**Should-Have:**
6. **Advanced Consumer Experience**
   - Prefill shipping/billing from Click to Pay profile
   - Support for multiple saved shipping addresses
   - Card management UI (add/remove/edit cards)
   - "Remember me" functionality

7. **Authentication Handling**
   - 3DS 2.0 challenge integration
   - Biometric authentication support (mobile)
   - Step-up authentication for high-value transactions
   - Fallback to traditional card entry

8. **Mobile Optimization**
   - Native mobile SDK integration (iOS/Android)
   - In-app Click to Pay support
   - Mobile-specific UI patterns
   - Biometric authentication (Face ID, Touch ID)

9. **Analytics & Reporting**
   - Click to Pay usage metrics
   - Conversion rate tracking
   - Authentication success rates
   - Token approval rates vs. traditional cards

#### **Phase 3: Advanced Capabilities**

**Nice-to-Have:**
10. **Subscription & Recurring Payments**
    - Token storage for recurring charges
    - Automatic token updates on card reissue
    - Subscription management interface

11. **Multi-Currency & Localization**
    - Support for international transactions
    - Localized UI/messaging
    - Regional DPA provider connections

12. **Advanced Fraud Prevention**
    - Device fingerprinting integration
    - Behavioral analytics
    - Risk scoring integration
    - Fraud rule customization

13. **Business Intelligence**
    - A/B testing framework (Click to Pay vs. traditional)
    - Cohort analysis
    - Revenue attribution
    - Customer lifetime value tracking

### 5.2 Technical Requirements

#### **Frontend Requirements**

```javascript
// Required SDK Capabilities
- Initialize SDK with merchant config
- Check consumer recognition status
- Display Click to Pay button (conditional)
- Handle checkout button click
- Process payment token response
- Handle errors and fallbacks
- Support callbacks/promises/async patterns
- Manage consumer session state
```

#### **Backend Requirements**

```
API Endpoints:
1. POST /api/checkout/clicktopay/initiate
   - Validate consumer identifier
   - Create checkout session
   - Return session token

2. POST /api/checkout/clicktopay/process
   - Receive EMV payment token
   - Validate token format
   - Submit to payment gateway
   - Return authorization result

3. GET /api/checkout/clicktopay/status/:sessionId
   - Check transaction status
   - Return order details

4. POST /api/checkout/clicktopay/enroll
   - Handle new consumer enrollment
   - Store consumer profile reference
   - Link to customer account (if applicable)
```

#### **Data Storage Requirements**

```sql
-- Consumer Click to Pay Profiles
Table: clicktopay_profiles
- profile_id (UUID, PK)
- customer_id (FK, nullable) -- Link to your customer DB
- email_hash (hashed, indexed)
- phone_hash (hashed, indexed)
- dpa_provider (enum: visa, mastercard, amex, discover)
- external_profile_id (from DPA)
- enrolled_at (timestamp)
- last_used_at (timestamp)
- status (enum: active, inactive)

-- Transaction Records
Table: clicktopay_transactions
- transaction_id (UUID, PK)
- profile_id (FK)
- order_id (FK)
- payment_token (encrypted)
- card_brand (enum)
- card_last4 (string)
- amount (decimal)
- currency (string)
- auth_method (enum: biometric, otp, risk_based)
- status (enum: pending, authorized, declined, refunded)
- created_at (timestamp)
```

### 5.3 Compliance & Security Requirements

1. **PCI DSS Compliance**
   - No storage of full PAN
   - Secure transmission of tokens (TLS 1.2+)
   - Token encryption at rest
   - Audit logging of payment operations

2. **Data Privacy**
   - GDPR compliance (right to erasure, data portability)
   - CCPA compliance (opt-out mechanisms)
   - Consent management for data sharing
   - Privacy policy updates

3. **Authentication**
   - SCA compliance (PSD2 for EU)
   - Support for 3DS 2.0
   - Risk-based authentication rules
   - Rate limiting on authentication attempts

4. **Monitoring & Incident Response**
   - Real-time fraud monitoring
   - Failed authentication alerts
   - Token compromise detection
   - Incident response playbook

### 5.4 Business Requirements

1. **Merchant Onboarding**
   - Registration with card network DPA providers
   - Merchant agreement and T&Cs
   - Sandbox/test environment access
   - Production credentials provisioning
   - Brand asset usage rights

2. **Financial Considerations**
   - Transaction fees (typically same as card-not-present)
   - Gateway integration costs
   - SDK/API usage fees (usually free)
   - Interchange optimization (tokens may qualify for better rates)

3. **Support & Operations**
   - Customer service training on Click to Pay
   - Troubleshooting documentation
   - Fallback procedures (if Click to Pay unavailable)
   - Dispute/chargeback handling for tokenized transactions

4. **Marketing & Adoption**
   - Consumer education materials
   - A/B testing strategy
   - Conversion optimization
   - Brand awareness campaigns

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Merchant registration with Visa/Mastercard DPA
- [ ] Sandbox environment setup
- [ ] SDK integration on checkout page
- [ ] Basic payment token processing
- [ ] Testing with test cards

### Phase 2: Core Features (Weeks 5-8)
- [ ] Consumer recognition implementation
- [ ] Card selection UI
- [ ] Backend API development
- [ ] Gateway integration
- [ ] Error handling and fallbacks

### Phase 3: Enhancement (Weeks 9-12)
- [ ] Mobile optimization
- [ ] Biometric authentication
- [ ] Address prefill
- [ ] Analytics integration
- [ ] Load testing

### Phase 4: Production Launch (Weeks 13-16)
- [ ] Production credentials
- [ ] Security audit
- [ ] Soft launch (5% traffic)
- [ ] Monitoring and optimization
- [ ] Full rollout

---

## 7. Key Integration Partners & Resources

### DPA Provider Documentation
- **Visa**: https://developer.visa.com/capabilities/clicktopay
- **Mastercard**: https://developer.mastercard.com/click-to-pay
- **American Express**: https://developer.americanexpress.com/
- **EMVCo Specifications**: https://www.emvco.com/emv-technologies/secure-remote-commerce/

### Payment Gateway Partners
- **Stripe**: Stripe.js supports Click to Pay
- **Adyen**: Drop-in component includes Click to Pay
- **Braintree**: SDK integration available
- **Cybersource**: Flex integration supported

### E-commerce Platforms
- **Shopify**: App marketplace integrations
- **Magento**: Extension available
- **WooCommerce**: Plugin development
- **BigCommerce**: Native support (check availability)

---

## 8. Key Performance Indicators

### Success Metrics
| KPI | Target | Measurement |
|-----|--------|-------------|
| Click to Pay Adoption Rate | 15-25% of transactions | % of completed orders via C2P |
| Conversion Rate Lift | +10-20% | vs. traditional checkout |
| Checkout Time Reduction | -30-50% | Time to complete payment |
| Cart Abandonment Reduction | -10-30% | Abandoned cart rate |
| Authentication Success Rate | >95% | Successful authentications |
| Token Authorization Rate | >90% | vs. ~85% traditional |
| Mobile Usage | 40-60% | C2P transactions on mobile |
| Return User Rate | 30-50% | Consumers using C2P 2+ times |

---

## 9. Competitive Landscape

### Click to Pay vs. Alternatives

| Solution | Pros | Cons |
|----------|------|------|
| **Click to Pay** | Universal, no app required, issuer-backed, EMV secure | Newer technology, consumer awareness building |
| **PayPal** | High recognition, buyer protection, established trust | Additional fees, account required, redirect flow |
| **Apple Pay** | Seamless on iOS, biometric, high approval rates | Limited to Apple devices, requires wallet setup |
| **Google Pay** | Android integration, Google account leverage | Limited iOS support, varying merchant support |
| **Amazon Pay** | Amazon trust, existing user base | Redirect flow, limited to Amazon account holders |
| **Shop Pay** | Fast checkout, Shopify ecosystem | Primarily Shopify merchants |

**Click to Pay Differentiation:**
- No separate app or account signup
- Works across all merchants after single enrollment
- Native card network solution (higher trust with issuers)
- Device and platform agnostic

---

## 10. Challenges & Considerations

### Implementation Challenges
1. **Consumer Awareness**: Click to Pay is newer; requires consumer education
2. **Issuer Coverage**: Not all banks/cards enrolled yet (growing rapidly)
3. **Testing Complexity**: Multiple DPA providers, various card types
4. **Browser Compatibility**: Need to support wide range of browsers
5. **Mobile App Integration**: Native SDKs require separate implementation

### Risk Mitigation
- **Fallback Flow**: Always provide traditional card entry option
- **Progressive Enhancement**: Detect and enable Click to Pay when available
- **User Testing**: Validate UX with real consumers before launch
- **Monitoring**: Close monitoring of success rates and errors during rollout
- **Support Documentation**: Comprehensive help content for consumers

---

## 11. Decision Matrix

### Should You Implement Click to Pay?

**Implement If:**
- ✅ Significant online/mobile commerce volume
- ✅ High cart abandonment rates
- ✅ Target audience is US/Europe (high issuer coverage)
- ✅ Mobile-first or mobile-significant traffic
- ✅ Competitive checkout experience is priority
- ✅ Payment gateway already supports it

**Deprioritize If:**
- ❌ Low transaction volumes (<1000/month)
- ❌ Primarily B2B with invoicing
- ❌ Markets with low Click to Pay adoption (check regional data)
- ❌ Already have high conversion rates (>90%)
- ❌ Resource constraints for integration

---

## 12. Next Steps

### Immediate Actions
1. **Assess Current State**
   - Review current checkout flow and metrics
   - Identify cart abandonment rate and causes
   - Check payment gateway compatibility

2. **Vendor Outreach**
   - Contact payment gateway about Click to Pay support
   - Request integration documentation
   - Set up sandbox/test accounts

3. **Business Case**
   - Calculate potential ROI based on conversion lift
   - Estimate implementation costs
   - Get stakeholder buy-in

4. **Technical Planning**
   - Architect integration approach
   - Define data models and API contracts
   - Create technical specification

5. **Pilot Planning**
   - Define pilot scope and success criteria
   - Set up analytics and tracking
   - Create rollout plan

---

## Appendix: Technical Specifications

### EMV Token Structure
```json
{
  "paymentToken": {
    "tokenData": "4111111111111111", // Network token
    "tokenExpirationDate": "1225",
    "cryptogram": "AgAAAAABk+cZZWJBVZdvAAAAAAA=",
    "eci": "05"
  },
  "cardDetails": {
    "cardBrand": "VISA",
    "cardType": "CREDIT",
    "last4": "1111",
    "expiryMonth": "12",
    "expiryYear": "2025"
  },
  "billingAddress": {
    "name": "John Doe",
    "addressLine1": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postalCode": "94105",
    "country": "US"
  }
}
```

### Integration Checklist
- [ ] Obtain merchant/API credentials from DPA providers
- [ ] Implement SDK initialization
- [ ] Build consumer recognition logic
- [ ] Create Click to Pay button UI
- [ ] Develop card selection interface
- [ ] Implement token reception and validation
- [ ] Integrate with payment gateway
- [ ] Add error handling and fallback flows
- [ ] Implement logging and monitoring
- [ ] Test across browsers and devices
- [ ] Conduct security review
- [ ] Prepare customer support documentation
- [ ] Plan gradual rollout strategy

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2025  
**Owner:** Product & Engineering Teams
