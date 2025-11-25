#!/bin/bash

# NetBird Exit Node Setup Script for Azure VM
# This script configures an Azure VM to act as a NetBird exit node

echo "======================================"
echo "NetBird Exit Node Setup"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run this script as root or with sudo${NC}"
    exit 1
fi

# Detect the main network interface (not lo or wt*)
MAIN_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
NETBIRD_INTERFACE=$(ip link show | grep -o 'wt[0-9]*' | head -n1)

echo "Detected interfaces:"
echo "  Main interface: $MAIN_INTERFACE"
echo "  NetBird interface: $NETBIRD_INTERFACE"
echo ""

if [ -z "$MAIN_INTERFACE" ]; then
    echo -e "${RED}Error: Could not detect main network interface${NC}"
    exit 1
fi

if [ -z "$NETBIRD_INTERFACE" ]; then
    echo -e "${YELLOW}Warning: NetBird interface not found. Is NetBird running?${NC}"
    echo "Continuing with setup anyway..."
    NETBIRD_INTERFACE="wt0"
fi

# 1. Enable IP forwarding
echo "Step 1: Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1

# Make it persistent
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi

if ! grep -q "net.ipv6.conf.all.forwarding=1" /etc/sysctl.conf; then
    echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
fi

echo -e "${GREEN}✓${NC} IP forwarding enabled and persisted"
echo ""

# 2. Configure iptables NAT
echo "Step 2: Configuring NAT with iptables..."

# Remove any existing rules to avoid duplicates
iptables -t nat -D POSTROUTING -o $MAIN_INTERFACE -j MASQUERADE 2>/dev/null
iptables -t nat -D POSTROUTING -s 100.64.0.0/10 -o $MAIN_INTERFACE -j MASQUERADE 2>/dev/null

# Add NAT rule for traffic going out the main interface
iptables -t nat -A POSTROUTING -o $MAIN_INTERFACE -j MASQUERADE

# NetBird typically uses 100.64.0.0/10 range (CGNAT range)
iptables -t nat -A POSTROUTING -s 100.64.0.0/10 -o $MAIN_INTERFACE -j MASQUERADE

echo -e "${GREEN}✓${NC} NAT rules configured"
echo ""

# 3. Configure FORWARD chain
echo "Step 3: Configuring FORWARD chain..."

# Accept forwarding for established connections
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
    iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Accept forwarding from NetBird interface
iptables -A FORWARD -i $NETBIRD_INTERFACE -j ACCEPT 2>/dev/null || true

# Accept forwarding to NetBird interface
iptables -A FORWARD -o $NETBIRD_INTERFACE -j ACCEPT 2>/dev/null || true

echo -e "${GREEN}✓${NC} FORWARD rules configured"
echo ""

# 4. Make iptables rules persistent
echo "Step 4: Making iptables rules persistent..."

# Check if iptables-persistent is installed
if ! command -v iptables-save &> /dev/null; then
    echo "Installing iptables-persistent..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y iptables-persistent
fi

# Save current rules
if command -v netfilter-persistent &> /dev/null; then
    netfilter-persistent save
    echo -e "${GREEN}✓${NC} iptables rules saved with netfilter-persistent"
elif [ -d /etc/iptables ]; then
    iptables-save > /etc/iptables/rules.v4
    ip6tables-save > /etc/iptables/rules.v6
    echo -e "${GREEN}✓${NC} iptables rules saved to /etc/iptables/"
else
    mkdir -p /etc/iptables
    iptables-save > /etc/iptables/rules.v4
    ip6tables-save > /etc/iptables/rules.v6
    echo -e "${GREEN}✓${NC} iptables rules saved to /etc/iptables/"
fi
echo ""

# 5. Disable UFW if it's active (can interfere)
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo -e "${YELLOW}Warning: UFW is active and may interfere with exit node${NC}"
        echo "Consider disabling UFW or configuring it properly"
        echo "To disable: sudo ufw disable"
    fi
fi

# 6. Check Azure configuration
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo -e "${GREEN}✓${NC} IP forwarding enabled"
echo -e "${GREEN}✓${NC} NAT rules configured"
echo -e "${GREEN}✓${NC} FORWARD rules configured"
echo -e "${GREEN}✓${NC} Rules persisted"
echo ""
echo -e "${YELLOW}CRITICAL: Azure Configuration Required${NC}"
echo ""
echo "You MUST enable IP forwarding in Azure Portal:"
echo "  1. Go to Azure Portal"
echo "  2. Navigate to your VM"
echo "  3. Go to: Networking → Network Interface (click the link)"
echo "  4. Go to: IP configurations → Enable 'IP forwarding'"
echo "  5. Click 'Save'"
echo ""
echo "Without this Azure setting, the exit node will NOT work!"
echo ""
echo "Additional Azure checklist:"
echo "  ✓ Ensure NSG allows outbound traffic"
echo "  ✓ Check if subnet has custom route tables"
echo "  ✓ Verify VM has a public IP (if needed)"
echo ""
echo "======================================"
echo "NetBird Configuration"
echo "======================================"
echo ""
echo "In NetBird Admin Panel or CLI:"
echo "  1. Mark this peer as an exit node"
echo "  2. On client devices (phone), enable this exit node"
echo "  3. Verify routing domains are configured"
echo ""
echo "To verify setup, run:"
echo "  sudo ./netbird-exit-node-troubleshoot.sh"
echo ""
