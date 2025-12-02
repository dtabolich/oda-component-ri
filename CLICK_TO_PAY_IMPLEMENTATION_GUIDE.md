# Click to Pay - Technical Implementation Guide

**Document Type:** Technical Implementation Guide  
**Audience:** Engineering Team  
**Last Updated:** December 2, 2025

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Frontend Implementation](#2-frontend-implementation)
3. [Backend Implementation](#3-backend-implementation)
4. [Payment Gateway Integration](#4-payment-gateway-integration)
5. [Security Implementation](#5-security-implementation)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment Guide](#7-deployment-guide)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser/Mobile App                       │
├─────────────────────────────────────────────────────────────────┤
│  Checkout Page                                                   │
│  ├── Click to Pay SDK (loaded from DPA)                         │
│  ├── Merchant Integration Code                                  │
│  └── Payment Form (fallback)                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Merchant Backend                            │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway / Load Balancer                                    │
│  ├── /api/clicktopay/init                                       │
│  ├── /api/clicktopay/process                                    │
│  └── /api/clicktopay/webhook                                    │
│                                                                  │
│  Application Servers                                            │
│  ├── Click to Pay Service                                       │
│  ├── Payment Service                                            │
│  ├── Order Service                                              │
│  └── Customer Service                                           │
│                                                                  │
│  Data Layer                                                     │
│  ├── PostgreSQL (transactions, profiles)                       │
│  ├── Redis (session cache)                                     │
│  └── S3 (logs, audit trails)                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTPS/TLS 1.2+
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Payment Gateway (Stripe/Adyen)                │
│  - Receives EMV tokens                                          │
│  - Processes authorization                                      │
│  - Returns transaction result                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              Card Networks & DPA Providers                       │
│  ├── Visa Click to Pay                                          │
│  ├── Mastercard Click to Pay                                    │
│  ├── American Express                                           │
│  └── Discover                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
User Action → Frontend → Backend → Gateway → Card Network → Issuer
                ↓
           Analytics
                ↓
            Monitoring
```

### 1.3 Technology Stack Recommendation

**Frontend:**
- JavaScript SDK: Click to Pay SDK (provided by DPA)
- Framework: React, Vue, or vanilla JS
- State Management: Redux/Context API (if needed)
- HTTP Client: Axios/Fetch

**Backend:**
- Language: Node.js, Python, Java, or Go
- Framework: Express/Fastify (Node), Django/Flask (Python), Spring Boot (Java)
- API: RESTful JSON
- Authentication: JWT tokens

**Data Storage:**
- Transactional DB: PostgreSQL, MySQL
- Cache: Redis, Memcached
- Object Storage: AWS S3, GCS

**Infrastructure:**
- Cloud: AWS, GCP, Azure
- Container: Docker + Kubernetes
- CI/CD: GitHub Actions, GitLab CI, Jenkins
- Monitoring: Datadog, New Relic, Prometheus

---

## 2. Frontend Implementation

### 2.1 SDK Integration

#### Step 1: Load Click to Pay SDK

**HTML/JavaScript:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Checkout</title>
</head>
<body>
    <div id="checkout-container">
        <!-- Traditional payment form -->
        <div id="traditional-checkout">
            <h2>Payment Information</h2>
            <form id="payment-form">
                <!-- Card fields -->
            </form>
        </div>

        <!-- Click to Pay section -->
        <div id="clicktopay-container" style="display: none;">
            <h3>Express Checkout</h3>
            <div id="clicktopay-button"></div>
        </div>
    </div>

    <!-- Load Click to Pay SDK asynchronously -->
    <script>
        (function() {
            var script = document.createElement('script');
            script.src = 'https://cdn.src.mastercard.com/srcsdk/2.1.0/src.min.js';
            script.async = true;
            script.onload = function() {
                console.log('Click to Pay SDK loaded');
                initializeClickToPay();
            };
            script.onerror = function() {
                console.error('Failed to load Click to Pay SDK');
                // Fallback to traditional checkout only
                document.getElementById('traditional-checkout').style.display = 'block';
            };
            document.head.appendChild(script);
        })();
    </script>

    <script src="checkout.js"></script>
</body>
</html>
```

#### Step 2: Initialize Click to Pay

**checkout.js:**
```javascript
// Configuration
const CLICKTOPAY_CONFIG = {
    merchantId: 'YOUR_MERCHANT_ID', // Provided by DPA
    environment: 'production', // or 'sandbox'
    dpaTransactionOptions: {
        transactionAmount: {
            total: '99.99',
            currency: 'USD'
        },
        merchantCountryCode: 'US',
        merchantCategoryCode: '5999', // MCC code
        merchantName: 'Your Store Name'
    },
    dpaLocale: 'en_US'
};

// Initialize Click to Pay
async function initializeClickToPay() {
    try {
        // Initialize SDK
        await SRC.init(CLICKTOPAY_CONFIG);
        console.log('Click to Pay initialized');

        // Check if consumer is recognized
        const isRecognized = await SRC.isRecognized();
        
        if (isRecognized) {
            // Show Click to Pay button
            renderClickToPayButton();
            document.getElementById('clicktopay-container').style.display = 'block';
        } else {
            // Optionally show "Checkout with Click to Pay" as enrollment option
            renderEnrollmentOption();
        }

    } catch (error) {
        console.error('Click to Pay initialization failed:', error);
        // Continue with traditional checkout
        document.getElementById('traditional-checkout').style.display = 'block';
    }
}

// Render Click to Pay button
function renderClickToPayButton() {
    const button = SRC.renderButton({
        container: '#clicktopay-button',
        buttonType: 'pay', // 'pay' or 'checkout'
        onClick: handleClickToPayClick
    });
}

// Handle Click to Pay button click
async function handleClickToPayClick(event) {
    event.preventDefault();
    
    try {
        // Show loading state
        showLoadingState();

        // Get consumer's cards
        const srcProfile = await SRC.getCards();
        
        if (srcProfile.cards && srcProfile.cards.length > 0) {
            // Let user select card (or use default)
            const selectedCard = await selectCard(srcProfile.cards);
            
            // Initiate checkout
            const checkoutResult = await SRC.checkout({
                card: selectedCard,
                windowRef: window
            });

            // Process payment token
            await processPaymentToken(checkoutResult);
            
        } else {
            // No cards enrolled, initiate enrollment
            await enrollNewCard();
        }

    } catch (error) {
        console.error('Click to Pay checkout failed:', error);
        handleCheckoutError(error);
    } finally {
        hideLoadingState();
    }
}

// Process payment token received from Click to Pay
async function processPaymentToken(checkoutResult) {
    const paymentToken = checkoutResult.tokenData;
    
    // Send token to backend for processing
    const response = await fetch('/api/clicktopay/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCsrfToken()
        },
        body: JSON.stringify({
            sessionId: getSessionId(),
            paymentToken: paymentToken,
            billingAddress: checkoutResult.billingAddress,
            shippingAddress: checkoutResult.shippingAddress
        })
    });

    const result = await response.json();

    if (result.status === 'success') {
        // Payment authorized, redirect to confirmation
        window.location.href = `/order/confirmation/${result.orderId}`;
    } else {
        // Payment failed, show error
        showError(result.message);
    }
}

// Card selection UI
async function selectCard(cards) {
    return new Promise((resolve) => {
        // Show modal with card options
        const modal = createCardSelectionModal(cards);
        
        modal.onSelect = (card) => {
            resolve(card);
            modal.close();
        };
        
        modal.show();
    });
}

// Create card selection modal
function createCardSelectionModal(cards) {
    const modal = document.createElement('div');
    modal.className = 'clicktopay-modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>Select a card</h3>
                <button class="close-btn">&times;</button>
            </div>
            <div class="modal-body">
                <div id="card-list"></div>
            </div>
            <div class="modal-footer">
                <button id="add-card-btn">Add new card</button>
            </div>
        </div>
    `;

    const cardList = modal.querySelector('#card-list');
    
    cards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card-item';
        cardElement.innerHTML = `
            <input type="radio" name="card" id="card-${index}" value="${index}" 
                   ${card.isDefault ? 'checked' : ''}>
            <label for="card-${index}">
                <img src="${getCardBrandLogo(card.brand)}" alt="${card.brand}">
                <span class="card-number">•••• ${card.last4}</span>
                <span class="card-expiry">Exp: ${card.expiryMonth}/${card.expiryYear}</span>
            </label>
        `;
        cardList.appendChild(cardElement);

        cardElement.addEventListener('click', () => {
            modal.onSelect(card);
        });
    });

    document.body.appendChild(modal);

    modal.close = () => {
        document.body.removeChild(modal);
    };

    modal.querySelector('.close-btn').addEventListener('click', () => {
        modal.close();
    });

    modal.show = () => {
        modal.style.display = 'block';
    };

    return modal;
}

// Helper functions
function getCardBrandLogo(brand) {
    const logos = {
        'visa': '/images/visa-logo.png',
        'mastercard': '/images/mastercard-logo.png',
        'amex': '/images/amex-logo.png',
        'discover': '/images/discover-logo.png'
    };
    return logos[brand.toLowerCase()] || '/images/card-default.png';
}

function showLoadingState() {
    document.getElementById('clicktopay-button').disabled = true;
    document.getElementById('clicktopay-button').innerHTML = 'Processing...';
}

function hideLoadingState() {
    document.getElementById('clicktopay-button').disabled = false;
    document.getElementById('clicktopay-button').innerHTML = 'Click to Pay';
}

function showError(message) {
    alert(message); // Replace with better UI
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

function getSessionId() {
    return sessionStorage.getItem('checkout_session_id');
}
```

### 2.2 React Implementation Example

**ClickToPayButton.jsx:**
```jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ClickToPayButton = ({ amount, currency, onSuccess, onError }) => {
    const [isSDKLoaded, setIsSDKLoaded] = useState(false);
    const [isRecognized, setIsRecognized] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Load Click to Pay SDK
        const loadSDK = async () => {
            try {
                const script = document.createElement('script');
                script.src = 'https://cdn.src.mastercard.com/srcsdk/2.1.0/src.min.js';
                script.async = true;
                
                script.onload = async () => {
                    await window.SRC.init({
                        merchantId: process.env.REACT_APP_C2P_MERCHANT_ID,
                        environment: process.env.REACT_APP_C2P_ENV,
                        dpaTransactionOptions: {
                            transactionAmount: { total: amount, currency }
                        }
                    });
                    
                    setIsSDKLoaded(true);
                    
                    // Check recognition
                    const recognized = await window.SRC.isRecognized();
                    setIsRecognized(recognized);
                };

                document.head.appendChild(script);
            } catch (error) {
                console.error('SDK load failed:', error);
                onError?.(error);
            }
        };

        loadSDK();
    }, [amount, currency]);

    const handleClick = async () => {
        setIsLoading(true);

        try {
            // Get cards
            const profile = await window.SRC.getCards();
            
            // Checkout
            const checkoutResult = await window.SRC.checkout({
                card: profile.cards[0], // Use default card
                windowRef: window
            });

            // Process payment
            const response = await axios.post('/api/clicktopay/process', {
                paymentToken: checkoutResult.tokenData,
                billingAddress: checkoutResult.billingAddress
            });

            if (response.data.status === 'success') {
                onSuccess?.(response.data);
            } else {
                onError?.(new Error(response.data.message));
            }

        } catch (error) {
            console.error('Payment failed:', error);
            onError?.(error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isSDKLoaded || !isRecognized) {
        return null; // Or show enrollment option
    }

    return (
        <button
            className="clicktopay-btn"
            onClick={handleClick}
            disabled={isLoading}
        >
            {isLoading ? 'Processing...' : 'Click to Pay'}
        </button>
    );
};

export default ClickToPayButton;
```

### 2.3 Mobile Implementation (React Native)

**ClickToPayScreen.js:**
```javascript
import React, { useEffect, useState } from 'react';
import { View, Button, Alert } from 'react-native';
import { ClickToPaySDK } from 'react-native-clicktopay'; // Hypothetical SDK

const ClickToPayScreen = ({ amount, currency, onSuccess }) => {
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        // Initialize SDK
        ClickToPaySDK.initialize({
            merchantId: 'YOUR_MERCHANT_ID',
            environment: 'production'
        }).then(() => {
            setIsReady(true);
        });
    }, []);

    const handlePayment = async () => {
        try {
            // Check biometric availability
            const isBiometricAvailable = await ClickToPaySDK.isBiometricAvailable();
            
            if (isBiometricAvailable) {
                // Use biometric authentication
                const authResult = await ClickToPaySDK.authenticateWithBiometric();
                
                if (authResult.success) {
                    // Process payment
                    const paymentResult = await ClickToPaySDK.processPayment({
                        amount,
                        currency
                    });

                    if (paymentResult.success) {
                        onSuccess(paymentResult);
                    }
                }
            } else {
                // Fallback to OTP or password
                Alert.alert('Biometric not available', 'Use alternative authentication');
            }

        } catch (error) {
            Alert.alert('Payment Failed', error.message);
        }
    };

    if (!isReady) {
        return <View><Text>Loading...</Text></View>;
    }

    return (
        <View>
            <Button title="Pay with Click to Pay" onPress={handlePayment} />
        </View>
    );
};

export default ClickToPayScreen;
```

---

## 3. Backend Implementation

### 3.1 Node.js/Express Implementation

**clickToPayController.js:**
```javascript
const express = require('express');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();

// Database models (using Sequelize or similar)
const { ClickToPayProfile, ClickToPayTransaction } = require('../models');

// Payment gateway client
const PaymentGateway = require('../services/paymentGateway');

/**
 * Initialize Click to Pay session
 * POST /api/clicktopay/init
 */
router.post('/init', async (req, res) => {
    try {
        const { amount, currency, merchantReference, consumerIdentifier } = req.body;

        // Validate input
        if (!amount || !currency || !consumerIdentifier) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        // Create session
        const sessionId = uuidv4();
        const sessionToken = generateSessionToken();

        // Store session in Redis (with 15 min TTL)
        await redis.setex(
            `c2p_session:${sessionId}`,
            900, // 15 minutes
            JSON.stringify({
                amount,
                currency,
                merchantReference,
                consumerIdentifier,
                createdAt: new Date().toISOString()
            })
        );

        // Check if consumer is recognized
        const emailHash = hashIdentifier(consumerIdentifier.email);
        const profile = await ClickToPayProfile.findOne({
            where: { emailHash }
        });

        let availableCards = [];
        if (profile) {
            // Fetch enrolled cards (store references only, not full card data)
            availableCards = await profile.getCards();
        }

        res.json({
            sessionId,
            sessionToken,
            expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
            recognized: !!profile,
            availableCards: availableCards.map(card => ({
                cardId: card.id,
                brand: card.brand,
                last4: card.last4,
                expiryMonth: card.expiryMonth,
                expiryYear: card.expiryYear,
                isDefault: card.isDefault
            }))
        });

    } catch (error) {
        console.error('Init error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

/**
 * Process Click to Pay payment
 * POST /api/clicktopay/process
 */
router.post('/process', async (req, res) => {
    try {
        const { sessionId, paymentToken, billingAddress, authMethod } = req.body;

        // Validate session
        const sessionData = await redis.get(`c2p_session:${sessionId}`);
        if (!sessionData) {
            return res.status(400).json({ error: 'Invalid or expired session' });
        }

        const session = JSON.parse(sessionData);

        // Validate payment token structure
        if (!paymentToken || !paymentToken.tokenData || !paymentToken.cryptogram) {
            return res.status(400).json({ error: 'Invalid payment token' });
        }

        // Create transaction record
        const transaction = await ClickToPayTransaction.create({
            id: uuidv4(),
            sessionId,
            paymentTokenReference: hashToken(paymentToken.tokenData), // Store hash only
            amount: session.amount,
            currency: session.currency,
            cardBrand: paymentToken.cardDetails?.brand,
            cardLastFour: paymentToken.cardDetails?.last4,
            authMethod,
            transactionStatus: 'pending',
            ipAddress: req.ip,
            userAgent: req.headers['user-agent']
        });

        // Process payment via gateway
        const gatewayResult = await PaymentGateway.authorize({
            amount: session.amount,
            currency: session.currency,
            paymentToken: paymentToken.tokenData,
            cryptogram: paymentToken.cryptogram,
            eci: paymentToken.eci,
            billingAddress,
            merchantReference: session.merchantReference
        });

        // Update transaction status
        transaction.transactionStatus = gatewayResult.success ? 'authorized' : 'declined';
        transaction.gatewayTransactionId = gatewayResult.transactionId;
        transaction.gatewayResponse = gatewayResult;
        await transaction.save();

        if (gatewayResult.success) {
            // Create order
            const order = await createOrder({
                amount: session.amount,
                currency: session.currency,
                transactionId: transaction.id,
                billingAddress
            });

            res.json({
                status: 'success',
                transactionId: transaction.id,
                authorizationCode: gatewayResult.authorizationCode,
                orderId: order.id,
                amount: session.amount,
                currency: session.currency,
                timestamp: new Date().toISOString()
            });
        } else {
            res.json({
                status: 'declined',
                message: gatewayResult.message,
                transactionId: transaction.id
            });
        }

    } catch (error) {
        console.error('Process error:', error);
        res.status(500).json({ error: 'Payment processing failed' });
    }
});

/**
 * Get session status
 * GET /api/clicktopay/session/:sessionId
 */
router.get('/session/:sessionId', async (req, res) => {
    try {
        const { sessionId } = req.params;

        const transaction = await ClickToPayTransaction.findOne({
            where: { sessionId }
        });

        if (!transaction) {
            return res.status(404).json({ error: 'Session not found' });
        }

        res.json({
            sessionId,
            status: transaction.transactionStatus,
            transactionId: transaction.id,
            createdAt: transaction.createdAt,
            completedAt: transaction.updatedAt
        });

    } catch (error) {
        console.error('Status error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

/**
 * Webhook endpoint for DPA notifications
 * POST /api/clicktopay/webhook
 */
router.post('/webhook', async (req, res) => {
    try {
        const { eventType, data, signature } = req.body;

        // Verify webhook signature
        if (!verifyWebhookSignature(req.body, signature)) {
            return res.status(401).json({ error: 'Invalid signature' });
        }

        // Handle different event types
        switch (eventType) {
            case 'token.updated':
                await handleTokenUpdate(data);
                break;
            case 'token.revoked':
                await handleTokenRevocation(data);
                break;
            case 'card.added':
                await handleCardAdded(data);
                break;
            default:
                console.log('Unknown event type:', eventType);
        }

        res.json({ received: true });

    } catch (error) {
        console.error('Webhook error:', error);
        res.status(500).json({ error: 'Webhook processing failed' });
    }
});

// Helper functions
function generateSessionToken() {
    return crypto.randomBytes(32).toString('hex');
}

function hashIdentifier(identifier) {
    return crypto.createHash('sha256').update(identifier.toLowerCase()).digest('hex');
}

function hashToken(token) {
    return crypto.createHash('sha256').update(token).digest('hex');
}

function verifyWebhookSignature(payload, signature) {
    const secret = process.env.C2P_WEBHOOK_SECRET;
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(JSON.stringify(payload))
        .digest('hex');
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

async function handleTokenUpdate(data) {
    // Update stored token reference
    await ClickToPayCard.update(
        { 
            expiryMonth: data.newExpiryMonth,
            expiryYear: data.newExpiryYear
        },
        { where: { cardReference: data.oldTokenReference } }
    );
}

async function handleTokenRevocation(data) {
    // Mark token as revoked
    await ClickToPayCard.update(
        { status: 'revoked' },
        { where: { cardReference: data.tokenReference } }
    );
}

async function handleCardAdded(data) {
    // Track new card enrollment
    console.log('New card added:', data);
}

async function createOrder(orderData) {
    // Create order in your system
    // Implementation depends on your order management system
    return { id: uuidv4(), ...orderData };
}

module.exports = router;
```

### 3.2 Python/Django Implementation

**views.py:**
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from .models import ClickToPayProfile, ClickToPayTransaction
from .services import PaymentGatewayService

@require_http_methods(["POST"])
def init_session(request):
    """Initialize Click to Pay session"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency')
        consumer_identifier = data.get('consumerIdentifier', {})

        # Validate input
        if not amount or not currency or not consumer_identifier:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Create session
        session_id = str(uuid.uuid4())
        session_token = generate_session_token()

        # Store in cache (Redis)
        cache.set(
            f'c2p_session:{session_id}',
            {
                'amount': amount,
                'currency': currency,
                'consumer_identifier': consumer_identifier,
                'created_at': datetime.now().isoformat()
            },
            timeout=900  # 15 minutes
        )

        # Check recognition
        email_hash = hash_identifier(consumer_identifier.get('email'))
        profile = ClickToPayProfile.objects.filter(email_hash=email_hash).first()

        available_cards = []
        if profile:
            available_cards = profile.cards.filter(status='active')

        return JsonResponse({
            'sessionId': session_id,
            'sessionToken': session_token,
            'expiresAt': (datetime.now() + timedelta(minutes=15)).isoformat(),
            'recognized': profile is not None,
            'availableCards': [
                {
                    'cardId': str(card.id),
                    'brand': card.brand,
                    'last4': card.last4,
                    'expiryMonth': card.expiry_month,
                    'expiryYear': card.expiry_year,
                    'isDefault': card.is_default
                }
                for card in available_cards
            ]
        })

    except Exception as e:
        logger.error(f'Init error: {e}')
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["POST"])
def process_payment(request):
    """Process Click to Pay payment"""
    try:
        data = json.loads(request.body)
        session_id = data.get('sessionId')
        payment_token = data.get('paymentToken')
        billing_address = data.get('billingAddress')
        auth_method = data.get('authMethod')

        # Validate session
        session_data = cache.get(f'c2p_session:{session_id}')
        if not session_data:
            return JsonResponse({'error': 'Invalid or expired session'}, status=400)

        # Create transaction record
        transaction = ClickToPayTransaction.objects.create(
            id=uuid.uuid4(),
            session_id=session_id,
            payment_token_reference=hash_token(payment_token['tokenData']),
            amount=session_data['amount'],
            currency=session_data['currency'],
            card_brand=payment_token.get('cardDetails', {}).get('brand'),
            card_last_four=payment_token.get('cardDetails', {}).get('last4'),
            auth_method=auth_method,
            transaction_status='pending',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        # Process via gateway
        gateway_service = PaymentGatewayService()
        gateway_result = gateway_service.authorize(
            amount=session_data['amount'],
            currency=session_data['currency'],
            payment_token=payment_token['tokenData'],
            cryptogram=payment_token['cryptogram'],
            eci=payment_token.get('eci'),
            billing_address=billing_address
        )

        # Update transaction
        transaction.transaction_status = 'authorized' if gateway_result['success'] else 'declined'
        transaction.gateway_transaction_id = gateway_result.get('transactionId')
        transaction.gateway_response = gateway_result
        transaction.save()

        if gateway_result['success']:
            # Create order
            order = create_order(session_data, transaction, billing_address)

            return JsonResponse({
                'status': 'success',
                'transactionId': str(transaction.id),
                'authorizationCode': gateway_result.get('authorizationCode'),
                'orderId': str(order.id),
                'amount': session_data['amount'],
                'currency': session_data['currency'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'status': 'declined',
                'message': gateway_result.get('message'),
                'transactionId': str(transaction.id)
            })

    except Exception as e:
        logger.error(f'Process error: {e}')
        return JsonResponse({'error': 'Payment processing failed'}, status=500)


# Helper functions
def generate_session_token():
    return uuid.uuid4().hex

def hash_identifier(identifier):
    return hashlib.sha256(identifier.lower().encode()).hexdigest()

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_order(session_data, transaction, billing_address):
    # Create order logic
    pass
```

---

## 4. Payment Gateway Integration

### 4.1 Stripe Integration

**stripePayment.js:**
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

async function processClickToPayWithStripe(paymentData) {
    try {
        // Create PaymentMethod from Click to Pay token
        const paymentMethod = await stripe.paymentMethods.create({
            type: 'card',
            card: {
                token: paymentData.tokenData, // Stripe handles Click to Pay tokens
                cryptogram: paymentData.cryptogram,
                eci: paymentData.eci
            },
            billing_details: {
                name: paymentData.billingAddress.name,
                address: {
                    line1: paymentData.billingAddress.line1,
                    city: paymentData.billingAddress.city,
                    state: paymentData.billingAddress.state,
                    postal_code: paymentData.billingAddress.postalCode,
                    country: paymentData.billingAddress.country
                }
            }
        });

        // Create PaymentIntent
        const paymentIntent = await stripe.paymentIntents.create({
            amount: Math.round(paymentData.amount * 100), // Amount in cents
            currency: paymentData.currency.toLowerCase(),
            payment_method: paymentMethod.id,
            confirm: true,
            metadata: {
                clickToPay: 'true',
                authMethod: paymentData.authMethod
            }
        });

        return {
            success: paymentIntent.status === 'succeeded',
            transactionId: paymentIntent.id,
            authorizationCode: paymentIntent.charges.data[0]?.authorization_code,
            message: paymentIntent.status
        };

    } catch (error) {
        console.error('Stripe error:', error);
        return {
            success: false,
            message: error.message
        };
    }
}

module.exports = { processClickToPayWithStripe };
```

### 4.2 Adyen Integration

**adyenPayment.js:**
```javascript
const { Client, CheckoutAPI } = require('@adyen/api-library');

const client = new Client({
    apiKey: process.env.ADYEN_API_KEY,
    environment: 'LIVE' // or 'TEST'
});

const checkout = new CheckoutAPI(client);

async function processClickToPayWithAdyen(paymentData) {
    try {
        const response = await checkout.payments({
            amount: {
                currency: paymentData.currency,
                value: Math.round(paymentData.amount * 100) // Amount in minor units
            },
            reference: paymentData.merchantReference,
            merchantAccount: process.env.ADYEN_MERCHANT_ACCOUNT,
            paymentMethod: {
                type: 'scheme',
                networkToken: paymentData.tokenData,
                cryptogram: paymentData.cryptogram,
                eci: paymentData.eci
            },
            billingAddress: {
                street: paymentData.billingAddress.line1,
                houseNumberOrName: '',
                city: paymentData.billingAddress.city,
                stateOrProvince: paymentData.billingAddress.state,
                postalCode: paymentData.billingAddress.postalCode,
                country: paymentData.billingAddress.country
            },
            metadata: {
                clickToPay: 'true',
                authMethod: paymentData.authMethod
            }
        });

        return {
            success: response.resultCode === 'Authorised',
            transactionId: response.pspReference,
            authorizationCode: response.authCode,
            message: response.resultCode
        };

    } catch (error) {
        console.error('Adyen error:', error);
        return {
            success: false,
            message: error.message
        };
    }
}

module.exports = { processClickToPayWithAdyen };
```

---

## 5. Security Implementation

### 5.1 Token Encryption

**encryption.js:**
```javascript
const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const KEY = Buffer.from(process.env.ENCRYPTION_KEY, 'hex'); // 32 bytes

function encryptToken(token) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);
    
    let encrypted = cipher.update(token, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
        encrypted,
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex')
    };
}

function decryptToken(encryptedData) {
    const decipher = crypto.createDecipheriv(
        ALGORITHM,
        KEY,
        Buffer.from(encryptedData.iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
}

module.exports = { encryptToken, decryptToken };
```

### 5.2 Rate Limiting

**rateLimiter.js:**
```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('redis');

const redisClient = redis.createClient({
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT
});

// Rate limit for Click to Pay endpoints
const clickToPayLimiter = rateLimit({
    store: new RedisStore({
        client: redisClient,
        prefix: 'ratelimit:c2p:'
    }),
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Max 100 requests per window per IP
    message: 'Too many requests, please try again later',
    standardHeaders: true,
    legacyHeaders: false
});

// Stricter limit for authentication attempts
const authLimiter = rateLimit({
    store: new RedisStore({
        client: redisClient,
        prefix: 'ratelimit:auth:'
    }),
    windowMs: 15 * 60 * 1000,
    max: 5, // Max 5 auth attempts
    message: 'Too many authentication attempts'
});

module.exports = { clickToPayLimiter, authLimiter };
```

### 5.3 PCI DSS Compliance Checklist

```markdown
# PCI DSS Compliance for Click to Pay

## Requirements Met:
- [x] No storage of full PAN (Primary Account Number)
- [x] Only token references stored
- [x] TLS 1.2+ for all communications
- [x] Token encryption at rest (AES-256)
- [x] Audit logging of all payment operations
- [x] Access controls (RBAC)
- [x] Secure key management
- [x] Regular security assessments

## SAQ (Self-Assessment Questionnaire):
- Type: SAQ A (for merchants using tokenization)
- Reduced scope due to Click to Pay implementation

## Annual Requirements:
- [ ] Security audit
- [ ] Penetration testing
- [ ] Vulnerability scanning
- [ ] Update security policies
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**clickToPayController.test.js:**
```javascript
const request = require('supertest');
const app = require('../app');

describe('Click to Pay API', () => {
    describe('POST /api/clicktopay/init', () => {
        it('should initialize session with valid data', async () => {
            const response = await request(app)
                .post('/api/clicktopay/init')
                .send({
                    amount: 99.99,
                    currency: 'USD',
                    consumerIdentifier: {
                        email: 'test@example.com'
                    }
                });

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('sessionId');
            expect(response.body).toHaveProperty('sessionToken');
        });

        it('should return 400 for missing fields', async () => {
            const response = await request(app)
                .post('/api/clicktopay/init')
                .send({});

            expect(response.status).toBe(400);
        });
    });

    describe('POST /api/clicktopay/process', () => {
        it('should process valid payment token', async () => {
            // Setup test session first
            const initResponse = await request(app)
                .post('/api/clicktopay/init')
                .send({
                    amount: 99.99,
                    currency: 'USD',
                    consumerIdentifier: { email: 'test@example.com' }
                });

            const sessionId = initResponse.body.sessionId;

            const response = await request(app)
                .post('/api/clicktopay/process')
                .send({
                    sessionId,
                    paymentToken: {
                        tokenData: '4111111111111111',
                        cryptogram: 'test_cryptogram',
                        eci: '05'
                    },
                    billingAddress: {
                        name: 'Test User',
                        line1: '123 Test St',
                        city: 'Test City',
                        state: 'CA',
                        postalCode: '12345',
                        country: 'US'
                    },
                    authMethod: 'biometric'
                });

            expect(response.status).toBe(200);
            expect(response.body.status).toBe('success');
        });
    });
});
```

### 6.2 Integration Tests

**paymentGateway.test.js:**
```javascript
const PaymentGateway = require('../services/paymentGateway');

describe('Payment Gateway Integration', () => {
    let gateway;

    beforeAll(() => {
        gateway = new PaymentGateway({
            apiKey: process.env.TEST_API_KEY,
            environment: 'sandbox'
        });
    });

    it('should authorize payment with valid token', async () => {
        const result = await gateway.authorize({
            amount: 10.00,
            currency: 'USD',
            paymentToken: 'test_token_visa',
            cryptogram: 'test_cryptogram',
            eci: '05',
            billingAddress: {
                name: 'Test User',
                line1: '123 Test St',
                city: 'Test City',
                state: 'CA',
                postalCode: '12345',
                country: 'US'
            }
        });

        expect(result.success).toBe(true);
        expect(result.transactionId).toBeDefined();
    });

    it('should decline invalid token', async () => {
        const result = await gateway.authorize({
            amount: 10.00,
            currency: 'USD',
            paymentToken: 'invalid_token',
            cryptogram: 'invalid',
            eci: '00'
        });

        expect(result.success).toBe(false);
    });
});
```

### 6.3 E2E Tests (Playwright)

**clickToPay.spec.js:**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Click to Pay Checkout', () => {
    test('should complete purchase with Click to Pay', async ({ page }) => {
        // Navigate to checkout
        await page.goto('https://example.com/checkout');

        // Wait for Click to Pay button
        await page.waitForSelector('#clicktopay-button');

        // Click button
        await page.click('#clicktopay-button');

        // Select card
        await page.waitForSelector('.card-item');
        await page.click('.card-item:first-child');

        // Biometric simulation (in test environment)
        await page.waitForSelector('.auth-success');

        // Verify success
        await expect(page).toHaveURL(/\/order\/confirmation/);
        await expect(page.locator('.order-success')).toBeVisible();
    });

    test('should fallback to traditional checkout on error', async ({ page }) => {
        // Simulate SDK load failure
        await page.route('**/src.min.js', route => route.abort());

        await page.goto('https://example.com/checkout');

        // Traditional checkout should be visible
        await expect(page.locator('#traditional-checkout')).toBeVisible();
    });
});
```

---

## 7. Deployment Guide

### 7.1 Environment Variables

**.env:**
```bash
# Click to Pay Configuration
C2P_MERCHANT_ID=your_merchant_id
C2P_ENVIRONMENT=production # or sandbox
C2P_WEBHOOK_SECRET=your_webhook_secret

# Payment Gateway
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Encryption
ENCRYPTION_KEY=hex_encoded_32_byte_key

# Monitoring
DATADOG_API_KEY=your_dd_api_key
SENTRY_DSN=your_sentry_dsn
```

### 7.2 Docker Deployment

**Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build if needed
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

# Start application
CMD ["node", "server.js"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/clicktopay
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=clicktopay
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 7.3 Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clicktopay-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: clicktopay-api
  template:
    metadata:
      labels:
        app: clicktopay-api
    spec:
      containers:
      - name: api
        image: your-registry/clicktopay-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: C2P_MERCHANT_ID
          valueFrom:
            secretKeyRef:
              name: clicktopay-secrets
              key: merchant-id
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: clicktopay-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: clicktopay-api
spec:
  selector:
    app: clicktopay-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue: SDK not loading**
```
Symptoms: Click to Pay button never appears
Causes:
- CSP (Content Security Policy) blocking script
- Network error/firewall
- Invalid merchant ID

Solutions:
1. Check browser console for errors
2. Verify CSP allows: https://cdn.src.mastercard.com
3. Test in incognito mode
4. Verify merchant ID is correct
```

**Issue: Consumer not recognized**
```
Symptoms: Button doesn't show even though user enrolled previously
Causes:
- Cookies cleared
- Different email/phone entered
- Cross-domain issue

Solutions:
1. Ask user to re-enter enrollment email
2. Check cookie settings
3. Verify domain matches enrollment domain
```

**Issue: Authentication fails**
```
Symptoms: Payment fails during authentication
Causes:
- Biometric not set up on device
- 3DS challenge timeout
- Issuer declining auth

Solutions:
1. Retry with OTP
2. Fallback to password
3. Contact issuer
```

**Issue: Payment declines**
```
Symptoms: Token valid but authorization fails
Causes:
- Insufficient funds
- Card expired
- Fraud block
- Token cryptogram invalid

Solutions:
1. Verify token structure
2. Check gateway logs
3. Try different card
4. Contact issuer
```

### 8.2 Debugging Tools

**Enable Debug Logging:**
```javascript
// Frontend
window.SRC.setLogLevel('debug');

// Backend
const logger = require('winston');
logger.level = 'debug';
```

**Monitor Network Traffic:**
```bash
# Use Chrome DevTools Network tab
# Filter by: src.mastercard.com OR api.visa.com

# Check for:
# - 200 OK responses
# - Valid JSON payloads
# - No CORS errors
```

**Database Query Logging:**
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- View recent transactions
SELECT * FROM clicktopay_transactions 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

---

## Conclusion

This implementation guide provides a comprehensive foundation for integrating Click to Pay into your platform. Key takeaways:

1. **Start with SDK**: Use official Click to Pay SDKs from DPA providers
2. **Security First**: Never store PANs, always use tokens, encrypt sensitive data
3. **Fallback Always**: Traditional checkout must always be available
4. **Test Thoroughly**: Unit, integration, and E2E tests across browsers/devices
5. **Monitor Closely**: Track success rates, errors, and performance metrics

For questions or issues, consult:
- EMVCo SRC Specification
- DPA Provider documentation (Visa, Mastercard)
- Payment Gateway support
- Your technical account manager

**Next Steps:**
1. Register with DPA providers
2. Set up sandbox environment
3. Implement basic SDK integration
4. Test with test cards
5. Security audit
6. Production deployment

Good luck with your Click to Pay integration!
