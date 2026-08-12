# 🚀 NineRouter Autoproxy - Complete All-in-One Guide

This is a **single Python file** that handles everything: setup, configuration, diagnostics, and running the proxy.

---

## 📥 Quick Start (2 minutes)

### 1. Download & Make Executable

```bash
# Download or copy nine_router_proxy.py to your Mac
chmod +x nine_router_proxy.py
```

### 1.1 Run Installer Script

Run this from the repository root directory on Linux/macOS:

```bash
chmod +x install.sh
./install.sh
```

On any platform with Python installed, you can also use the cross-platform installer:

```bash
python3 install.py
```

On Windows, run:

```cmd
install.bat
```

All installers perform the same steps:

- install runtime dependencies
- copy `nine_router_proxy.py` to the install directory
- create the launcher command `9router-proxy`
- attempt to detect 9Router and warn if it is not found

If you are not in the project folder yet, first clone the repo and `cd` into it:

```bash
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
chmod +x install.sh
./install.sh
```

This installer installs dependencies, configures the script, and creates a launcher command named `9router-proxy`.

It also attempts to detect 9Router and warns if it is not found.

Repository files:

- `install.sh`: Linux/macOS install script
- `install.py`: Cross-platform Python installer
- `install.bat`: Windows wrapper installer
- `nine_router_proxy.py`: Proxy runtime and setup script
- `9router-proxy`: Installed command launcher

### 2. Run Interactive Menu

```bash
python3 nine_router_proxy.py
```

**You'll see:**
```
🚀 NineRouter Autoproxy - Main Menu

What would you like to do?
  S  Setup (install & configure)
  R  Run proxy server
  D  Run diagnostics
  H  Help & documentation
  Q  Quit

Select option: 
```

### 3. Follow the Wizard (Option S)

```
Type: S
↓
System Requirements Check ✅
Port Configuration (default: 8080)
Installing Addon
Verification
Setup complete!
```

### 4. Start the Proxy (Option R)

```
Type: R
↓
Proxy starts on 127.0.0.1:8080
Shows real-time logs
Press Ctrl+C to stop
```

### 5. Configure 9Router

In 9Router settings:
- **Address:** `127.0.0.1`
- **Port:** `8080`
- **Protocol:** HTTP

---

## 📋 Command Line Usage

### Interactive Menu (Default)
```bash
9router-proxy
```
Opens menu to Setup / Run / Diagnose

### Setup Only
```bash
9router-proxy --setup
```
Runs the setup wizard without menu

### Run Proxy Directly
```bash
9router-proxy --run
```
Starts proxy immediately (must run setup first)

### Diagnostics Only
```bash
9router-proxy --diag
```
Runs full system checks and configuration dump

### If the launcher is not on PATH
```bash
~/.local/bin/9router-proxy --setup
```

---

## 🔍 Error Messages & Diagnostics

All errors have codes like **[E001]**, **[E002]**, etc. Each includes:
- **Title**: Short description
- **Message**: What went wrong
- **Check**: What to verify
- **Action**: How to fix it

### Examples:

#### E001 - Python Version Too Old
```
❌ [E001] Python Version Too Old
Python 3.9+ required for mitmproxy

🔍 Check: Current version: 3.8.10
💡 Action: Install Python 3.9 or later from python.org or Homebrew
```

**Fix:** `brew install python@3.11`

#### E002 - mitmproxy Not Installed
```
❌ [E002] mitmproxy Not Installed
mitmproxy is required to run this proxy

🔍 Check: mitmproxy not found in PATH
💡 Action: Run: brew install mitmproxy  OR  pip install mitmproxy
```

**Fix:** `brew install mitmproxy`

#### E003 - Port Already in Use
```
❌ [E003] Port Already in Use
The proxy port is already bound by another process

🔍 Check: Port 8080 in use by PID 12345
💡 Action: Change port in config, or: kill -9 12345
```

**Fix:** `kill -9 12345` or use different port in setup

#### E004 - Configuration File Not Found
```
❌ [E004] Configuration File Not Found
Config file is missing or unreadable

🔍 Check: Expected at: /Users/username/.nine_router/config.json
💡 Action: Run setup wizard first: python3 nine_router_proxy.py --setup
```

**Fix:** Run setup wizard first

#### E011 - SSL Certificate Verification Failed
```
❌ [E011] SSL Certificate Verification Failed
The remote endpoint could not be verified with the local certificate store

🔍 Check: URL: https://api.proxyscrape.com/v2/ | Status: certificate verification failed
💡 Action: Check the system date, trust store, and whether a custom proxy is intercepting HTTPS traffic
```

**Fix:** Check your local trust store, system date, VPN, firewall, or certificate intercepting proxy. The generated addon now logs this cleanly instead of crashing with a `NameError`.

#### E005 - ProxyScrape API Unreachable
```
❌ [E005] ProxyScrape API Unreachable
Cannot fetch proxy list from API

🔍 Check: ProxyScrape API timeout or connection error
💡 Action: Check internet connection, ProxyScrape service status, or firewall
```

**This is OK** - Proxy will use cached proxies and retry next rotation

#### E006 - No Proxies Available
```
❌ [E006] No Proxies Available
All proxies failed testing, no fallback available

🔍 Check: Dead proxy list full, batch exhausted
💡 Action: Proxies will auto-refresh next rotation. This is OK, traffic passes through direct.
```

**This is SAFE** - Requests pass through direct, will recover automatically

#### E008 - Unsupported Operating System
```
❌ [E008] Unsupported Operating System
This tool is optimized for macOS and Linux

🔍 Check: OS detected: Windows
💡 Action: This script may still work, but is untested on Windows
```

**May still work** - But is optimized for Mac/Linux

---

## 📊 Interactive Menu Options

### S - Setup Wizard
```
1️⃣  System Requirements Check
    - Verifies Python 3.9+
    - Checks for mitmproxy
    - Checks OS compatibility

2️⃣  Port Configuration
    - Default: 8080
    - Checks if port is available
    - Allows custom port

3️⃣  Installing Addon
    - Creates ~/.mitmproxy/ directory
    - Installs autoproxy addon file
    - Sets permissions

4️⃣  Verification
    - Confirms port is free
    - Tests configuration
```

**Output:**
```
✅ All system requirements met!
✅ Addon installed to ~/.mitmproxy/nine_router_autoproxy.py
✅ Setup complete!
```

### R - Run Proxy Server
```
Starts mitmproxy with autoproxy addon

Shows live logs:
🚀 NineRouter Autoproxy Rotator
Status: ✅ ACTIVE & LISTENING
Listen Address: http://localhost:8080

⏰ [Scheduler] Next proxy rotation in 60s
🔀 [Routing] Request via verified proxy -> 1.2.3.4:8080
🔄 [Auto-Rotate] 60 seconds elapsed
```

**Press Ctrl+C to stop**

### D - Run Diagnostics
```
Checks everything:
- System information
- Configuration loaded
- All prerequisite checks
- File system locations
- Suggests next steps

Example output:
  OS: Darwin 23.0.0
  Python: 3.11.0
  
  Python Version: ✅ 3.11.0
  mitmproxy: ✅ mitmproxy 10.0.2
  Port 8080: ✅ Available
  Internet: ✅ Connection OK
  
  Config dir: ~/.nine_router - ✅ Exists
  Addon file: ~/.mitmproxy/nine_router_autoproxy.py - ✅ Exists
```

The generated addon also includes a built-in `ErrorCode` helper, so self-signed certificate issues produce a clean E-code log instead of a runtime traceback during startup.

### H - Help & Documentation
```
Shows quick reference:
- Quick start steps
- Proxy details
- Features list
- Troubleshooting
- Configuration paths
- Support info
```

### Q - Quit
```
Exits the program
```

---

## 📁 Files & Configuration

### Automatic Locations

```
~/.nine_router/
  └─ config.json          # Configuration file

~/.mitmproxy/
  └─ nine_router_autoproxy.py    # Proxy addon
```

### Configuration File (config.json)

```json
{
  "port": 8080,
  "rotation_interval": 60,
  "max_workers": 10,
  "test_timeout": 2.0,
  "failed_proxy_memory": 20,
  "api_url": "https://api.proxyscrape.com/v2/...",
  "test_endpoints": [
    "http://httpbin.org/ip",
    "http://ifconfig.io",
    "http://icanhazip.com"
  ],
  "version": "1.0"
}
```

### Changing Configuration

**Edit port:**
```bash
# Manual edit
nano ~/.nine_router/config.json

# Or run setup again
python3 nine_router_proxy.py --setup
```

**View current config:**
```bash
python3 nine_router_proxy.py --diag
```

---

## 🎯 Log Messages Explained

### Startup
```
🚀 NineRouter Autoproxy Rotator
Status: ✅ ACTIVE & LISTENING
System: macOS
Proxy Type: HTTP
Listen Address: http://localhost:8080

📋 CONFIGURE 9ROUTER WITH:
   HTTP Proxy: 127.0.0.1:8080
```
✅ Proxy is ready

### Scheduling
```
⏰ [Scheduler] Next proxy rotation in 60s
```
✅ Rotation timer active

### Auto-Rotation
```
🔄 [Auto-Rotate] 60 seconds elapsed. Forcing proxy rotation...
```
✅ Automatically rotating every 60 seconds

### Testing
```
⚡ [Testing] Concurrent testing of 10 proxies...
✅ [Success] Found 8 active proxies. Selected: 1.2.3.4:8080 (125ms, different from last: True)
```
✅ Testing complete, fastest proxy selected

### Routing
```
🔀 [Routing] Request via verified proxy -> 1.2.3.4:8080 (speed: 125ms)
```
✅ Request routed through upstream proxy

### Failed Proxies
```
⚠️ [All Dead] All proxies failed. Adding to failed list and refreshing batch...
📡 [Rotator] Fetching 10 fresh ACTIVE HTTP proxies from ProxyScrape...
```
✅ Recovery triggered, fetching new batch

### Critical
```
❌ [Critical] No proxies available. Passing direct (unproxied).
```
⚠️ Extreme fallback, request goes unproxied

---

## 🚨 Troubleshooting

### Problem: "Python 3.9+ required" (E001)

**Error Message:**
```
❌ [E001] Python Version Too Old
Python 3.9+ required for mitmproxy

🔍 Check: Current version: 3.8.10
💡 Action: Install Python 3.9 or later
```

**Solution:**
```bash
# Check current version
python3 --version

# Install via Homebrew
brew install python@3.11

# Or download from python.org
```

### Problem: "mitmproxy Not Installed" (E002)

**Error Message:**
```
❌ [E002] mitmproxy Not Installed
mitmproxy is required to run this proxy
```

**Solution:**
```bash
# Install via Homebrew
brew install mitmproxy

# Or via pip
pip install mitmproxy

# Verify
mitmproxy --version
```

### Problem: "Port Already in Use" (E003)

**Error Message:**
```
❌ [E003] Port Already in Use
The proxy port is already bound by another process

🔍 Check: Port 8080 in use by PID 12345
```

**Solution:**
```bash
# Kill the process using the port
kill -9 12345

# Or run setup again and choose different port
python3 nine_router_proxy.py --setup
```

### Problem: "No 9Router Proxy Connection" (Not an Error Code)

**Check:**
1. Is mitmproxy running? → `lsof -i :8080`
2. Is 9Router configured correctly? → Should be `127.0.0.1:8080`
3. Is firewall blocking? → System Preferences → Security → Firewall

**Solution:**
```bash
# Verify mitmproxy is running
lsof -i :8080

# Reconfigure 9Router proxy settings
# In 9Router: Proxy = 127.0.0.1:8080

# Check logs for routing messages
# Should see: 🔀 [Routing] Request via verified proxy...
```

### Problem: "API Timeouts" (E005)

**Error Message:**
```
❌ [E005] ProxyScrape API Unreachable
Cannot fetch proxy list from API
```

**This is OK!** The proxy will:
- Continue using cached proxies
- Retry API next rotation
- Never stop working

**Solution:**
```bash
# Just wait - it will recover automatically
# Or check your internet connection
ping 8.8.8.8

# Or check if ProxyScrape is down
curl https://api.proxyscrape.com/v2/
```

### Problem: "No Proxies Available" (E006)

**Error Message:**
```
❌ [E006] No Proxies Available
All proxies failed testing
```

**This is SAFE!** Requests will pass through direct:
- Autoproxy will retry fetching new proxies
- Will recover next rotation cycle
- No requests are lost

**Solution:**
```bash
# Just wait - automatic recovery
# Or restart the proxy
# Press Ctrl+C and run again:
python3 nine_router_proxy.py --run
```

### Problem: "Configuration Invalid" (E010)

**Error Message:**
```
❌ [E010] Invalid Configuration
Configuration file is corrupted or invalid JSON
```

**Solution:**
```bash
# Reset configuration
rm ~/.nine_router/config.json

# Run setup again
python3 nine_router_proxy.py --setup
```

---

## 💡 Pro Tips

### 1. Run in Background

```bash
# Start in background and save logs
nohup python3 nine_router_proxy.py --run > /tmp/nineproxy.log 2>&1 &

# View logs in real-time
tail -f /tmp/nineproxy.log

# View only routing messages
tail -f /tmp/nineproxy.log | grep "\[Routing\]"

# Stop the background process
pkill -f nine_router_proxy
```

### 2. Monitor Proxy Changes

```bash
# Watch current upstream proxy in real-time
tail -f /tmp/nineproxy.log | grep "\[Routing\]"

# Example output:
# 🔀 [Routing] Request via verified proxy -> 1.2.3.4:8080 (speed: 125ms)
# 🔀 [Routing] Request via verified proxy -> 5.6.7.8:9090 (speed: 89ms)
# ...
```

### 3. Use Custom Port

```bash
# During setup, choose custom port (e.g., 9090)
python3 nine_router_proxy.py --setup

# Then configure 9Router to use that port
# Proxy: 127.0.0.1:9090
```

### 4. Auto-Start on Mac Login

```bash
# Create LaunchAgent
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.nineproxy.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nineproxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/nine_router_proxy.py</string>
        <string>--run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.nineproxy.plist
```

---

## 🎓 Understanding the Logs

### Log Symbols

| Symbol | Meaning |
|--------|---------|
| 🚀 | Startup message |
| ⏰ | Scheduler message |
| 🔄 | Auto-rotation |
| ⚡ | Testing proxies |
| ✅ | Success |
| 🔀 | Routing request |
| 📡 | Fetching from API |
| 📥 | Loaded proxies |
| ⚠️ | Warning/fallback |
| ❌ | Error |

### Sample Log Sequence

```
🚀 NineRouter Autoproxy Rotator
Status: ✅ ACTIVE & LISTENING
Listen Address: http://localhost:8080

⏰ [Scheduler] Next proxy rotation in 60s

[9Router makes a request]
⚡ [Testing] Concurrent testing of 10 proxies...
✅ [Success] Found 8 active proxies. Selected: 1.2.3.4:8080
🔀 [Routing] Request via verified proxy -> 1.2.3.4:8080 (speed: 125ms)

[60 seconds pass]
🔄 [Auto-Rotate] 60 seconds elapsed. Forcing proxy rotation...

⚡ [Testing] Concurrent testing of 10 proxies...
✅ [Success] Found 9 active proxies. Selected: 5.6.7.8:9090
🔀 [Routing] Request via verified proxy -> 5.6.7.8:9090 (speed: 98ms)
```

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Run setup: `python3 nine_router_proxy.py --setup`
- [ ] All checks pass (system requirements, port available)
- [ ] Addon installed to `~/.mitmproxy/`
- [ ] Start proxy: `python3 nine_router_proxy.py --run`
- [ ] Startup banner shows: ✅ ACTIVE & LISTENING
- [ ] Configure 9Router: `127.0.0.1:8080`
- [ ] Send request from 9Router
- [ ] Check logs for: 🔀 [Routing] message
- [ ] Wait 60 seconds
- [ ] See rotation: 🔄 [Auto-Rotate]
- [ ] New request shows different proxy IP

---

## 📞 Quick Reference Card

```bash
# Setup
python3 nine_router_proxy.py --setup

# Run
python3 nine_router_proxy.py --run

# Diagnose
python3 nine_router_proxy.py --diag

# Interactive menu
python3 nine_router_proxy.py

# View logs (if running in background)
tail -f /tmp/nineproxy.log

# Check if running
lsof -i :8080

# Stop (if background)
pkill -f nine_router_proxy

# Kill process on port
lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

## 🎉 You're Ready!

**Everything is in one file:** `nine_router_proxy.py`

1. Copy it to your Mac
2. Run: `python3 nine_router_proxy.py`
3. Choose: S (Setup)
4. Choose: R (Run)
5. Configure 9Router: `127.0.0.1:8080`

That's it! Enjoy automatic rotating proxies! 🚀
