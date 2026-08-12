# NineRouter Autoproxy

A lightweight rotating HTTP proxy helper for 9Router and other tools that need a resilient upstream proxy with auto-rotation, diagnostics, and graceful fallback behavior.

## Features

- Rotates through live HTTP proxies on a timer
- Tests proxy candidates in parallel and selects the fastest healthy result
- Avoids reusing the same proxy consecutively
- Tracks dead proxies in memory to skip repeated retries
- Includes diagnostics for missing dependencies, missing routes, SSL issues, timeouts, network outages, and more
- Generates a mitmproxy addon with embedded runtime diagnostics so startup does not crash on certificate failures
- Automatically copies the local proxy URL to the clipboard when available
- Supports configurable rotation and dead-proxy memory settings without editing code
- Provides setup and startup commands without requiring a package manager or framework

## Requirements

- Python 3.9+ already installed
- mitmproxy installed and available on your PATH (installer will install it if Python is present)
- Network access to fetch proxy lists and test endpoints

### Install with installer script

From the repository root directory on Linux/macOS:

```bash
chmod +x install.sh
./install.sh
```

On any platform with Python installed, you can use the cross-platform installer:

```bash
python3 install.py
```

On Windows, you can also run:

```cmd
install.bat
```

All installers (`install.sh`, `install.py`, and `install.bat`) perform the same installation steps:

- install runtime dependencies
- copy `nine_router_proxy.py` to the install directory
- create the launcher command `9router-proxy` or `nineRouter-autoproxy` if `9router-proxy` is already taken

If you are not already in the project folder, first clone the repo and `cd` into it:

```bash
git clone https://github.com/homelessdeveloper-vector/NineRouter-Autoproxy.git
cd NineRouter-Autoproxy
chmod +x install.sh
./install.sh
```

What the installer does:

- Detects an existing Python 3.9+ interpreter
- Installs Python dependencies: `requests`, `mitmproxy`, and `rich`
- Copies `nine_router_proxy.py` to `~/.local/bin` on macOS/Linux or `%LOCALAPPDATA%\NineRouterAutoproxy` on Windows
- Creates a launcher command named `9router-proxy` or `nineRouter-autoproxy` (`nineRouter-autoproxy.cmd` on Windows)
- Prints the next commands to run after installation

Files in this repository:

- `install.sh`: Linux/macOS shell installer
- `install.py`: Cross-platform Python installer for Windows, macOS, and Linux
- `install.bat`: Windows batch installer wrapper for `install.py`
- `nine_router_proxy.py`: Core proxy script with setup, diagnostics, and runtime logic
- `9router-proxy` or `nineRouter-autoproxy`: Installed launcher command for easy usage

What the installer does not do:

- It does not install Python itself. You must already have Python 3.9+ installed.

### Install mitmproxy

macOS:

```bash
brew install mitmproxy
```

Linux:

```bash
python3 -m pip install mitmproxy
```

## Quick start

```bash
9router-proxy
```

This opens the interactive menu. To run the proxy directly, use:

```bash
9router-proxy --run
```

To start setup directly:

```bash
9router-proxy --setup
```

To open the menu explicitly:

```bash
9router-proxy --menu
```

If `9router-proxy` is already taken on your system, the installer will create `nineRouter-autoproxy` instead.

```bash
nineRouter-autoproxy --menu
```

Or run the legacy script directly:

```bash
python3 nine_router_proxy.py --run
```

## Configuration

The script stores configuration at:

- ~/.nine_router/config.json
- ~/.mitmproxy/nine_router_autoproxy.py

Default values include:

- port: 8080
- rotation interval: 60 seconds
- max workers: 10
- timeout: 2.0 seconds per proxy test
- failed proxy memory: 20

## Diagnostics

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

## Error handling behavior

The project now includes clearer classification for common failures such as:

- route does not exist (404)
- access blocked or rate limited (403/429)
- SSL certificate verification failures
- request timeout or network unreachable conditions
- DNS issues
- invalid route configuration
- no available proxies after testing

Each error includes:

- a diagnostic code
- a human-friendly summary
- a check description
- an action to fix or retry

### Common SSL certificate failure

If the upstream ProxyScrape API fails with a certificate verification error like `CERTIFICATE_VERIFY_FAILED`, the generated addon will now log a proper E-code instead of crashing with a `NameError`.

Example diagnosis:

```text
❌ [E011] SSL Certificate Verification Failed
The remote endpoint could not be verified with the local certificate store

🔍 Check: URL: https://api.proxyscrape.com/v2/ | Status: certificate verification failed
💡 Action: Check the system date, trust store, and whether a custom proxy is intercepting HTTPS traffic
```

This usually means a local trust-store, VPN, firewall, or MITM certificate is intercepting HTTPS traffic.

## Running with 9Router

Configure your 9Router HTTP proxy settings to use:

- 127.0.0.1:8080
- or localhost:8080

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

Then stop the process or pick a different port during setup.

### API or route errors

Use diagnostics:

```bash
python3 nine_router_proxy.py --diag
```

If the upstream proxy API returns a certificate problem, timeout, 404, or blocked response, the script now surfaces a clearer explanation and recommended next step.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
