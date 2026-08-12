# NineRouter Autoproxy

A resilient rotating HTTP proxy helper for 9Router and other AI/dev tooling that needs a fast, stable upstream proxy with auto-rotation, diagnostics, and graceful fallback behavior.

> Never stop coding. Keep your tools online with smart proxy rotation, health checks, and automatic recovery.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![mitmproxy](https://img.shields.io/badge/Proxy-mitmproxy-2E7D32?logo=mitmproxy&logoColor=white)](https://mitmproxy.org/) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-5B7CFF)](#) [![Pre-Alpha](https://img.shields.io/badge/Status-Pre--Alpha-orange)](#)

[🚀 Quick Start](#quick-start) • [💡 Features](#key-features) • [📖 Setup](#installation) • [🔧 Configuration](#configuration)

> ⚠️ This project is currently in Pre-Alpha stage. It is early, experimental, and actively evolving. Feedback, testing, and issue reports are welcome.

## Why this project?

If your workflow depends on AI coding tools, proxy routing, or upstream proxy health, one dead endpoint can break an entire session. NineRouter Autoproxy keeps your connection resilient by rotating through healthy proxies, skipping dead candidates, and exposing clear diagnostics when upstream services fail.

## Key features

- Rotates through live HTTP proxies on a timer
- Tests proxy candidates in parallel and selects the fastest healthy result
- Avoids reusing the same proxy consecutively
- Keeps a memory of dead proxies so unhealthy endpoints are skipped automatically
- Validates connectivity, routes, SSL trust, timeouts, and outages with richer diagnostics
- Generates a mitmproxy addon with embedded runtime checks so startup is safer on certificate failures
- Copies the active local proxy URL to the clipboard when supported
- Supports rotation timing and dead-proxy memory configuration without editing code
- Ships with simple install and launch commands for Linux, macOS, and Windows

## Works with 9Router and modern AI tooling

This project is designed to power 9Router-based workflows and other setups that need a dependable HTTP proxy layer while staying resilient under network issues and noisy upstream providers.

## Please support the project

If you find this useful, please help keep it moving:

- Star the repo
- Share it with other developers and AI tool users
- Open issues for bugs, ideas, and improvements
- Contribute code, testing, or documentation

Your support helps fund development, improve stability, and keep the project growing.

---

## Quick Start

### Install

From the repository root:

```bash
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
python3 install.py
```

### Initialize (First Run Only)

Open a new terminal and run:

```bash
nine-router-autoproxy
```

This auto-configures everything. The proxy runs on **127.0.0.1:8080** by default.

### Use It

```bash
nine-router-autoproxy --run    # Start the proxy
nine-router-autoproxy --diag   # Check status
nine-router-autoproxy --menu   # Interactive menu
```

Configure your app/tool to use proxy: **127.0.0.1:8080**

## Installation

### Requirements

- Python 3.9+
- mitmproxy installed and available on your `PATH`
- Network access to fetch proxy lists and health-check endpoints
- 9Router installed for proxy routing

### Install mitmproxy

**macOS:**
```bash
brew install mitmproxy
```

**Linux:**
```bash
python3 -m pip install mitmproxy
```

**Windows:**
```bash
python3 -m pip install mitmproxy
```

### 9Router setup guide

9Router is the app that consumes this proxy. Install it from the official distribution for your platform.

> The installer attempts to detect a 9Router command and warns if it cannot find one. It does not install 9Router automatically.

## Configuration

The script stores configuration in:

- `~/.nine_router/config.json`
- `~/.mitmproxy/nine_router_autoproxy.py`

Default values include:

- port: `8080`
- rotation interval: `60` seconds
- max workers: `10`
- timeout: `2.0` seconds per proxy test
- failed proxy memory: `20`

### Reconfigure

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

## License

MIT License - See LICENSE file for details
