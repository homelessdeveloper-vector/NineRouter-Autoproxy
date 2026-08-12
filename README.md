# NineRouter Autoproxy

A resilient rotating HTTP proxy helper for 9Router and other AI/dev tooling that needs a fast, stable upstream proxy with auto-rotation, diagnostics, and graceful fallback behavior.

> Never stop coding. Keep your tools online with smart proxy rotation, health checks, and automatic recovery.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![mitmproxy](https://img.shields.io/badge/Proxy-mitmproxy-2E7D32?logo=mitmproxy&logoColor=white)](https://mitmproxy.org/) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-5B7CFF)](#) [![Pre-Alpha](https://img.shields.io/badge/Status-Pre--Alpha-orange)](#)

[🚀 Quick Start](#quick-start) • [💡 Features](#key-features) • [📖 Setup](#installation) • [⚙️ Installation Guide](#installation-guide) • [🔧 Configuration](#configuration)

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

## Quick start

```bash
9router-proxy
```

## Please support the project

If you find this useful, please help keep it moving:

- Star the repo
- Share it with other developers and AI tool users
- Open issues for bugs, ideas, and improvements
- Contribute code, testing, or documentation

Your support helps fund development, improve stability, and keep the project growing.

---


This opens the interactive menu. To run the proxy directly:

```bash
9router-proxy --run
```

To jump straight into setup:

```bash
9router-proxy --setup
```

To open the interactive menu explicitly:

```bash
9router-proxy --menu
```

If `9router-proxy` is already taken on your system, the installer creates `nineRouter-autoproxy` instead:

```bash
nineRouter-autoproxy --menu
```

Or run the script directly:

```bash
python3 nine_router_proxy.py --run
```

## Installation Guide

[📦 Install](#installation) • [🧰 Requirements](#requirements) • [⚡ Quick Start](#quick-start)

## Installation

### Requirements

- Python 3.9+
- mitmproxy installed and available on your `PATH`
- Network access to fetch proxy lists and health-check endpoints
- 9Router installed for proxy routing

### Install with installer script

From the repository root on Linux/macOS:

```bash
chmod +x install.sh
./install.sh
```

On any platform with Python installed:

```bash
python3 install.py
```

On Windows:

```cmd
install.bat
```

All installers perform the same setup steps:

- install Python dependencies
- copy the proxy script into the install directory
- create a launcher command such as `9router-proxy` or `nineRouter-autoproxy`

### Enabling the launcher command in new terminal windows

After installation, the launcher command is installed to `~/.local/bin` (macOS/Linux) or `AppData/Local/NineRouterAutoproxy` (Windows).

**For macOS/Linux with zsh or bash:**

Add this line to your shell profile (`~/.zshrc` for zsh, `~/.bashrc` or `~/.bash_profile` for bash):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your profile:

```bash
source ~/.zshrc  # or source ~/.bashrc / ~/.bash_profile
```

Or simply open a new terminal window.

**For Windows:**

The installer should add the directory to your PATH automatically. If not, add `%APPDATA%\Local\NineRouterAutoproxy` to your system PATH and restart your terminal.

If you're not in a new shell session yet, you can use the full path directly:

**macOS/Linux:**
```bash
~/.local/bin/9router-proxy --setup
# or
~/.local/bin/nineRouter-autoproxy --setup
```

**Windows:**
```cmd
%APPDATA%\Local\NineRouterAutoproxy\9router-proxy.cmd --setup
```

### All commands work from anywhere

Once the launcher is installed, all commands work from any directory:

```bash
nine-router-autoproxy --setup    # Setup wizard
nine-router-autoproxy --run      # Run proxy
nine-router-autoproxy --diag     # Run diagnostics
nine-router-autoproxy --menu     # Interactive menu
```

The launcher uses absolute paths, so it works consistently regardless of your current working directory.

### Reinstalling updates to the latest version

If you reinstall using the same installer script, it will automatically overwrite the old version:

```bash
python3 install.py
```

This ensures you're always running the latest version from the repository.

If you are not already in the project folder:

```bash
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
chmod +x install.sh
./install.sh
```

### Install mitmproxy

macOS:

```bash
brew install mitmproxy
```

Linux:

```bash
python3 -m pip install mitmproxy
```

## 9Router setup guide

9Router is the app that consumes this proxy. Install it from the official distribution for your platform.

### macOS / Linux

- Download and install 9Router from the official site.
- Ensure the app or executable is available on your system.

### Windows

- Download and install 9Router from the official site.
- Ensure the program is present and accessible.

> The installer attempts to detect a 9Router command and warns if it cannot find one. It does not install 9Router automatically.

### Run guide

1. Install the autoproxy using one of the installers above.
2. Run `9router-proxy` to open the interactive menu.
3. Select setup or run directly.
4. Confirm the proxy port and addon installation when prompted.
5. In 9Router, configure the HTTP proxy to `127.0.0.1:8080` (or the port chosen during setup).

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

## Diagnostics and error handling

Run the built-in diagnostic report:

```bash
python3 nine_router_proxy.py --diag
```

This checks:

- Python version
- OS compatibility
- mitmproxy availability
- port availability
- internet connectivity
- configured route and fallback health
- filesystem setup for config and addon files

The project classifies common upstream problems clearly, including:

- route does not exist (`404`)
- access blocked or rate limited (`403` / `429`)
- SSL certificate verification failures
- request timeout or network unreachable conditions
- DNS issues
- invalid route configuration
- no available proxies after testing

Each error includes a diagnostic code, a human-readable summary, a check description, and a recommended next step.

### Example SSL failure

```text
❌ [E011] SSL Certificate Verification Failed
The remote endpoint could not be verified with the local certificate store

🔍 Check: URL: https://api.proxyscrape.com/v2/ | Status: certificate verification failed
💡 Action: Check the system date, trust store, and whether a custom proxy is intercepting HTTPS traffic
```

This normally indicates a local certificate store issue, VPN/firewall interference, or a MITM-style intercept on the network path.

## Troubleshooting

### mitmproxy is missing

```bash
python3 -m pip install mitmproxy
```

### Port already in use

Check what is using the port:

```bash
lsof -i :8080
```

Then stop the process or choose a different port during setup.

### API or route errors

Use diagnostics:

```bash
python3 nine_router_proxy.py --diag
```

If the upstream proxy API returns a certificate problem, timeout, `404`, or rate-limit response, the app surfaces a clearer explanation and recommended recovery path.

## Project files

- `install.sh`: Linux/macOS installer
- `install.py`: Cross-platform installer
- `install.bat`: Windows launcher wrapper
- `nine_router_proxy.py`: Core proxy logic, setup flow, and diagnostics
- `LICENSE`: MIT license

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
