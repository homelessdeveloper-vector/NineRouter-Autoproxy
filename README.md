# NineRouter Autoproxy

A resilient rotating HTTP proxy helper for 9Router and other AI/dev tooling.

> Never stop coding. Keep your tools online with smart proxy rotation and automatic recovery.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![mitmproxy](https://img.shields.io/badge/Proxy-mitmproxy-2E7D32?logo=mitmproxy&logoColor=white)](https://mitmproxy.org/) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Quick Start

### 1. Install

**macOS/Linux:**
```bash
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
python3 install.py
```

**Windows:**
```cmd
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
python install.py
```

### 2. Initialize

Open a new terminal and run:
```bash
nine-router-autoproxy
```

This auto-configures everything (first run only). The proxy runs on **127.0.0.1:8080** by default.

### 3. Use It

```bash
nine-router-autoproxy --run    # Start the proxy
nine-router-autoproxy --diag   # Check status
nine-router-autoproxy --menu   # Interactive menu
```

Configure your app/tool to use proxy: **127.0.0.1:8080**

That's it! The proxy will:
- Rotate through healthy proxies automatically
- Avoid dead endpoints
- Handle timeouts and SSL issues
- Run diagnostics if anything breaks

## Prerequisites

Before installing, make sure you have:

1. **Python 3.9+**
2. **mitmproxy**:
   ```bash
   # macOS
   brew install mitmproxy
   
   # Linux
   python3 -m pip install mitmproxy
   
   # Windows
   python3 -m pip install mitmproxy
   ```
3. **9Router** installed (download from official site)

## Features

- 🔄 Rotates through live HTTP proxies
- ⚡ Parallel proxy health testing
- 🛡️ Avoids dead endpoints automatically
- 📊 Built-in diagnostics
- 🎯 Works from any directory
- 📝 Automatic configuration on first run

## Configuration

Advanced settings stored in: `~/.nine_router/config.json`

To reconfigure, delete the config and run again:
```bash
rm ~/.nine_router/config.json
nine-router-autoproxy
```

Or use interactive setup:
```bash
nine-router-autoproxy --setup
```

## Troubleshooting

### Command not found after install?
Open a new terminal window. The installer adds the command to your PATH.

### Proxy not working?
```bash
nine-router-autoproxy --diag
```

### Need to update?
Just run the installer again:
```bash
python3 install.py
```

## Support

- Star ⭐ the repo
- Report issues 🐛
- Share with others 📢
- Contribute code 💻

## License

MIT License - See LICENSE file for details
