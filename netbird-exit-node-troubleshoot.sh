#!/bin/bash

# NetBird Exit Node Troubleshooting Script for Azure VM
# This script helps diagnose issues with NetBird exit node configuration

echo "======================================"
echo "NetBird Exit Node Troubleshooting"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_section() {
    echo ""
    echo "======================================"
    echo "$1"
    echo "======================================"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run this script as root or with sudo${NC}"
    exit 1
fi

# 1. Check NetBird service status
print_section "1. NetBird Service Status"
systemctl is-active --quiet netbird
print_status $? "NetBird service is running"

if systemctl is-active --quiet netbird; then
    echo "NetBird status:"
    netbird status 2>/dev/null || echo "Unable to get NetBird status"
fi

# 2. Check IP forwarding
print_section "2. IP Forwarding Configuration"
IPV4_FORWARD=$(sysctl -n net.ipv4.ip_forward 2>/dev/null)
IPV6_FORWARD=$(sysctl -n net.ipv6.conf.all.forwarding 2>/dev/null)

if [ "$IPV4_FORWARD" = "1" ]; then
    print_status 0 "IPv4 forwarding is enabled"
else
    print_status 1 "IPv4 forwarding is DISABLED (needs to be enabled)"
fi

if [ "$IPV6_FORWARD" = "1" ]; then
    print_status 0 "IPv6 forwarding is enabled"
else
    print_warning "IPv6 forwarding is disabled (enable if needed)"
fi

# 3. Check NetBird interface
print_section "3. NetBird Network Interface"
NETBIRD_INTERFACE=$(ip link show | grep -o 'wt[0-9]*' | head -n1)

if [ -n "$NETBIRD_INTERFACE" ]; then
    print_status 0 "NetBird interface found: $NETBIRD_INTERFACE"
    echo ""
    echo "Interface details:"
    ip addr show $NETBIRD_INTERFACE
    echo ""
    NETBIRD_IP=$(ip -4 addr show $NETBIRD_INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    echo "NetBird IP: $NETBIRD_IP"
else
    print_status 1 "NetBird interface (wt*) not found"
fi

# 4. Check NAT/iptables rules
print_section "4. NAT/iptables Configuration"
echo "Checking NAT rules in POSTROUTING chain:"
iptables -t nat -L POSTROUTING -v -n | grep -E "MASQUERADE|SNAT" | head -10

NAT_RULES=$(iptables -t nat -L POSTROUTING -n | grep -c "MASQUERADE\|SNAT")
if [ $NAT_RULES -gt 0 ]; then
    print_status 0 "NAT rules found ($NAT_RULES rules)"
else
    print_status 1 "No NAT rules found (required for exit node)"
fi

echo ""
echo "Checking FORWARD chain rules:"
iptables -L FORWARD -v -n | head -15

# 5. Check default route
print_section "5. Network Routes"
echo "Default route:"
ip route show default

echo ""
echo "NetBird routes:"
ip route show | grep "$NETBIRD_INTERFACE" 2>/dev/null || echo "No NetBird routes found"

# 6. Check DNS
print_section "6. DNS Configuration"
echo "DNS servers in /etc/resolv.conf:"
cat /etc/resolv.conf | grep nameserver

# 7. Check Azure Network Security Group (NSG) note
print_section "7. Azure Configuration Checklist"
print_warning "Azure VM Settings to Verify (cannot be checked from inside VM):"
echo ""
echo "  1. Azure NSG (Network Security Group):"
echo "     - Outbound rule allowing all traffic should exist"
echo "     - Check NSG attached to both VM and subnet"
echo ""
echo "  2. Azure VM Network Interface:"
echo "     - IP forwarding MUST be enabled on the NIC"
echo "     - Go to: VM → Networking → Network Interface → IP configurations"
echo "     - Enable 'IP forwarding'"
echo ""
echo "  3. Azure Route Table (if applicable):"
echo "     - Check if custom routes are interfering"

# 8. Check connectivity
print_section "8. Connectivity Tests"
echo "Testing DNS resolution:"
if nslookup google.com >/dev/null 2>&1; then
    print_status 0 "DNS resolution works"
else
    print_status 1 "DNS resolution failed"
fi

echo ""
echo "Testing external connectivity:"
if ping -c 2 8.8.8.8 >/dev/null 2>&1; then
    print_status 0 "Can ping external IP (8.8.8.8)"
else
    print_status 1 "Cannot ping external IP"
fi

if ping -c 2 google.com >/dev/null 2>&1; then
    print_status 0 "Can ping external domain (google.com)"
else
    print_status 1 "Cannot ping external domain"
fi

# 9. Check for packet drops
print_section "9. Packet Statistics"
echo "Interface statistics (errors/drops):"
ip -s link show $NETBIRD_INTERFACE 2>/dev/null || echo "Cannot get interface statistics"

# 10. Show current iptables rules summary
print_section "10. Complete iptables Rules Summary"
echo "FILTER table:"
iptables -L -v -n --line-numbers | head -30
echo ""
echo "NAT table:"
iptables -t nat -L -v -n --line-numbers | head -30

# Summary
print_section "Summary and Next Steps"
echo ""
echo "Common issues and fixes:"
echo ""
echo "1. If IP forwarding is disabled:"
echo "   Run: sudo sysctl -w net.ipv4.ip_forward=1"
echo "   Persist: echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf"
echo ""
echo "2. If NAT rules are missing:"
echo "   Run the netbird-exit-node-setup.sh script"
echo ""
echo "3. Azure IP forwarding MUST be enabled:"
echo "   - Azure Portal → VM → Networking → Network Interface → IP configurations"
echo "   - Enable 'IP forwarding' toggle"
echo "   - This is CRITICAL and cannot be done from inside the VM"
echo ""
echo "4. Check NetBird exit node configuration:"
echo "   - Ensure the peer is configured as an exit node in NetBird admin"
echo "   - Ensure client peers have the exit node enabled"
echo ""
echo "5. Verify Azure NSG allows outbound traffic"
echo ""
echo "======================================"
echo "Troubleshooting complete!"
echo "======================================"
