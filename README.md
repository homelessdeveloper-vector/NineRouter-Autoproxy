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

```bash
chmod +x install.sh
./install.sh
```

What `install.sh` does:

- Detects an existing Python 3.9+ interpreter
- Installs Python dependencies: `requests`, `mitmproxy`, and `rich`
- Copies `nine_router_proxy.py` to `~/.local/bin`
- Creates a launcher command named `nine-router-autoproxy`
- Prints the next commands to run after installation

What `install.sh` does not do:

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
nine-router-autoproxy --setup
nine-router-autoproxy --run
```

Or use the interactive menu:

```bash
python3 nine_router_proxy.py
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
