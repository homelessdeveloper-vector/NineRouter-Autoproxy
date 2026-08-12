#!/usr/bin/env python3
"""
🚀 NineRouter Autoproxy - All-in-One HTTP Proxy Rotator for 9Router
Integrated Setup, Configuration, Monitoring & Diagnostics

Usage:
    python3 nine_router_proxy.py         # Interactive menu
    python3 nine_router_proxy.py --run   # Run proxy directly
    python3 nine_router_proxy.py --setup # Setup wizard only
"""

import sys
import os
import json
import shutil
import subprocess
import threading
import time
import platform
from pathlib import Path
from typing import Optional, Dict, Tuple

import requests

# Try to import rich for nice UI, fallback to basic formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# Color codes for basic terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ErrorCode:
    """Error codes with diagnostic messages."""

    ERRORS = {
        "E001": {
            "title": "Python Version Too Old",
            "message": "Python 3.9+ required for mitmproxy",
            "check": "Current version: {version}",
            "action": "Install Python 3.9 or later from python.org or Homebrew"
        },
        "E002": {
            "title": "mitmproxy Not Installed",
            "message": "mitmproxy is required to run this proxy",
            "check": "mitmproxy not found in PATH",
            "action": "Run: brew install mitmproxy  OR  pip install mitmproxy"
        },
        "E003": {
            "title": "Port Already in Use",
            "message": "The proxy port is already bound by another process",
            "check": "Port {port} in use by PID {pid}",
            "action": "Change port in config, or: kill -9 {pid}"
        },
        "E004": {
            "title": "Configuration File Not Found",
            "message": "Config file is missing or unreadable",
            "check": "Expected at: {path}",
            "action": "Run setup wizard first: python3 nine_router_proxy.py --setup"
        },
        "E005": {
            "title": "ProxyScrape API Unreachable",
            "message": "Cannot fetch proxy list from API",
            "check": "ProxyScrape API timeout or connection error",
            "action": "Check internet connection, ProxyScrape service status, or firewall"
        },
        "E006": {
            "title": "No Proxies Available",
            "message": "All proxies failed testing, no fallback available",
            "check": "Dead proxy list full, batch exhausted",
            "action": "Proxies will auto-refresh next rotation. This is OK, traffic passes through direct."
        },
        "E007": {
            "title": "Addon Directory Permission Denied",
            "message": "Cannot write addon files to directory",
            "check": "Directory: {path}",
            "action": "Fix permissions: chmod 755 {path}  OR  run: mkdir -p ~/.mitmproxy"
        },
        "E008": {
            "title": "Unsupported Operating System",
            "message": "This tool is optimized for macOS and Linux",
            "check": "OS detected: {os}",
            "action": "This script may still work, but is untested on {os}"
        },
        "E009": {
            "title": "Mitmproxy Crashed",
            "message": "Proxy process exited unexpectedly",
            "check": "Exit code: {code}",
            "action": "Check logs, verify mitmproxy installation: mitmproxy --version"
        },
        "E010": {
            "title": "Invalid Configuration",
            "message": "Configuration file is corrupted or invalid JSON",
            "check": "File: {path}",
            "action": "Delete config and re-run setup: rm ~/.nine_router/config.json && python3 nine_router_proxy.py --setup"
        },
        "E011": {
            "title": "SSL Certificate Verification Failed",
            "message": "The remote endpoint could not be verified with the local certificate store",
            "check": "URL: {url} | Status: {status}",
            "action": "Check the system date, trust store, and whether a custom proxy is intercepting HTTPS traffic"
        },
        "E012": {
            "title": "Request Timeout",
            "message": "The upstream API or route did not respond in time",
            "check": "Endpoint: {url} | Timeout: {timeout}s",
            "action": "Retry later, check your network quality, or reduce the timeout for the current environment"
        },
        "E013": {
            "title": "Network Unreachable",
            "message": "Unable to access the network or remote host",
            "check": "Host: {host} | Error: {error}",
            "action": "Verify the internet connection, firewall, VPN, or captive portal and retry"
        },
        "E014": {
            "title": "Route Not Found",
            "message": "The requested API route does not exist or is no longer available",
            "check": "Route: {route} | Response: {status}",
            "action": "Confirm the API URL and update the upstream route if the service changed"
        },
        "E015": {
            "title": "Rate Limited or Forbidden",
            "message": "The service rejected the request before the proxy could rotate",
            "check": "Route: {route} | Status: {status}",
            "action": "Wait a bit, lower request frequency, or switch to an alternate proxy source"
        },
        "E016": {
            "title": "Invalid Endpoint Configuration",
            "message": "The endpoint URL is malformed or unsupported",
            "check": "URL: {url}",
            "action": "Validate the URL format and ensure it begins with http:// or https://"
        },
        "E017": {
            "title": "DNS Resolution Failed",
            "message": "The host name could not be resolved",
            "check": "Host: {host}",
            "action": "Check the DNS settings, local resolvers, and network adapters"
        },
        "E018": {
            "title": "Upstream Proxy Route Unreachable",
            "message": "The selected proxy or route is blocked or refusing requests",
            "check": "Proxy: {proxy} | Target: {target}",
            "action": "Remove the broken proxy from the active list and retry with a fresh batch"
        },
        "E999": {
            "title": "Unexpected Error",
            "message": "An unknown runtime error occurred while checking connectivity",
            "check": "Context: {context} | Error: {error}",
            "action": "Capture the logs and re-run the diagnostics command to isolate the issue"
        },
    }

    @staticmethod
    def _safe_format(template: str, **kwargs) -> str:
        """Format text without crashing if a placeholder is missing."""
        if not template:
            return ""
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    @staticmethod
    def format_error(code: str, **kwargs) -> str:
        """Format an error with details."""
        if code not in ErrorCode.ERRORS:
            return f"Unknown error: {code}"

        err = ErrorCode.ERRORS[code]
        msg = f"\n{Colors.RED}{Colors.BOLD}❌ [{code}] {err['title']}{Colors.END}\n"
        msg += f"{Colors.RED}{err['message']}{Colors.END}\n\n"

        if 'check' in err:
            msg += f"{Colors.YELLOW}🔍 Check:{Colors.END} {ErrorCode._safe_format(err['check'], **kwargs)}\n"

        if 'action' in err:
            msg += f"{Colors.CYAN}💡 Action:{Colors.END} {ErrorCode._safe_format(err['action'], **kwargs)}\n"

        return msg

    @staticmethod
    def classify_http_exception(exc: Exception, context: str = "network") -> str:
        """Map request exceptions into compact diagnostics codes."""
        if isinstance(exc, requests.exceptions.SSLError):
            return "E011"
        if isinstance(exc, requests.exceptions.Timeout):
            return "E012"
        if isinstance(exc, requests.exceptions.ConnectionError):
            return "E013"
        if isinstance(exc, requests.exceptions.HTTPError):
            response = exc.response
            status = getattr(response, 'status_code', 'unknown')
            if status == 404:
                return "E014"
            if status in (403, 429):
                return "E015"
            return "E015"
        if isinstance(exc, requests.exceptions.InvalidURL):
            return "E016"
        if isinstance(exc, requests.exceptions.InvalidSchema):
            return "E016"
        if isinstance(exc, requests.exceptions.RetryError):
            return "E013"
        if isinstance(exc, requests.exceptions.TooManyRedirects):
            return "E018"
        return "E999"


class Config:
    """Configuration management"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".nine_router"
        self.config_file = self.config_dir / "config.json"
        self.addon_dir = Path.home() / ".mitmproxy"
        self.addon_file = self.addon_dir / "nine_router_autoproxy.py"
        self.default_config = {
            "port": 8080,
            "rotation_interval": 60,
            "proxy_batch_size": 10,
            "max_workers": 10,
            "test_timeout": 2.0,
            "api_url": "https://api.proxyscrape.com/v4/free-proxy-list/get?protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&limit=2000&request=getproxies&simplified=false",
            "test_endpoints": [
                "http://httpbin.org/ip",
                "http://ifconfig.io",
                "http://icanhazip.com"
            ],
            "failed_proxy_memory": 20,
            "never_repeat_proxy": True,
            "version": "1.0"
        }
    
    def exists(self) -> bool:
        """Check if config exists and is valid"""
        if not self.config_file.exists():
            return False
        try:
            with open(self.config_file) as f:
                json.load(f)
            return True
        except:
            return False
    
    def load(self) -> Dict:
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                raise ValueError(ErrorCode.format_error("E010", path=str(self.config_file)))
        return self.default_config.copy()
    
    def save(self, config: Dict) -> None:
        """Save configuration"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except PermissionError:
            raise PermissionError(ErrorCode.format_error("E007", path=str(self.config_dir)))
    
    def get(self, key: str, default=None):
        """Get config value"""
        config = self.load()
        return config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set config value"""
        config = self.load()
        config[key] = value
        self.save(config)


class SystemChecker:
    """Check system prerequisites and network health."""

    @staticmethod
    def check_python() -> Tuple[bool, str]:
        """Check Python version."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            return False, ErrorCode.format_error("E001", version=f"{version.major}.{version.minor}")
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"

    @staticmethod
    def check_mitmproxy() -> Tuple[bool, str]:
        """Check if mitmproxy is installed."""
        try:
            result = subprocess.run(['mitmproxy', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                return True, f"✅ {version}"
            return False, ErrorCode.format_error("E002")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, ErrorCode.format_error("E002")

    @staticmethod
    def check_port(port: int) -> Tuple[bool, str]:
        """Check if port is available."""
        try:
            result = subprocess.run(
                f"lsof -i :{port} -sTCP:LISTEN 2>/dev/null || true",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    try:
                        pid = lines[1].split()[1]
                        return False, ErrorCode.format_error("E003", port=port, pid=pid)
                    except Exception:
                        pass
                return False, f"❌ Port {port} is in use"
            return True, f"✅ Port {port} is available"
        except Exception:
            return True, f"⚠️  Could not verify port (proceeding anyway)"

    @staticmethod
    def check_os() -> Tuple[bool, str]:
        """Check operating system."""
        os_name = platform.system()
        if os_name not in ['Darwin', 'Linux', 'Windows']:
            return False, ErrorCode.format_error("E008", os=os_name)
        return True, f"✅ {os_name}"

    @staticmethod
    def check_internet() -> Tuple[bool, str]:
        """Check internet connectivity and classify common failures."""
        url = "https://api.proxyscrape.com/v2/"
        timeout = 7
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return True, "✅ Internet connection OK"
        except requests.exceptions.HTTPError as exc:
            code = ErrorCode.classify_http_exception(exc)
            status = getattr(exc.response, 'status_code', 'unknown')
            return False, ErrorCode.format_error(code, route=url, status=status, url=url, timeout=timeout)
        except requests.exceptions.Timeout as exc:
            return False, ErrorCode.format_error("E012", url=url, timeout=timeout)
        except requests.exceptions.SSLError as exc:
            return False, ErrorCode.format_error("E011", url=url, status="SSL verification failed")
        except requests.exceptions.ConnectionError as exc:
            return False, ErrorCode.format_error("E013", host="api.proxyscrape.com", error=str(exc))
        except requests.exceptions.InvalidURL as exc:
            return False, ErrorCode.format_error("E016", url=url)
        except requests.exceptions.RequestException as exc:
            return False, ErrorCode.format_error("E999", context="internet check", error=str(exc))
        except Exception as exc:
            return False, ErrorCode.format_error("E999", context="internet check", error=str(exc))

    @staticmethod
    def diagnose_route(url: str, timeout: int = 7) -> Tuple[bool, str]:
        """Probe a route and return a human-readable diagnostic result."""
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 404:
                return False, ErrorCode.format_error("E014", route=url, status=response.status_code)
            response.raise_for_status()
            return True, f"✅ Route reachable: {url} (HTTP {response.status_code})"
        except requests.exceptions.HTTPError as exc:
            code = ErrorCode.classify_http_exception(exc)
            status = getattr(exc.response, 'status_code', 'unknown')
            return False, ErrorCode.format_error(code, route=url, status=status, url=url)
        except requests.exceptions.Timeout as exc:
            return False, ErrorCode.format_error("E012", url=url, timeout=timeout)
        except requests.exceptions.SSLError as exc:
            return False, ErrorCode.format_error("E011", url=url, status="SSL verification failed")
        except requests.exceptions.ConnectionError as exc:
            return False, ErrorCode.format_error("E013", host=url, error=str(exc))
        except requests.exceptions.InvalidURL as exc:
            return False, ErrorCode.format_error("E016", url=url)
        except requests.exceptions.RequestException as exc:
            return False, ErrorCode.format_error("E999", context=f"route:{url}", error=str(exc))
        except Exception as exc:
            return False, ErrorCode.format_error("E999", context=f"route:{url}", error=str(exc))


class ClipboardHelper:
    """Copy a value to the system clipboard when supported."""

    @staticmethod
    def copy_text(value: str) -> Tuple[bool, str]:
        """Attempt to copy the supplied value to the OS clipboard."""
        if not value:
            return False, "Empty value provided for clipboard copy"

        value = str(value).strip()
        os_name = platform.system().lower()

        try:
            if os_name == 'darwin':
                result = subprocess.run(['pbcopy'], input=value, text=True, capture_output=True, check=False)
                if result.returncode == 0:
                    return True, "Copied to clipboard"
                return False, "pbcopy failed"

            if os_name == 'linux':
                for cmd in (['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input'], ['wl-copy']):
                    if shutil.which(cmd[0]):
                        result = subprocess.run(cmd, input=value, text=True, capture_output=True, check=False)
                        if result.returncode == 0:
                            return True, "Copied to clipboard"
                        return False, f"Clipboard command failed: {' '.join(cmd)}"
                return False, "No Linux clipboard utility found (install xclip, xsel, or wl-clipboard)"

            if os_name == 'windows':
                result = subprocess.run(['powershell', '-NoProfile', '-Command', 'Set-Clipboard -Value @"' + value + '"@'], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return True, "Copied to clipboard"
                return False, "PowerShell clipboard command failed"

            return False, f"Clipboard copy is not supported on {platform.system()}"
        except Exception as exc:
            return False, str(exc)


class UI:
    """Terminal User Interface"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
    
    def header(self, text: str) -> None:
        """Print header"""
        if self.console:
            self.console.print(f"\n{text}\n", style="bold cyan underline")
        else:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}\n")
    
    def section(self, title: str) -> None:
        """Print section title"""
        if self.console:
            self.console.print(f"\n{title}", style="bold blue")
        else:
            print(f"\n{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    
    def info(self, msg: str) -> None:
        """Print info message"""
        if self.console:
            self.console.print(f"ℹ️  {msg}", style="cyan")
        else:
            print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")
    
    def success(self, msg: str) -> None:
        """Print success message"""
        if self.console:
            self.console.print(f"✅ {msg}", style="bold green")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ {msg}{Colors.END}")
    
    def warning(self, msg: str) -> None:
        """Print warning message"""
        if self.console:
            self.console.print(f"⚠️  {msg}", style="bold yellow")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {msg}{Colors.END}")
    
    def error(self, msg: str) -> None:
        """Print error message"""
        if self.console:
            self.console.print(f"❌ {msg}", style="bold red")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ {msg}{Colors.END}")
    
    def code_block(self, code: str, title: str = "") -> None:
        """Print code block"""
        if self.console:
            if title:
                self.console.print(f"\n{title}:", style="bold")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
            self.console.print(syntax)
        else:
            print(f"\n{title}:")
            print(code)
    
    def table(self, title: str, data: Dict[str, str]) -> None:
        """Print table"""
        if self.console:
            table = Table(title=title)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            for key, value in data.items():
                table.add_row(key, str(value))
            self.console.print(table)
        else:
            print(f"\n{title}")
            print("-" * 50)
            for key, value in data.items():
                print(f"  {key:<20} {value}")
            print("-" * 50)
    
    def prompt_text(self, prompt: str, default: str = "") -> str:
        """Prompt for text input"""
        if self.console:
            return Prompt.ask(prompt, default=default)
        else:
            if default:
                print(f"{prompt} [{default}]: ", end="", flush=True)
            else:
                print(f"{prompt}: ", end="", flush=True)
            response = input()
            return response or default
    
    def prompt_confirm(self, prompt: str, default: bool = True) -> bool:
        """Prompt for yes/no"""
        if self.console:
            return Confirm.ask(prompt, default=default)
        else:
            yes_no = "Y/n" if default else "y/N"
            print(f"{prompt} [{yes_no}]: ", end="", flush=True)
            response = input().lower()
            if default:
                return response != 'n'
            else:
                return response == 'y'
    
    def menu(self, title: str, options: Dict[str, str]) -> str:
        """Display menu and get selection"""
        self.header(title)
        
        for key, description in options.items():
            print(f"  {Colors.CYAN}{key}{Colors.END}  {description}")
        
        print()
        choice = input(f"{Colors.BLUE}Select option: {Colors.END}").strip().upper()
        return choice
    
    def status_box(self, title: str, items: Dict[str, str]) -> None:
        """Display status box"""
        if self.console:
            from rich.panel import Panel
            content = "\n".join([f"{k}: {v}" for k, v in items.items()])
            self.console.print(Panel(content, title=title, expand=False, border_style="green"))
        else:
            print(f"\n{'='*50}")
            print(f"  {title}")
            print(f"{'='*50}")
            for key, value in items.items():
                print(f"  {key}: {value}")
            print(f"{'='*50}\n")


# Mitmproxy addon code (embedded)
ADDON_TEMPLATE = '''import concurrent.futures
import requests
import threading
import time
import sys
from collections import deque
from mitmproxy import ctx


class Colors:
    RED = ""
    BOLD = ""
    YELLOW = ""
    CYAN = ""
    END = ""


class ErrorCode:
    """Runtime-safe error diagnostics for the generated addon."""

    ERRORS = {
        "E011": {
            "title": "SSL Certificate Verification Failed",
            "message": "The remote endpoint could not be verified with the local certificate store",
            "check": "URL: {url} | Status: {status}",
            "action": "Check the system date, trust store, and whether a custom proxy is intercepting HTTPS traffic",
        },
        "E012": {
            "title": "Request Timeout",
            "message": "The upstream API or route did not respond in time",
            "check": "Endpoint: {url} | Timeout: {timeout}s",
            "action": "Retry later, check your network quality, or reduce the timeout for the current environment",
        },
        "E013": {
            "title": "Network Unreachable",
            "message": "Unable to access the network or remote host",
            "check": "Host: {host} | Error: {error}",
            "action": "Verify the internet connection, firewall, VPN, or captive portal and retry",
        },
        "E014": {
            "title": "Route Not Found",
            "message": "The requested API route does not exist or is no longer available",
            "check": "Route: {route} | Response: {status}",
            "action": "Confirm the API URL and update the upstream route if the service changed",
        },
        "E015": {
            "title": "Rate Limited or Forbidden",
            "message": "The service rejected the request before the proxy could rotate",
            "check": "Route: {route} | Status: {status}",
            "action": "Wait a bit, lower request frequency, or switch to an alternate proxy source",
        },
        "E016": {
            "title": "Invalid Endpoint Configuration",
            "message": "The endpoint URL is malformed or unsupported",
            "check": "URL: {url}",
            "action": "Validate the URL format and ensure it begins with http:// or https://",
        },
        "E018": {
            "title": "Upstream Proxy Route Unreachable",
            "message": "The selected proxy or route is blocked or refusing requests",
            "check": "Proxy: {proxy} | Target: {target}",
            "action": "Remove the broken proxy from the active list and retry with a fresh batch",
        },
        "E999": {
            "title": "Unexpected Error",
            "message": "An unknown runtime error occurred while checking connectivity",
            "check": "Context: {context} | Error: {error}",
            "action": "Capture the logs and re-run the diagnostics command to isolate the issue",
        },
    }

    @staticmethod
    def _safe_format(template: str, **kwargs) -> str:
        if not template:
            return ""
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    @staticmethod
    def format_error(code: str, **kwargs) -> str:
        if code not in ErrorCode.ERRORS:
            return "Unknown error: " + code

        err = ErrorCode.ERRORS[code]
        lines = []
        lines.append("[E" + code[-3:] + "] " + err['title'])
        lines.append(err['message'])
        lines.append("")

        if 'check' in err:
            lines.append("Check: " + ErrorCode._safe_format(err['check'], **kwargs))
        if 'action' in err:
            lines.append("Action: " + ErrorCode._safe_format(err['action'], **kwargs))

        result = ""
        for line in lines:
            result = result + line + chr(10)
        return result

    @staticmethod
    def classify_http_exception(exc):
        if isinstance(exc, requests.exceptions.SSLError):
            return "E011"
        if isinstance(exc, requests.exceptions.Timeout):
            return "E012"
        if isinstance(exc, requests.exceptions.ConnectionError):
            return "E013"
        if isinstance(exc, requests.exceptions.HTTPError):
            status = getattr(exc.response, 'status_code', 'unknown')
            if status == 404:
                return "E014"
            if status in (403, 429):
                return "E015"
            return "E015"
        if isinstance(exc, requests.exceptions.InvalidURL):
            return "E016"
        if isinstance(exc, requests.exceptions.InvalidSchema):
            return "E016"
        if isinstance(exc, requests.exceptions.TooManyRedirects):
            return "E018"
        return "E999"


class NineRouterPreTester:
    def __init__(self):
        self.raw_proxies = []
        self.current_proxy = None
        self.previous_proxy = None
        self.failed_proxy_memory = __FAILED_PROXY_MEMORY__
        self.failed_proxies = deque(maxlen=self.failed_proxy_memory)
        self.proxy_scores = {}
        self.rotation_interval = __ROTATION_INTERVAL__
        self.batch_size = __PROXY_BATCH_SIZE__
        self.max_workers = __MAX_WORKERS__
        self.never_repeat_proxy = __NEVER_REPEAT_PROXY__
        self.lock = threading.Lock()
        self.rotation_timer = None
        
        self._announce_startup()
        self.refresh_batch()
        self.schedule_rotation()

    def _format_box(self, lines, width=74):
        border_top = "╔" + "═" * width + "╗"
        border_bottom = "╚" + "═" * width + "╝"
        body_lines = []
        for line in lines:
            body_lines.append("║" + line.ljust(width) + "║")
        body = ""
        for body_line in body_lines:
            body = body + body_line + chr(10)
        return border_top + chr(10) + body + border_bottom

    def _announce_startup(self):
        """Announce localhost HTTP proxy details for 9router configuration."""
        system = sys.platform
        if system == "darwin":
            os_name = "macOS"
        elif system == "linux":
            os_name = "Linux"
        elif system == "win32":
            os_name = "Windows"
        else:
            os_name = system
        
        repeat_text = "Never same proxy twice in a row" if self.never_repeat_proxy else "Proxy may repeat before refresh"
        announcement = self._format_box([
            "                   🚀 NineRouter Autoproxy Rotator",
            "",
            "  Status: ✅ ACTIVE & LISTENING",
            f"  System: {os_name}",
            "  Proxy Type: HTTP",
            "  Listen Address: http://localhost:8080",
            "",
            "  📋 CONFIGURE 9ROUTER WITH:",
            "     HTTP Proxy: 127.0.0.1:8080",
            "     Or: localhost:8080",
            "",
            f"  🔄 Rotation: Every {self.rotation_interval} seconds (auto)",
            f"  Strategy: Fetch {self.batch_size} ACTIVE proxies → Test in parallel → Pick fastest",
            f"  Fallback: Memory of {self.failed_proxy_memory} dead proxies (skip retesting)",
            f"  Guarantee: {repeat_text}",
            ""
        ], width=74)
        ctx.log.info(announcement)

    def schedule_rotation(self):
        """Schedule the next proxy rotation."""
        self.rotation_timer = threading.Timer(
            self.rotation_interval,
            self._rotate_proxy_scheduled
        )
        self.rotation_timer.daemon = True
        self.rotation_timer.start()
        ctx.log.info(f"⏰ [Scheduler] Next proxy rotation in {self.rotation_interval}s")

    def _rotate_proxy_scheduled(self):
        """Called by the timer to rotate proxy."""
        with self.lock:
            ctx.log.info("🔄 [Auto-Rotate] Timer elapsed. Forcing proxy rotation...")
            self.current_proxy = None
        self.schedule_rotation()

    def refresh_batch(self):
        """Fetches a fresh batch of ACTIVE HTTP proxies from ProxyScrape with SSL retry fallback."""
        ctx.log.info(f"📡 [Rotator] Fetching {self.batch_size} fresh ACTIVE HTTP proxies from ProxyScrape...")

        https_url = (
            "https://api.proxyscrape.com/v2/"
            "?request=get"
            "&protocol=http"
            "&timeout=5000"
            "&ssl=yes"
            "&anonymity=all"
            "&country=all"
            "&simplified=true"
            "&sort=last_checked"
        )
        
        http_url = (
            "http://api.proxyscrape.com/v2/"
            "?request=get"
            "&protocol=http"
            "&timeout=5000"
            "&ssl=yes"
            "&anonymity=all"
            "&country=all"
            "&simplified=true"
            "&sort=last_checked"
        )

        # Try HTTPS first, fallback to HTTP on SSL errors
        urls_to_try = [
            (https_url, True, 10),      # (url, verify_ssl, timeout)
            (https_url, False, 10),     # Retry HTTPS without SSL verification
            (http_url, True, 10),       # Fallback to HTTP
        ]

        for attempt_url, verify_ssl, timeout in urls_to_try:
            try:
                protocol = "HTTPS (verified)" if attempt_url.startswith("https") and verify_ssl else \
                           "HTTPS (unverified)" if attempt_url.startswith("https") else "HTTP"
                ctx.log.debug(f"🔗 [Rotator] Attempting {protocol}: {attempt_url[:50]}...")
                
                response = requests.get(attempt_url, timeout=timeout, verify=verify_ssl)
                response.raise_for_status()

                raw_list = response.text.strip().split("\\r\\n")
                self.raw_proxies = []
                for p in raw_list:
                    p = p.strip()
                    if ":" in p and self._is_valid_proxy(p):
                        if p not in self.failed_proxies:
                            self.raw_proxies.append(p)

                self.raw_proxies = list(dict.fromkeys(self.raw_proxies))[:self.batch_size]
                ctx.log.info(f"📥 [Rotator] Loaded {len(self.raw_proxies)} validated HTTP proxies via {protocol}")
                return  # Success, exit retry loop

            except requests.exceptions.SSLError as exc:
                ctx.log.warn(f"⚠️  [SSL Error] Certificate verification failed on {attempt_url[:40]}... Trying fallback.")
                # Continue to next URL in the list
                continue
            except requests.exceptions.Timeout as exc:
                ctx.log.error(ErrorCode.format_error("E012", url=attempt_url, timeout=timeout))
                self.raw_proxies = []
                return
            except requests.exceptions.ConnectionError as exc:
                ctx.log.warn(f"⚠️  [Connection Error] Could not reach {attempt_url[:40]}... Trying next option.")
                continue
            except requests.exceptions.HTTPError as exc:
                status = getattr(exc.response, 'status_code', 'unknown')
                code = ErrorCode.classify_http_exception(exc)
                ctx.log.error(ErrorCode.format_error(code, route=attempt_url, status=status, url=attempt_url))
                self.raw_proxies = []
                return
            except requests.exceptions.InvalidURL as exc:
                ctx.log.error(ErrorCode.format_error("E016", url=attempt_url))
                self.raw_proxies = []
                return
            except requests.exceptions.RequestException as exc:
                ctx.log.error(ErrorCode.format_error("E999", context="proxy fetch", error=str(exc)))
                self.raw_proxies = []
                return
            except Exception as exc:
                ctx.log.error(ErrorCode.format_error("E999", context="proxy fetch", error=str(exc)))
                self.raw_proxies = []
                return

        # All retry attempts exhausted
        ctx.log.error("❌ [Rotator] All proxy fetch attempts failed. No fallback available.")
        self.raw_proxies = []

    def _is_valid_proxy(self, proxy_str):
        """Validates proxy is in valid IP:port format."""
        try:
            parts = proxy_str.split(":")
            if len(parts) != 2:
                return False
            ip, port = parts
            if not all(c.isdigit() or c == "." for c in ip):
                return False
            if not port.isdigit() or not (1 <= int(port) <= 65535):
                return False
            return True
        except:
            return False

    def check_single_proxy(self, proxy_str):
        """Tests a single proxy concurrently."""
        proxy_config = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }
        
        test_urls = [
            "http://httpbin.org/ip",
            "http://ifconfig.io",
            "http://icanhazip.com",
        ]
        
        for test_url in test_urls:
            try:
                start = time.time()
                response = requests.get(
                    test_url,
                    proxies=proxy_config,
                    timeout=2.0,
                    allow_redirects=False
                )
                elapsed_ms = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    ctx.log.debug(f"✓ {proxy_str} OK ({elapsed_ms:.0f}ms via {test_url})")
                    return (proxy_str, elapsed_ms)
                    
            except requests.exceptions.Timeout:
                continue
            except Exception:
                continue
        
        return None

    def find_working_proxy(self):
        """Tests current batch concurrently and returns best working proxy."""
        if not self.raw_proxies:
            ctx.log.warn("⚠️ [Testing] No proxies in batch. Refreshing...")
            self.refresh_batch()
            if not self.raw_proxies:
                ctx.log.error("❌ [Testing] Refresh failed. Batch is empty.")
                return None

        ctx.log.info(f"⚡ [Testing] Concurrent testing of {len(self.raw_proxies)} proxies...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.check_single_proxy, self.raw_proxies)
        
        working_proxies = [p for p in results if p is not None]
        
        if working_proxies:
            working_proxies.sort(key=lambda x: x[1])
            
            selected = None
            if self.never_repeat_proxy:
                for proxy, speed in working_proxies:
                    if proxy != self.previous_proxy:
                        selected = proxy
                        break
            else:
                selected = working_proxies[0][0]
            
            if not selected:
                selected = working_proxies[0][0]
            
            for proxy, speed in working_proxies:
                self.proxy_scores[proxy] = speed
            
            ctx.log.info(
                f"✅ [Success] Found {len(working_proxies)} active proxies. "
                f"Selected: {selected} ({self.proxy_scores[selected]:.0f}ms, "
                f"different from last: {selected != self.previous_proxy})"
            )
            return selected
        
        ctx.log.warn("⚠️ [All Dead] All proxies failed. Adding to failed list and refreshing batch...")
        for proxy in self.raw_proxies:
            self.failed_proxies.append(proxy)
        
        self.refresh_batch()
        return None

    def request(self, flow):
        """Intercepts HTTP/HTTPS requests and routes via verified rotating proxy."""
        with self.lock:
            if not self.current_proxy:
                self.current_proxy = self.find_working_proxy()
            
            active_proxy = self.current_proxy
        
        if not active_proxy:
            if self.raw_proxies:
                active_proxy = self.raw_proxies[0]
                ctx.log.warn(f"⚠️ [Fallback] Using untested proxy: {active_proxy}")
            else:
                ctx.log.error("❌ [Critical] No proxies available. Passing direct (unproxied).")
                return
        
        try:
            ip, port = active_proxy.split(":")
            port = int(port)
            
            self.previous_proxy = self.current_proxy
            
            ctx.log.info(
                f"🔀 [Routing] Request via verified proxy -> {ip}:{port} "
                f"(speed: {self.proxy_scores.get(active_proxy, 'unknown')}ms)"
            )
            
            flow.live.change_upstream_proxy_server((ip, port))
            
        except ValueError as e:
            ctx.log.error(f"❌ [Error] Invalid proxy format {active_proxy}: {e}")

    def done(self):
        """Cleanup when addon is unloaded."""
        if self.rotation_timer:
            self.rotation_timer.cancel()
        
        announcement = self._format_box([
            "                   🛑 Autoproxy Rotator Shutting Down",
            "",
            "  Status: STOPPED",
            "  Proxy: http://localhost:8080 (no longer available)",
            ""
        ], width=74)
        ctx.log.info(announcement)

addons = [NineRouterPreTester()]
'''


def build_addon_code(config: Dict) -> str:
    """Render the addon code from configured values."""
    rotation_interval = max(5, int(config.get("rotation_interval", 60)))
    batch_size = max(1, int(config.get("proxy_batch_size", 10)))
    max_workers = max(1, int(config.get("max_workers", 10)))
    failed_memory = max(1, int(config.get("failed_proxy_memory", 20)))
    never_repeat = bool(config.get("never_repeat_proxy", True))

    return ADDON_TEMPLATE \
        .replace("__ROTATION_INTERVAL__", str(rotation_interval)) \
        .replace("__PROXY_BATCH_SIZE__", str(batch_size)) \
        .replace("__MAX_WORKERS__", str(max_workers)) \
        .replace("__FAILED_PROXY_MEMORY__", str(failed_memory)) \
        .replace("__NEVER_REPEAT_PROXY__", str(never_repeat))


ADDON_CODE = build_addon_code(Config().default_config)


class SetupWizard:
    """Interactive setup wizard"""
    
    def __init__(self, ui: UI, config: Config):
        self.ui = ui
        self.config = config
    
    def run(self) -> bool:
        """Run setup wizard"""
        self.ui.header("🔧 NineRouter Autoproxy - Setup Wizard")
        
        # System checks
        self.ui.section("1️⃣  System Requirements Check")
        checks = [
            ("Python Version", SystemChecker.check_python()),
            ("Operating System", SystemChecker.check_os()),
            ("mitmproxy Installation", SystemChecker.check_mitmproxy()),
        ]
        
        all_ok = True
        for name, (ok, msg) in checks:
            print(f"  {msg}")
            if not ok:
                all_ok = False
        
        if not all_ok:
            self.ui.error("Some prerequisites are missing. Please install them first.")
            return False
        
        self.ui.success("All system requirements met!")
        
        # Port configuration
        self.ui.section("2️⃣  Port Configuration")
        default_port = self.config.get("port", 8080)
        
        while True:
            port_str = self.ui.prompt_text(
                "Enter proxy port number",
                default=str(default_port)
            )
            try:
                port = int(port_str)
                if not (1 <= port <= 65535):
                    self.ui.error("Port must be between 1 and 65535")
                    continue
                
                ok, msg = SystemChecker.check_port(port)
                print(f"  {msg}")
                if ok:
                    self.config.set("port", port)
                    break
                else:
                    if self.ui.prompt_confirm("Try different port?", default=True):
                        continue
                    else:
                        break
            except ValueError:
                self.ui.error("Invalid port number")

        self.ui.section("3️⃣  Rotation Settings")
        config = self.config.load()

        rotation_interval = int(self.ui.prompt_text("Rotation interval in seconds", default=str(config.get("rotation_interval", 60))))
        batch_size = int(self.ui.prompt_text("Active proxy batch size", default=str(config.get("proxy_batch_size", 10))))
        worker_count = int(self.ui.prompt_text("Concurrent test workers", default=str(config.get("max_workers", 10))))
        failed_memory = int(self.ui.prompt_text("Dead proxy memory", default=str(config.get("failed_proxy_memory", 20))))
        never_repeat = self.ui.prompt_confirm("Never use the same proxy twice in a row?", default=config.get("never_repeat_proxy", True))

        config["rotation_interval"] = max(5, rotation_interval)
        config["proxy_batch_size"] = max(1, batch_size)
        config["max_workers"] = max(1, worker_count)
        config["failed_proxy_memory"] = max(1, failed_memory)
        config["never_repeat_proxy"] = bool(never_repeat)
        self.config.save(config)

        addon_code = ADDON_TEMPLATE \
            .replace("__ROTATION_INTERVAL__", str(config["rotation_interval"])) \
            .replace("__PROXY_BATCH_SIZE__", str(config["proxy_batch_size"])) \
            .replace("__MAX_WORKERS__", str(config["max_workers"])) \
            .replace("__FAILED_PROXY_MEMORY__", str(config["failed_proxy_memory"])) \
            .replace("__NEVER_REPEAT_PROXY__", str(bool(config["never_repeat_proxy"])))
        
        # Create addon
        self.ui.section("4️⃣  Installing Addon")
        try:
            self.config.addon_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config.addon_file, 'w') as f:
                f.write(addon_code)
            os.chmod(self.config.addon_file, 0o755)
            self.ui.success(f"Addon installed to {self.config.addon_file}")
        except Exception as e:
            self.ui.error(f"Failed to install addon: {e}")
            return False

        proxy_url = f"http://127.0.0.1:{self.config.get('port', 8080)}"
        copied, result = ClipboardHelper.copy_text(proxy_url)
        if copied:
            self.ui.success(f"Proxy URL copied to clipboard: {proxy_url}")
        else:
            self.ui.warning(f"Clipboard unavailable: {result}. You can still paste: {proxy_url}")
        
        # Verify
        self.ui.section("5️⃣  Verification")
        ok, msg = SystemChecker.check_port(self.config.get("port", 8080))
        print(f"  {msg}")
        
        self.ui.success("Setup complete!")
        
        return True

    def auto_run(self) -> bool:
        """Automatic setup with all defaults - no prompts"""
        print("🚀 Auto-configuring NineRouter Autoproxy...")
        
        # System checks
        checks = [
            ("Python Version", SystemChecker.check_python()),
            ("Operating System", SystemChecker.check_os()),
            ("mitmproxy Installation", SystemChecker.check_mitmproxy()),
        ]
        
        all_ok = True
        for name, (ok, msg) in checks:
            print(f"  {msg}")
            if not ok:
                all_ok = False
        
        if not all_ok:
            print("❌ Some prerequisites are missing. Please install them first.")
            return False
        
        # Use defaults
        default_port = 8080
        ok, msg = SystemChecker.check_port(default_port)
        print(f"  Port {default_port}: {msg}")
        
        if not ok:
            print(f"❌ Port {default_port} is not available")
            return False
        
        self.config.set("port", default_port)
        
        # Set default rotation settings
        config = {
            "port": default_port,
            "rotation_interval": 60,
            "proxy_batch_size": 10,
            "max_workers": 10,
            "failed_proxy_memory": 20,
            "never_repeat_proxy": True,
        }
        self.config.save(config)
        
        addon_code = ADDON_TEMPLATE \
            .replace("__ROTATION_INTERVAL__", str(config["rotation_interval"])) \
            .replace("__PROXY_BATCH_SIZE__", str(config["proxy_batch_size"])) \
            .replace("__MAX_WORKERS__", str(config["max_workers"])) \
            .replace("__FAILED_PROXY_MEMORY__", str(config["failed_proxy_memory"])) \
            .replace("__NEVER_REPEAT_PROXY__", str(bool(config["never_repeat_proxy"])))
        
        # Create addon
        try:
            self.config.addon_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config.addon_file, 'w') as f:
                f.write(addon_code)
            os.chmod(self.config.addon_file, 0o755)
            print(f"✅ Addon installed to {self.config.addon_file}")
        except Exception as e:
            print(f"❌ Failed to install addon: {e}")
            return False
        
        proxy_url = f"http://127.0.0.1:{default_port}"
        copied, result = ClipboardHelper.copy_text(proxy_url)
        if copied:
            print(f"✅ Proxy URL copied to clipboard: {proxy_url}")
        else:
            print(f"✅ Proxy URL (copy this): {proxy_url}")
        
        print("✅ Auto-setup complete! Run 'nine-router-autoproxy --run' to start.")
        
        return True


class AdvancedSettings:
    """Edit rotation, proxy, and retry behavior without editing code."""

    def __init__(self, ui: UI, config: Config):
        self.ui = ui
        self.config = config

    def run(self) -> None:
        self.ui.header("⚙️ Advanced Settings")
        settings = self.config.load()

        edited = False
        prompts = {
            "rotation_interval": ("Rotation interval in seconds", int, lambda v: max(5, v)),
            "proxy_batch_size": ("Active proxy batch size", int, lambda v: max(1, v)),
            "max_workers": ("Concurrent test workers", int, lambda v: max(1, v)),
            "failed_proxy_memory": ("Dead proxy memory", int, lambda v: max(1, v)),
            "never_repeat_proxy": ("Never repeat the same proxy twice?", bool, lambda v: bool(v)),
        }

        for key, (label, cast, clean) in prompts.items():
            current = settings.get(key, self.config.default_config.get(key))
            default = str(current)
            value = self.ui.prompt_text(f"{label} [{default}]", default=default)
            try:
                parsed = cast(value)
                settings[key] = clean(parsed)
                edited = True
            except ValueError:
                self.ui.warning(f"Invalid value for {label}; keeping current setting: {current}")

        if edited:
            self.config.save(settings)
            self.ui.success("Advanced settings saved.")
        else:
            self.ui.info("No changes made.")

        self.ui.info("Changes apply on the next setup/run.")


class ProxyRunner:
    """Run the proxy server"""
    
    def __init__(self, ui: UI, config: Config):
        self.ui = ui
        self.config = config
        self.process = None
    
    def run(self) -> None:
        """Start the proxy"""
        port = self.config.get("port", 8080)
        addon_file = str(self.config.addon_file)
        
        if not Path(addon_file).exists():
            self.ui.error(f"Addon file not found: {addon_file}")
            self.ui.info("Run setup first: python3 nine_router_proxy.py --setup")
            return
        
        self.ui.header("🚀 Starting NineRouter Autoproxy")

        proxy_url = f"http://127.0.0.1:{port}"
        copied, result = ClipboardHelper.copy_text(proxy_url)
        if copied:
            self.ui.success(f"Proxy URL copied to clipboard: {proxy_url}")
        else:
            self.ui.warning(f"Clipboard unavailable: {result}. Manual value: {proxy_url}")
        
        self.ui.status_box("Configuration", {
            "Port": str(port),
            "Addon": addon_file,
            "Protocol": "HTTP",
            "Address": "127.0.0.1",
            "Status": "Starting..."
        })
        
        self.ui.info("Press Ctrl+C to stop the proxy\n")
        
        try:
            cmd = [
                "mitmdump",
                "-s", addon_file,
                "-p", str(port),
                "--mode", "regular"
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            proxy_url = f"http://127.0.0.1:{port}"
            self.ui.success(f"Proxy on {proxy_url}")
            self.ui.info("Copy this URL into 9Router or your HTTP proxy settings.")
            
            # Stream output
            for line in self.process.stdout:
                print(line, end='')
            
            self.process.wait()
            
        except FileNotFoundError:
            self.ui.error(ErrorCode.format_error("E002"))
        except KeyboardInterrupt:
            self.ui.warning("\nShutting down...")
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
        except Exception as e:
            self.ui.error(f"Error running proxy: {e}")


class Diagnostics:
    """Run diagnostics"""
    
    def __init__(self, ui: UI, config: Config):
        self.ui = ui
        self.config = config
    
    def run(self) -> None:
        """Run full diagnostics"""
        self.ui.header("🔍 Diagnostics")
        
        self.ui.section("System Information")
        print(f"  OS: {platform.system()} {platform.release()}")
        print(f"  Python: {sys.version}")
        print(f"  Home: {Path.home()}")
        
        self.ui.section("Configuration")
        config = self.config.load()
        for key, value in config.items():
            if key != 'api_url' and key != 'test_endpoints':
                self.ui.info(f"{key}: {value}")
        
        self.ui.section("Checks")
        checks = [
            ("Python", SystemChecker.check_python()),
            ("OS", SystemChecker.check_os()),
            ("mitmproxy", SystemChecker.check_mitmproxy()),
            ("Port", SystemChecker.check_port(self.config.get("port", 8080))),
            ("Internet", SystemChecker.check_internet()),
        ]
        
        for name, (ok, msg) in checks:
            print(f"  {msg}")
        
        self.ui.section("File System")
        print(f"  Config dir: {self.config.config_dir} - {self._exists(self.config.config_dir)}")
        print(f"  Config file: {self.config.config_file} - {self._exists(self.config.config_file)}")
        print(f"  Addon dir: {self.config.addon_dir} - {self._exists(self.config.addon_dir)}")
        print(f"  Addon file: {self.config.addon_file} - {self._exists(self.config.addon_file)}")
        
        self.ui.section("Next Steps")
        self.ui.info("To run the proxy: python3 nine_router_proxy.py --run")
        self.ui.info("To configure 9Router: Set proxy to 127.0.0.1:8080")
    
    @staticmethod
    def _exists(path: Path) -> str:
        """Check if path exists"""
        if path.exists():
            return f"✅ Exists"
        else:
            return f"❌ Not found"


class MainMenu:
    """Main menu interface"""
    
    def __init__(self):
        self.ui = UI()
        self.config = Config()
    
    def show(self) -> None:
        """Show main menu"""
        while True:
            self.ui.header("🚀 NineRouter Autoproxy - Main Menu")

            choice = self.ui.menu(
                "What would you like to do?",
                {
                    "S": "Setup (install & configure)",
                    "R": "Run proxy server",
                    "D": "Run diagnostics",
                    "A": "Advanced settings",
                    "H": "Help & documentation",
                    "Q": "Quit"
                }
            )

            if choice == "S":
                wizard = SetupWizard(self.ui, self.config)
                wizard.run()
            elif choice == "R":
                runner = ProxyRunner(self.ui, self.config)
                runner.run()
            elif choice == "D":
                diag = Diagnostics(self.ui, self.config)
                diag.run()
            elif choice == "A":
                settings = AdvancedSettings(self.ui, self.config)
                settings.run()
            elif choice == "H":
                self._show_help()
            elif choice == "Q":
                self.ui.info("Goodbye!")
                break
            else:
                self.ui.error("Invalid option")
    
    def _show_help(self) -> None:
        """Show help"""
        self.ui.header("📚 Help & Documentation")
        
        help_text = """
QUICK START:
  1. Run Setup wizard: python3 nine_router_proxy.py --setup
  2. Start proxy: python3 nine_router_proxy.py --run
  3. Configure 9Router: Set proxy to 127.0.0.1:8080

PROXY DETAILS:
  • Type: HTTP
  • Address: 127.0.0.1
  • Port: 8080 (configurable)
  • Rotation: Every 60 seconds
  • Upstream proxies: From ProxyScrape API (ACTIVE only)
  • Testing: All proxies tested in parallel before use
  • Fallback: Memory of 20 dead proxies, never repeats consecutive

FEATURES:
  ✅ Auto-rotation every 60 seconds
  ✅ Tests 10 ACTIVE proxies in parallel
  ✅ Picks fastest working proxy
  ✅ Never uses same proxy twice in a row
  ✅ Remembers failed proxies for 20 cycles
  ✅ Graceful fallback if all proxies fail
  ✅ Detailed logging and diagnostics

TROUBLESHOOTING:
  • Can't connect: Check 9Router proxy settings (127.0.0.1:8080)
  • mitmproxy not found: brew install mitmproxy
  • Port in use: Kill process or use different port in setup
  • API timeout: Temporary, will retry next rotation
  • No proxies: Requests pass direct, will recover next rotation

CONFIGURATION:
  • Config: ~/.nine_router/config.json
  • Addon: ~/.mitmproxy/nine_router_autoproxy.py
  • Logs: Visible in proxy terminal output

MORE INFO:
  • Visit: https://github.com/... (your repo)
  • Or run diagnostics: python3 nine_router_proxy.py --setup
"""
        print(help_text)
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    ui = UI()
    config = Config()
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()
        # Handle empty or whitespace-only arguments
        if not arg or arg.startswith('\x00'):
            arg = None
    else:
        arg = None
    
    if arg:
        if arg == "--setup":
            SetupWizard(ui, config).run()
        elif arg == "--auto-setup":
            SetupWizard(ui, config).auto_run()
        elif arg == "--run":
            ProxyRunner(ui, config).run()
        elif arg == "--diag":
            Diagnostics(ui, config).run()
        elif arg in ("--menu", "-m"):
            MainMenu().show()
        elif arg in ("-h", "--help", "help"):
            print("Usage: nine_router_proxy.py [--auto-setup|--setup|--run|--diag|--menu|--help]")
            print("  --auto-setup    Auto-configure with defaults (recommended)")
            print("  --setup         Interactive setup wizard")
            print("  --run           Run proxy directly")
            print("  --diag          Run diagnostics")
            print("  --menu, -m      Show interactive menu")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: nine_router_proxy.py [--auto-setup|--setup|--run|--diag|--menu|--help]")
            sys.exit(1)
    else:
        # If no config exists, auto-setup. Otherwise show menu.
        config_path = config.config_dir / "config.json"
        if not config_path.exists():
            print("No configuration found. Running auto-setup...")
            SetupWizard(ui, config).auto_run()
        else:
            MainMenu().show()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown...")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        sys.exit(1)