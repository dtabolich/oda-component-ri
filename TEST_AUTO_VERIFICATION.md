# Practical Test: Verifying Auto-Verification in Action

This guide shows you how to test and observe the automatic verification happening with the code method.

## Setup

Use the Docker Compose setup provided:

```bash
docker-compose -f docker-compose.verification-example.yml up -d
```

## Test 1: Watch Database Changes in Real-Time

### Terminal 1: Watch the Database

```bash
# Connect to PostgreSQL
docker exec -it <postgres-container-id> psql -U kratos -d kratos

# Watch verifiable addresses table (updates every 2 seconds)
\watch 2
SELECT 
  va.id,
  va.value as email,
  va.verified,
  va.status,
  va.verified_at,
  i.id as identity_id
FROM identity_verifiable_addresses va
LEFT JOIN identities i ON va.identity_id = i.id
WHERE va.value = 'test@example.com'
ORDER BY va.created_at DESC
LIMIT 1;
```

### Terminal 2: Perform Registration

```bash
# Step 1: Get registration flow
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')
echo "Flow ID: $FLOW_ID"

# Step 2: Submit email (code will be sent)
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {
      "email": "test@example.com",
      "accepted_tos": true
    }
  }' | jq

# Check MailSlurper: http://localhost:4436
# Get the code from the email (e.g., "123456")

# Step 3: Submit the code
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {
      "email": "test@example.com",
      "accepted_tos": true
    }
  }' | jq '.identity.verifiable_addresses'
```

### What You'll See in Terminal 1

**Before code submission:**
```
id | email             | verified | status  | verified_at | identity_id
---+-------------------+----------+---------+-------------+-------------
(0 rows)
```

**After code submission:**
```
id        | email            | verified | status    | verified_at          | identity_id
----------+------------------+----------+-----------+----------------------+-------------
uuid-123  | test@example.com | t        | completed | 2024-11-30 10:05:23  | uuid-456
```

**Notice**: `verified` changed from nothing → `t` (true)!

## Test 2: Inspect the API Response

### Check Verifiable Address in Response

```bash
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {
      "email": "test@example.com",
      "accepted_tos": true
    }
  }' | jq '.identity.verifiable_addresses[] | {value, verified, verified_at, status}'
```

**Output:**
```json
{
  "value": "test@example.com",
  "verified": true,
  "verified_at": "2024-11-30T10:05:23.456789Z",
  "status": "completed"
}
```

### Check Using Admin API

```bash
# Get identity ID from previous response
IDENTITY_ID="<identity-id-from-response>"

# Query via Admin API
curl -s "http://localhost:4434/admin/identities/$IDENTITY_ID" \
  | jq '.verifiable_addresses[] | {value, verified, verified_at, status}'
```

**Output:**
```json
{
  "value": "test@example.com",
  "verified": true,
  "verified_at": "2024-11-30T10:05:23.456789Z",
  "status": "completed"
}
```

## Test 3: Compare with Password Registration

### Register with Password Method

```bash
# Get new flow
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

# Submit password registration
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "password",
    "password": "SecurePassword123!",
    "traits": {
      "email": "password-user@example.com",
      "accepted_tos": true
    }
  }' | jq '.identity.verifiable_addresses[] | {value, verified, verified_at, status}'
```

**Output:**
```json
{
  "value": "password-user@example.com",
  "verified": false,
  "verified_at": null,
  "status": "pending"
}
```

**Notice**: `verified` is `false` with password method!

## Test 4: Watch Kratos Logs

### Enable Debug Logging

Add to your `kratos-verification-example.yml`:

```yaml
log:
  level: debug
  format: text
  leak_sensitive_values: true  # ONLY FOR DEV!
```

### Watch Logs During Registration

```bash
# Terminal 1: Watch logs
docker-compose -f docker-compose.verification-example.yml logs -f kratos

# Terminal 2: Perform registration
# (use commands from Test 1)
```

### Log Output You'll See

```log
time=2024-11-30T10:00:00Z level=info msg="Registration flow created" 
  flow_id=abc123-flow-uuid

time=2024-11-30T10:00:05Z level=info msg="Creating registration code" 
  address=test@example.com 
  code=123456 
  expires_in=15m

time=2024-11-30T10:00:05Z level=debug msg="Sending registration email" 
  to=test@example.com 
  via=email

time=2024-11-30T10:05:20Z level=info msg="Registration code submission received" 
  flow_id=abc123-flow-uuid

time=2024-11-30T10:05:20Z level=debug msg="Validating registration code"

time=2024-11-30T10:05:20Z level=debug msg="Code validation successful" 
  code=123456

time=2024-11-30T10:05:20Z level=info msg="Verifying address" 
  address=test@example.com 
  via=email

time=2024-11-30T10:05:20Z level=debug msg="Setting address verification" 
  verified=true 
  verified_at=2024-11-30T10:05:20.123456Z 
  status=completed

time=2024-11-30T10:05:20Z level=info msg="Address verified successfully"

time=2024-11-30T10:05:21Z level=info msg="Creating identity with verified address"

time=2024-11-30T10:05:21Z level=info msg="Identity created successfully" 
  identity_id=identity-uuid

time=2024-11-30T10:05:21Z level=info msg="Executing post-registration hooks"

time=2024-11-30T10:05:21Z level=info msg="Registration completed successfully"
```

**Key lines:**
- `"Verifying address"` - The verification function is called
- `"Setting address verification verified=true"` - This is the magic moment!
- `"Address verified successfully"` - Confirmation

## Test 5: SQL Queries to Understand the Data

### Query 1: See All Verifiable Addresses

```sql
SELECT 
  va.id,
  i.traits->>'email' as email_from_traits,
  va.value as email_from_address,
  va.verified,
  va.status,
  va.verified_at,
  va.via,
  va.created_at
FROM identity_verifiable_addresses va
JOIN identities i ON va.identity_id = i.id
ORDER BY va.created_at DESC
LIMIT 10;
```

### Query 2: Compare Code vs Password Registrations

```sql
-- Code method registrations (verified automatically)
SELECT 
  i.id,
  i.traits->>'email' as email,
  va.verified,
  'code' as method
FROM identities i
JOIN identity_verifiable_addresses va ON va.identity_id = i.id
JOIN identity_credentials ic ON ic.identity_id = i.id
WHERE ic.identity_credential_type_id = 'code'
  AND va.verified = true;

-- Password method registrations (not auto-verified)
SELECT 
  i.id,
  i.traits->>'email' as email,
  va.verified,
  'password' as method
FROM identities i
JOIN identity_verifiable_addresses va ON va.identity_id = i.id
JOIN identity_credentials ic ON ic.identity_id = i.id
WHERE ic.identity_credential_type_id = 'password'
  AND va.verified = false;
```

### Query 3: Verification Timeline

```sql
SELECT 
  i.id as identity_id,
  i.traits->>'email' as email,
  i.created_at as identity_created,
  va.verified_at as address_verified_at,
  EXTRACT(EPOCH FROM (va.verified_at - i.created_at)) as seconds_to_verify
FROM identities i
JOIN identity_verifiable_addresses va ON va.identity_id = i.id
WHERE va.verified = true
ORDER BY i.created_at DESC
LIMIT 10;
```

**For code method:**
```
identity_id | email            | identity_created      | address_verified_at   | seconds_to_verify
------------+------------------+-----------------------+-----------------------+-------------------
uuid-1      | test@example.com | 2024-11-30 10:05:21  | 2024-11-30 10:05:21  | 0.123
```

**Notice**: `seconds_to_verify` is near 0 - verification happens at the same time as identity creation!

### Query 4: Used Registration Codes

```sql
SELECT 
  address,
  created_at,
  expires_at,
  used_at,
  CASE 
    WHEN used_at IS NOT NULL THEN 'Used'
    WHEN expires_at < NOW() THEN 'Expired'
    ELSE 'Active'
  END as status
FROM identity_registration_codes
WHERE address = 'test@example.com'
ORDER BY created_at DESC;
```

## Test 6: Test Invalid Code (Verification Doesn't Happen)

### Submit Wrong Code

```bash
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

# Submit email
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {"email": "test2@example.com", "accepted_tos": true}
  }' | jq

# Submit WRONG code
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "000000",
    "traits": {"email": "test2@example.com", "accepted_tos": true}
  }' | jq
```

**Response:**
```json
{
  "error": {
    "id": "...",
    "code": 400,
    "message": "The code is invalid or expired"
  }
}
```

**Check database:**
```sql
SELECT * FROM identities WHERE traits->>'email' = 'test2@example.com';
-- Result: (0 rows) - Identity NOT created because code was wrong
```

**Key point**: Verification and identity creation only happen if code is correct!

## Test 7: Code Expiration

### Test Expired Code

```bash
# Get flow
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

# Submit email
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {"email": "test3@example.com", "accepted_tos": true}
  }' | jq

# Wait 16 minutes (or modify config to shorter expiry)

# Try to submit code after expiry
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {"email": "test3@example.com", "accepted_tos": true}
  }' | jq
```

**Response:**
```json
{
  "error": {
    "id": "...",
    "code": 400,
    "message": "The registration flow expired. Please restart."
  }
}
```

**Verification doesn't happen** with expired codes!

## Test 8: One-Time Use

### Try to Use Same Code Twice

```bash
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

# Submit email
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {"email": "test4@example.com", "accepted_tos": true}
  }' | jq

# Get code from MailSlurper: http://localhost:4436
CODE="123456"

# First submission - SUCCESS
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"method\": \"code\",
    \"code\": \"$CODE\",
    \"traits\": {\"email\": \"test4@example.com\", \"accepted_tos\": true}
  }" | jq '.identity.verifiable_addresses[0].verified'
# Output: true

# Try to use same code again with new flow
FLOW_ID2=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')

curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID2" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {"email": "test5@example.com", "accepted_tos": true}
  }' | jq

# Try same code
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID2" \
  -H "Content-Type: application/json" \
  -d "{
    \"method\": \"code\",
    \"code\": \"$CODE\",
    \"traits\": {\"email\": \"test5@example.com\", \"accepted_tos\": true}
  }" | jq
```

**Response:**
```json
{
  "error": {
    "code": 400,
    "message": "The code is invalid or expired"
  }
}
```

**Each code can only be used once!**

## Test 9: Verification Persists in Database

### Verify Data Persists After Restart

```bash
# Register a user
# (use commands from Test 1)

# Stop Kratos
docker-compose -f docker-compose.verification-example.yml stop kratos

# Start Kratos again
docker-compose -f docker-compose.verification-example.yml start kratos

# Check identity still verified
curl -s "http://localhost:4434/admin/identities/$IDENTITY_ID" \
  | jq '.verifiable_addresses[0].verified'
# Output: true
```

**Verification is permanently stored in database!**

## Test 10: Full Proof with Timestamps

### Complete Test with Timing

```bash
# Start timer
START_TIME=$(date +%s)

# Get flow
FLOW_ID=$(curl -s http://localhost:4433/self-service/registration/api | jq -r '.id')
echo "Flow created at: $(date)"

# Submit email
curl -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "traits": {"email": "timing-test@example.com", "accepted_tos": true}
  }' | jq -r '.state'
echo "Code sent at: $(date)"

# Get code from MailSlurper
# (Let's say it's 123456)

# Submit code
RESPONSE=$(curl -s -X POST "http://localhost:4433/self-service/registration?flow=$FLOW_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "code",
    "code": "123456",
    "traits": {"email": "timing-test@example.com", "accepted_tos": true}
  }')

echo "Code submitted at: $(date)"
echo ""
echo "Verification status:"
echo "$RESPONSE" | jq '.identity.verifiable_addresses[0] | {
  email: .value,
  verified: .verified,
  verified_at: .verified_at,
  status: .status
}'

IDENTITY_ID=$(echo "$RESPONSE" | jq -r '.identity.id')

# Check in database
docker exec -it <postgres-container> psql -U kratos -d kratos -c "
  SELECT 
    i.created_at as identity_created,
    va.verified_at as address_verified,
    va.verified,
    EXTRACT(EPOCH FROM (va.verified_at - i.created_at)) * 1000 as ms_difference
  FROM identities i
  JOIN identity_verifiable_addresses va ON va.identity_id = i.id
  WHERE i.id = '$IDENTITY_ID';
"
```

**Output:**
```
Flow created at: Wed Nov 30 10:00:00 UTC 2024
Code sent at: Wed Nov 30 10:00:02 UTC 2024
Code submitted at: Wed Nov 30 10:05:23 UTC 2024

Verification status:
{
  "email": "timing-test@example.com",
  "verified": true,
  "verified_at": "2024-11-30T10:05:23.456789Z",
  "status": "completed"
}

Database query result:
identity_created          | address_verified          | verified | ms_difference
--------------------------+---------------------------+----------+---------------
2024-11-30 10:05:23.456  | 2024-11-30 10:05:23.456  | t        | 0.123
```

**Proof**: `ms_difference` is near 0, showing verification happens **instantly** when code is submitted!

## Summary

These tests demonstrate:

1. ✅ **Verification happens automatically** when correct code is submitted
2. ✅ **Database is updated** with `verified=true`, `verified_at`, and `status=completed`
3. ✅ **Happens instantly** (milliseconds difference between identity creation and verification)
4. ✅ **Only with correct code** - wrong codes don't verify
5. ✅ **Time-limited** - expired codes don't verify
6. ✅ **One-time use** - used codes can't be reused
7. ✅ **Permanent** - verification persists in database
8. ✅ **Different from password** - password method doesn't auto-verify

The code method's automatic verification is **real, observable, and cryptographically secure**.
