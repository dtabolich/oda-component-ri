#!/bin/bash

################################################################################
# Prism Mock Server - Deployment Test Script
# 
# This script validates that your Prism Mock Server deployment is working correctly.
# Usage: ./test-deployment.sh <release-name> [namespace]
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RELEASE_NAME=${1:-my-mock-server}
NAMESPACE=${2:-default}
TIMEOUT=120  # seconds

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Prism Mock Server - Deployment Test                   ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "Release Name: ${GREEN}${RELEASE_NAME}${NC}"
echo -e "Namespace: ${GREEN}${NAMESPACE}${NC}"
echo ""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        return 1
    fi
}

# Function to wait for condition
wait_for() {
    local timeout=$1
    local check_cmd=$2
    local description=$3
    
    echo -ne "${YELLOW}⏳ Waiting for: ${description}${NC}"
    
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if eval "$check_cmd" &>/dev/null; then
            echo -e "\r${GREEN}✓${NC} ${description} (${elapsed}s)"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -ne "\r${YELLOW}⏳ Waiting for: ${description} (${elapsed}/${timeout}s)${NC}"
    done
    
    echo -e "\r${RED}✗${NC} ${description} - Timeout after ${timeout}s"
    return 1
}

# Test 1: Check if Helm release exists
echo ""
echo -e "${BLUE}[Test 1/8]${NC} Checking Helm release..."
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    print_result 0 "Helm release '${RELEASE_NAME}' exists"
else
    print_result 1 "Helm release '${RELEASE_NAME}' not found"
    echo -e "${YELLOW}Hint: Install with: helm install ${RELEASE_NAME} ./PrismMockServer -n ${NAMESPACE}${NC}"
    exit 1
fi

# Test 2: Check if deployment exists
echo ""
echo -e "${BLUE}[Test 2/8]${NC} Checking Kubernetes deployment..."
if kubectl get deployment ${RELEASE_NAME}-prism -n ${NAMESPACE} &>/dev/null; then
    print_result 0 "Deployment exists"
else
    print_result 1 "Deployment not found"
    exit 1
fi

# Test 3: Check if service exists
echo ""
echo -e "${BLUE}[Test 3/8]${NC} Checking Kubernetes service..."
if kubectl get service ${RELEASE_NAME}-prism -n ${NAMESPACE} &>/dev/null; then
    print_result 0 "Service exists"
    SERVICE_TYPE=$(kubectl get svc ${RELEASE_NAME}-prism -n ${NAMESPACE} -o jsonpath='{.spec.type}')
    echo -e "   Service Type: ${GREEN}${SERVICE_TYPE}${NC}"
else
    print_result 1 "Service not found"
    exit 1
fi

# Test 4: Wait for pods to be ready
echo ""
echo -e "${BLUE}[Test 4/8]${NC} Waiting for pods to be ready..."
if wait_for ${TIMEOUT} \
    "kubectl wait --for=condition=ready pod -l app=${RELEASE_NAME}-prism -n ${NAMESPACE} --timeout=0s" \
    "Pod ready"; then
    
    POD_COUNT=$(kubectl get pods -l app=${RELEASE_NAME}-prism -n ${NAMESPACE} --no-headers | wc -l)
    echo -e "   Running pods: ${GREEN}${POD_COUNT}${NC}"
else
    echo -e "${RED}Pods failed to become ready${NC}"
    echo ""
    echo "Pod status:"
    kubectl get pods -l app=${RELEASE_NAME}-prism -n ${NAMESPACE}
    echo ""
    echo "Recent events:"
    kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' | tail -10
    exit 1
fi

# Test 5: Check pod logs for errors
echo ""
echo -e "${BLUE}[Test 5/8]${NC} Checking pod logs..."
POD_NAME=$(kubectl get pods -l app=${RELEASE_NAME}-prism -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
LOGS=$(kubectl logs ${POD_NAME} -n ${NAMESPACE} --tail=20 2>&1)

if echo "$LOGS" | grep -iq "error\|fatal\|exception"; then
    print_result 1 "Found errors in pod logs"
    echo ""
    echo "Recent logs:"
    echo "$LOGS"
else
    print_result 0 "No errors in pod logs"
fi

# Test 6: Check if endpoints exist
echo ""
echo -e "${BLUE}[Test 6/8]${NC} Checking service endpoints..."
ENDPOINTS=$(kubectl get endpoints ${RELEASE_NAME}-prism -n ${NAMESPACE} -o jsonpath='{.subsets[*].addresses[*].ip}')
if [ -n "$ENDPOINTS" ]; then
    print_result 0 "Service has endpoints"
    echo -e "   Endpoints: ${GREEN}${ENDPOINTS}${NC}"
else
    print_result 1 "Service has no endpoints"
    exit 1
fi

# Test 7: Test HTTP connectivity
echo ""
echo -e "${BLUE}[Test 7/8]${NC} Testing HTTP connectivity..."

# Start port-forward in background
echo -e "${YELLOW}Starting port-forward...${NC}"
kubectl port-forward -n ${NAMESPACE} svc/${RELEASE_NAME}-prism 18080:80 >/dev/null 2>&1 &
PF_PID=$!

# Give port-forward time to establish
sleep 3

# Test HTTP request
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:18080/ 2>/dev/null || echo "000")

# Clean up port-forward
kill $PF_PID 2>/dev/null || true

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "404" ]; then
    print_result 0 "HTTP service is responding (HTTP ${HTTP_STATUS})"
else
    print_result 1 "HTTP service not responding (HTTP ${HTTP_STATUS})"
fi

# Test 8: Check resource usage
echo ""
echo -e "${BLUE}[Test 8/8]${NC} Checking resource usage..."
if kubectl top pods -l app=${RELEASE_NAME}-prism -n ${NAMESPACE} &>/dev/null; then
    print_result 0 "Resource metrics available"
    echo ""
    kubectl top pods -l app=${RELEASE_NAME}-prism -n ${NAMESPACE}
else
    echo -e "${YELLOW}⚠ Resource metrics not available (metrics-server may not be installed)${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Test Summary                                           ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${GREEN}✓ All critical tests passed!${NC}"
echo ""
echo -e "${BLUE}Access Information:${NC}"
echo -e "  Internal (from cluster):"
echo -e "    ${GREEN}http://${RELEASE_NAME}-prism.${NAMESPACE}.svc.cluster.local${NC}"
echo ""
echo -e "  External (port-forward):"
echo -e "    ${YELLOW}kubectl port-forward -n ${NAMESPACE} svc/${RELEASE_NAME}-prism 8080:80${NC}"
echo -e "    Then access: ${GREEN}http://localhost:8080${NC}"
echo ""

# Additional info based on service type
if [ "$SERVICE_TYPE" = "NodePort" ]; then
    NODE_PORT=$(kubectl get svc ${RELEASE_NAME}-prism -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}')
    echo -e "  NodePort access:"
    echo -e "    ${GREEN}http://<node-ip>:${NODE_PORT}${NC}"
    echo ""
fi

# Check for Ingress
if kubectl get ingress ${RELEASE_NAME}-prism -n ${NAMESPACE} &>/dev/null; then
    INGRESS_HOST=$(kubectl get ingress ${RELEASE_NAME}-prism -n ${NAMESPACE} -o jsonpath='{.spec.rules[0].host}')
    echo -e "  Ingress access:"
    echo -e "    ${GREEN}http://${INGRESS_HOST}${NC}"
    echo ""
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}Deployment test completed successfully! 🎉${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

exit 0
