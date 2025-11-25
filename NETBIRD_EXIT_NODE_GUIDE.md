# NetBird Exit Node Configuration Guide for Azure VM

## Overview
This guide will help you configure an Azure VM as a NetBird exit node, allowing your mobile phone and other devices to route all their internet traffic through the Azure VM when connected to NetBird.

## Problem
When connecting to NetBird with exit node enabled, internet access is not working from the client device (mobile phone).

## Root Causes
The issue typically stems from one or more of these problems:

1. **Azure IP Forwarding Disabled** (Most Common)
   - Azure VMs have IP forwarding disabled by default at the NIC level
   - This blocks packet forwarding regardless of OS configuration

2. **OS IP Forwarding Disabled**
   - Linux kernel needs IP forwarding enabled

3. **Missing NAT Rules**
   - iptables needs MASQUERADE rules for NAT

4. **Azure NSG Restrictions**
   - Network Security Groups may block traffic

5. **NetBird Configuration**
   - Exit node not properly configured in NetBird

## Complete Setup Guide

### Part 1: Linux VM Configuration

#### Step 1: Run the Setup Script

```bash
# Make the script executable
chmod +x netbird-exit-node-setup.sh

# Run the setup script
sudo ./netbird-exit-node-setup.sh
```

This script will:
- Enable IP forwarding at the OS level
- Configure NAT with iptables MASQUERADE rules
- Configure FORWARD chain rules
- Persist all settings

#### Step 2: Verify Configuration

```bash
# Run the troubleshooting script
chmod +x netbird-exit-node-troubleshoot.sh
sudo ./netbird-exit-node-troubleshoot.sh
```

Review the output for any red ✗ marks and follow the recommendations.

### Part 2: Azure Portal Configuration (CRITICAL)

#### Step 1: Enable IP Forwarding on Azure NIC

**This is the most critical step and the most common reason for exit node failures!**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Virtual Machine
3. Click on **Networking** in the left menu
4. Click on the **Network Interface** name (link in the Overview section)
5. In the Network Interface settings, click **IP configurations**
6. Find the **IP forwarding** toggle and set it to **Enabled**
7. Click **Save** at the top

**Without this setting, your exit node will not work, regardless of other configurations!**

#### Step 2: Verify Network Security Group (NSG)

1. Go to your VM → Networking → Network Security Group
2. Check **Outbound security rules**
3. Ensure there's a rule allowing outbound internet traffic (usually a default rule exists)
4. If not, add a rule:
   - Priority: 100
   - Source: Any
   - Destination: Internet
   - Service: Custom
   - Protocol: Any
   - Action: Allow

#### Step 3: Check Route Tables (if applicable)

1. Go to your VM → Networking
2. Check if a **Route Table** is associated
3. If yes, ensure no routes are blocking internet traffic
4. The default route (0.0.0.0/0) should point to Internet

### Part 3: NetBird Configuration

#### Option A: Using NetBird Web UI

1. Go to NetBird Management Console
2. Navigate to **Peers**
3. Find your Azure VM peer
4. Click on it and enable **Exit Node**
5. Set routing domains (use `0.0.0.0/0` for all traffic)
6. Save the configuration

#### Option B: Using NetBird CLI

On the Azure VM:

```bash
# Check NetBird status
netbird status

# If not connected, connect first
netbird up

# Get the peer ID
netbird status | grep "NetBird IP"
```

Then in the management console or using the API, enable exit node for this peer.

### Part 4: Client Configuration (Mobile Phone)

#### On iOS:

1. Open NetBird app
2. Connect to your network
3. Go to **Settings** → **Exit Node**
4. Select your Azure VM from the list
5. Toggle on **Use Exit Node**

#### On Android:

1. Open NetBird app
2. Connect to your network
3. Tap on **Settings** or the menu
4. Select **Exit Node**
5. Choose your Azure VM
6. Enable it

### Part 5: Testing and Verification

#### On the Azure VM:

```bash
# Check if NetBird is connected
netbird status

# Monitor traffic (in real-time)
sudo tcpdump -i any -n host <your-phone-netbird-ip>

# Check NAT translations
sudo iptables -t nat -L POSTROUTING -v -n

# Verify IP forwarding
sysctl net.ipv4.ip_forward
# Should return: net.ipv4.ip_forward = 1
```

#### On the Mobile Phone:

```bash
# Check your public IP (should be Azure VM's IP)
# Visit: https://ifconfig.me
# Or: https://whatismyipaddress.com

# Test DNS resolution
# Try opening various websites

# Check NetBird connection
# In NetBird app, verify you're connected and exit node is active
```

## Manual Configuration Steps

If you prefer to configure manually instead of using the scripts:

### 1. Enable IP Forwarding

```bash
# Enable temporarily
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Enable permanently
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. Configure NAT with iptables

```bash
# Get your main network interface
MAIN_IFACE=$(ip route | grep default | awk '{print $5}')

# Add NAT rule
sudo iptables -t nat -A POSTROUTING -o $MAIN_IFACE -j MASQUERADE

# Add specific rule for NetBird network (100.64.0.0/10)
sudo iptables -t nat -A POSTROUTING -s 100.64.0.0/10 -o $MAIN_IFACE -j MASQUERADE
```

### 3. Configure FORWARD Chain

```bash
# Get NetBird interface
NETBIRD_IFACE=$(ip link show | grep -o 'wt[0-9]*' | head -n1)

# Allow forwarding for established connections
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow forwarding from/to NetBird interface
sudo iptables -A FORWARD -i $NETBIRD_IFACE -j ACCEPT
sudo iptables -A FORWARD -o $NETBIRD_IFACE -j ACCEPT
```

### 4. Persist iptables Rules

```bash
# Install iptables-persistent
sudo apt-get update
sudo apt-get install -y iptables-persistent

# Save rules
sudo netfilter-persistent save
```

## Troubleshooting Common Issues

### Issue 1: Internet Not Working After Connecting to Exit Node

**Symptoms:** Phone connects to NetBird, exit node is enabled, but no internet access.

**Solutions:**
1. ✓ Verify Azure IP forwarding is enabled (Azure Portal → NIC → IP forwarding)
2. ✓ Check OS IP forwarding: `sysctl net.ipv4.ip_forward`
3. ✓ Verify NAT rules: `sudo iptables -t nat -L POSTROUTING -n`
4. ✓ Check if NetBird interface exists: `ip link show | grep wt`
5. ✓ Run the troubleshooting script: `sudo ./netbird-exit-node-troubleshoot.sh`

### Issue 2: Some Websites Work, Others Don't

**Symptoms:** Can access some websites but not others, or DNS resolution fails.

**Solutions:**
1. Check DNS configuration on the phone
2. Verify NetBird DNS settings
3. Test DNS resolution from Azure VM: `nslookup google.com`
4. Check if MTU issues exist (common with VPNs)
   ```bash
   # Lower MTU on NetBird interface
   sudo ip link set dev wt0 mtu 1400
   ```

### Issue 3: Connection Drops After Some Time

**Symptoms:** Exit node works initially but stops after a few minutes.

**Solutions:**
1. Check for NAT timeout issues
2. Verify Azure NSG rules aren't blocking long-lived connections
3. Check NetBird logs: `journalctl -u netbird -f`
4. Verify VM isn't running out of resources: `top`, `free -h`

### Issue 4: Can Ping but Can't Browse

**Symptoms:** Can ping IPs but websites don't load in browser.

**Solutions:**
1. DNS issue - check DNS configuration
2. MTU issue - reduce MTU as shown above
3. Check if only TCP or UDP is blocked
4. Verify firewall rules aren't interfering

### Issue 5: "No Route to Host" Errors

**Symptoms:** Client shows "no route to host" or similar errors.

**Solutions:**
1. Verify routes on the client device
2. Check NetBird routing configuration
3. Ensure exit node is actually advertising routes
4. Verify NetBird peers can communicate: `ping <other-peer-netbird-ip>`

## Advanced Configuration

### Using Specific Exit Domains

Instead of routing all traffic (0.0.0.0/0), you can route specific domains:

1. In NetBird management, configure routing domains
2. Examples:
   - `*.company.com` - Route only company traffic
   - `10.0.0.0/8` - Route only private network
   - `192.168.1.0/24` - Route specific subnet

### Monitoring Traffic

```bash
# Monitor all traffic on NetBird interface
sudo tcpdump -i wt0 -n

# Monitor specific client
sudo tcpdump -i wt0 -n host 100.64.x.x

# Check connection tracking
sudo conntrack -L

# Monitor bandwidth
sudo iftop -i wt0
```

### Performance Tuning

```bash
# Increase connection tracking table size
sudo sysctl -w net.netfilter.nf_conntrack_max=262144

# Optimize TCP settings
sudo sysctl -w net.ipv4.tcp_fastopen=3
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# Add to /etc/sysctl.conf to persist
```

## Security Considerations

1. **Limit Exit Node Access:** Only allow specific peers to use the exit node
2. **Monitor Usage:** Regularly check logs for unusual activity
3. **Azure NSG:** Keep restrictive inbound rules, allow necessary outbound
4. **Update Regularly:** Keep NetBird and OS updated
5. **Logging:** Enable logging for troubleshooting:
   ```bash
   sudo journalctl -u netbird -f
   ```

## Quick Reference Commands

```bash
# Check NetBird status
netbird status

# Check IP forwarding
sysctl net.ipv4.ip_forward

# View NAT rules
sudo iptables -t nat -L POSTROUTING -v -n

# View FORWARD rules
sudo iptables -L FORWARD -v -n

# View routes
ip route show

# Check NetBird interface
ip addr show wt0

# Restart NetBird
sudo systemctl restart netbird

# View NetBird logs
sudo journalctl -u netbird -n 100

# Test connectivity from VM
ping -c 4 8.8.8.8
curl -I https://google.com
```

## Additional Resources

- [NetBird Documentation](https://netbird.io/docs)
- [NetBird Exit Nodes](https://netbird.io/docs/how-to/routing-traffic-to-private-networks)
- [Azure IP Forwarding](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface#enable-or-disable-ip-forwarding)
- [Linux IP Forwarding](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt)

## Support

If you continue to experience issues after following this guide:

1. Run the troubleshooting script and save the output
2. Check NetBird logs: `sudo journalctl -u netbird -n 200 > netbird.log`
3. Verify Azure configuration in Portal
4. Check NetBird community forums or GitHub issues

## Scripts Included

1. **netbird-exit-node-setup.sh** - Automated setup script
2. **netbird-exit-node-troubleshoot.sh** - Comprehensive troubleshooting script

Both scripts should be run with sudo privileges.
