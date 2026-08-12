# NineRouter Autoproxy

A lightweight rotating HTTP proxy helper for 9Router and other tools that need a resilient upstream proxy with auto-rotation, diagnostics, and graceful fallback behavior.

## Features

- Rotates through live HTTP proxies on a timer
- Tests proxy candidates in parallel and selects the fastest healthy result
- Avoids reusing the same proxy consecutively
- Tracks dead proxies in memory to skip repeated retries
- Includes diagnostics for missing dependencies, missing routes, SSL issues, timeouts, network outages, and more
- Provides setup and startup commands without requiring a package manager or framework

## Requirements

- Python 3.9+
- mitmproxy installed and available on your PATH
- Network access to fetch proxy lists and test endpoints

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
python3 nine_router_proxy.py --setup
python3 nine_router_proxy.py --run
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
