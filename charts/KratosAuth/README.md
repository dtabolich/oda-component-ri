# Kratos Auth - Passwordless Phone Authentication

This Helm chart deploys Ory Kratos 25.0.4 with a complete passwordless phone authentication system using browser-based flows.

## Features

- ✅ **Passwordless Authentication**: Users can log in using only their phone number
- ✅ **Browser-based Flows**: Full support for browser-based login and registration
- ✅ **Automatic Registration**: If identity doesn't exist during login, automatically redirect to registration
- ✅ **Phone Verification**: SMS verification step after registration
- ✅ **Modern UI**: Beautiful, responsive authentication pages
- ✅ **Multiple SMS Providers**: Support for Twilio, AWS SNS, Vonage, or mock provider
- ✅ **Production Ready**: Includes PostgreSQL for persistence and proper security configurations

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│   Browser   │────────▶│  UI Service │────────▶│   Kratos    │
│             │         │  (Express)  │         │  (Public)   │
└─────────────┘         └─────────────┘         └──────┬──────┘
                                                       │
                                                       │
                                                ┌──────▼──────┐
                                                │   SMS       │
                                                │  Service    │
                                                └──────┬──────┘
                                                       │
                                                ┌──────▼──────┐
                                                │  Twilio /   │
                                                │  AWS SNS /  │
                                                │  Vonage     │
                                                └─────────────┘
```

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PostgreSQL (included or external)
- SMS provider account (optional, uses mock by default)

## Installation

### Quick Start (Development)

```bash
# Add the Helm repository
helm repo add oda-components https://tmforum-oda.github.io/reference-example-components
helm repo update

# Install with default values (uses mock SMS provider)
helm install kratos-auth oda-components/kratos-auth -n auth --create-namespace
```

### Production Installation

1. **Create a values file** (`production-values.yaml`):

```yaml
global:
  environment: production

kratos:
  database:
    type: postgres
    host: your-postgres-host
    port: 5432
    database: kratos
    user: kratos
    password: "YOUR_SECURE_PASSWORD"

  secrets:
    cookie:
      - "YOUR_32_CHARACTER_COOKIE_SECRET_HERE"
    cipher:
      - "YOUR_32_CHARACTER_CIPHER_SECRET_HERE"

  baseUrls:
    public: "https://api.yourdomain.com/auth"
    admin: "http://kratos-admin.auth.svc.cluster.local:4434"
    ui: "https://yourdomain.com"

  cors:
    allowedOrigins:
      - "https://yourdomain.com"

smsService:
  provider: "twilio"  # or "aws-sns" or "vonage"
  
  twilio:
    accountSid: "YOUR_TWILIO_ACCOUNT_SID"
    authToken: "YOUR_TWILIO_AUTH_TOKEN"
    phoneNumber: "+1234567890"

uiService:
  sessionSecret: "YOUR_SECURE_SESSION_SECRET_HERE"
  
  ingress:
    enabled: true
    className: "nginx"
    hosts:
      - host: yourdomain.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: yourdomain-tls
        hosts:
          - yourdomain.com

postgresql:
  enabled: true
  auth:
    password: "YOUR_POSTGRES_PASSWORD"
```

2. **Install the chart**:

```bash
helm install kratos-auth oda-components/kratos-auth \
  -f production-values.yaml \
  -n auth \
  --create-namespace
```

## Configuration

### SMS Providers

#### Twilio

```yaml
smsService:
  provider: "twilio"
  twilio:
    accountSid: "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    authToken: "your_auth_token"
    phoneNumber: "+1234567890"
```

#### AWS SNS

```yaml
smsService:
  provider: "aws-sns"
  awsSns:
    region: "us-east-1"
    accessKeyId: "AKIAIOSFODNN7EXAMPLE"
    secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

#### Vonage

```yaml
smsService:
  provider: "vonage"
  vonage:
    apiKey: "your_api_key"
    apiSecret: "your_api_secret"
    fromNumber: "YourBrand"
```

### Database

#### Use Included PostgreSQL

```yaml
postgresql:
  enabled: true
  auth:
    username: kratos
    password: changeme
    database: kratos
```

#### Use External PostgreSQL

```yaml
postgresql:
  enabled: false

kratos:
  database:
    type: postgres
    host: external-postgres.example.com
    port: 5432
    database: kratos
    user: kratos
    password: "secure_password"
```

## User Flow

### Login Flow

1. User visits `/login`
2. Enters phone number
3. System sends verification code via SMS
4. User enters code
5. If identity exists and code is valid → Redirect to dashboard
6. If identity doesn't exist → Redirect to registration with pre-filled phone

### Registration Flow

1. User visits `/registration` (or redirected from failed login)
2. Phone number is pre-filled if coming from login
3. User confirms phone number
4. System creates identity
5. Automatically redirects to verification page
6. SMS code is sent
7. User verifies phone
8. Redirect to dashboard

## API Endpoints

### UI Service (Port 3000)

- `GET /` - Home page (redirects to login or dashboard)
- `GET /login` - Login page
- `POST /login` - Submit login
- `GET /registration` - Registration page
- `POST /registration` - Submit registration
- `GET /verification` - Verification page
- `POST /verification` - Submit verification code
- `GET /dashboard` - User dashboard (protected)
- `GET /logout` - Logout

### Kratos Public API (Port 4433)

- `/self-service/login/browser` - Initialize login flow
- `/self-service/registration/browser` - Initialize registration flow
- `/self-service/verification/browser` - Initialize verification flow
- `/sessions/whoami` - Get current session

### SMS Service (Port 4436)

- `POST /sms/send` - Send SMS (called by Kratos)
- `GET /health` - Health check

## Testing

### Local Development

1. **Start services locally**:

```bash
# Terminal 1: Start Kratos
cd source/KratosAuth/config
docker run --rm -it \
  -p 4433:4433 \
  -p 4434:4434 \
  -v $(pwd):/etc/config/kratos \
  oryd/kratos:v1.0.4 \
  serve all --config /etc/config/kratos/kratos.yml

# Terminal 2: Start SMS Service
cd source/KratosAuth/backend
npm install
npm start

# Terminal 3: Start UI Service
cd source/KratosAuth/ui
npm install
npm start
```

2. **Open browser**: http://localhost:3000

3. **Test the flow**:
   - Try to login with a phone number (e.g., +1234567890)
   - System will redirect to registration
   - Complete registration
   - Check terminal for SMS code
   - Enter code to verify
   - Access dashboard

### Kubernetes Testing

```bash
# Port-forward the UI service
kubectl port-forward -n auth svc/kratos-auth-ui 3000:3000

# In another terminal, port-forward SMS service to see logs
kubectl logs -n auth -l component=sms-service -f

# Open browser
open http://localhost:3000
```

## Monitoring

### Check Service Status

```bash
# Check all pods
kubectl get pods -n auth

# Check Kratos logs
kubectl logs -n auth -l component=kratos -f

# Check SMS service logs (to see verification codes in mock mode)
kubectl logs -n auth -l component=sms-service -f

# Check UI logs
kubectl logs -n auth -l component=ui -f
```

### Health Checks

```bash
# Kratos health
kubectl port-forward -n auth svc/kratos-auth-kratos-admin 4434:4434
curl http://localhost:4434/health/ready

# SMS service health
kubectl port-forward -n auth svc/kratos-auth-sms-service 4436:4436
curl http://localhost:4436/health
```

## Security Considerations

### Production Checklist

- [ ] Change all default secrets (cookie, cipher, session)
- [ ] Use strong passwords for PostgreSQL
- [ ] Enable TLS/HTTPS for all public endpoints
- [ ] Configure proper CORS origins
- [ ] Use a production SMS provider (not mock)
- [ ] Enable database SSL connections
- [ ] Set up proper monitoring and alerting
- [ ] Configure rate limiting
- [ ] Review and adjust session lifespans
- [ ] Enable audit logging

### Secrets Management

Consider using external secret management:

```yaml
# Example with External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: kratos-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: kratos-auth-secrets
  data:
    - secretKey: cookie-secret
      remoteRef:
        key: kratos/cookie-secret
```

## Troubleshooting

### Common Issues

#### 1. SMS Not Received

```bash
# Check SMS service logs
kubectl logs -n auth -l component=sms-service

# Verify SMS provider credentials
kubectl get secret kratos-auth-sms-secrets -n auth -o yaml
```

#### 2. Login Flow Not Working

```bash
# Check Kratos configuration
kubectl get configmap kratos-auth-kratos-config -n auth -o yaml

# Verify Kratos can connect to database
kubectl logs -n auth -l component=kratos | grep -i database
```

#### 3. Verification Code Invalid

- Codes expire after 15 minutes
- Each code can only be used once
- Check that phone number format is correct (E.164)

#### 4. CORS Errors

Update `values.yaml`:

```yaml
kratos:
  cors:
    allowedOrigins:
      - "https://your-frontend-domain.com"
```

## Upgrading

```bash
# Update Helm repository
helm repo update

# Upgrade release
helm upgrade kratos-auth oda-components/kratos-auth \
  -n auth \
  -f your-values.yaml
```

## Uninstallation

```bash
# Uninstall the release
helm uninstall kratos-auth -n auth

# Delete the namespace (optional)
kubectl delete namespace auth
```

## Advanced Configuration

### Custom Identity Schema

To add additional fields to the identity schema, modify the ConfigMap:

```yaml
identity:
  schemas:
    - id: default
      url: file:///etc/config/kratos/identity.schema.json
```

### Session Configuration

```yaml
session:
  lifespan: 24h
  earliest_possible_extend: 1h
  cookie:
    domain: yourdomain.com
    secure: true
    same_site: Lax
```

### Recovery Flow

Enable account recovery:

```yaml
selfservice:
  flows:
    recovery:
      enabled: true
      ui_url: https://yourdomain.com/recovery
      use: code
```

## Support

For issues and questions:

- GitHub Issues: https://github.com/ory/kratos/issues
- Ory Community: https://github.com/ory/kratos/discussions
- Documentation: https://www.ory.sh/docs/kratos

## License

This implementation is based on Ory Kratos, which is licensed under Apache 2.0.
