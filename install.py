#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def ensure_python_version() -> Path:
    executable = Path(sys.executable)
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        fail("Python 3.9+ is required. Install Python 3.9 or later and rerun this installer.")
    return executable


def get_install_dir() -> Path:
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "NineRouterAutoproxy"
    return Path.home() / ".local" / "bin"


def install_dependencies(python_executable: Path) -> None:
    packages = ["requests", "mitmproxy", "rich"]
    print("Installing runtime dependencies...")
    cmd = [str(python_executable), "-m", "pip", "install", "--user", *packages]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        fail(
            "Failed to install dependencies. Ensure pip is available and retry: "
            f"{python_executable} -m pip install --user {' '.join(packages)}"
        )


def choose_wrapper_name() -> str:
    if shutil.which("9router-proxy") is not None:
        return "nineRouter-autoproxy"
    return "9router-proxy"


def write_wrapper(install_dir: Path, python_executable: Path, script_path: Path) -> str:
    install_dir.mkdir(parents=True, exist_ok=True)
    wrapper_name = choose_wrapper_name()

    if platform.system() == "Windows":
        wrapper_path = install_dir / f"{wrapper_name}.cmd"
        wrapper_content = (
            f"@echo off\n"
            f"\"{python_executable}\" \"{script_path}\" %*\n"
        )
    else:
        wrapper_path = install_dir / wrapper_name
        wrapper_content = (
            "#!/usr/bin/env bash\n"
            f"exec \"{python_executable}\" \"{script_path}\" \"$@\"\n"
        )

    wrapper_path.write_text(wrapper_content, encoding="utf-8")
    if platform.system() != "Windows":
        wrapper_path.chmod(0o755)
    print(f"Created launcher: {wrapper_path}")
    return wrapper_name


def main() -> None:
    python_executable = ensure_python_version()
    repo_dir = Path(__file__).resolve().parent
    source_script = repo_dir / "nine_router_proxy.py"

    if not source_script.exists():
        fail(f"Source script not found: {source_script}. Run this installer from the repository root.")

    install_dir = get_install_dir()
    target_script = install_dir / "nine_router_proxy.py"

    install_dependencies(python_executable)

    install_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_script, target_script)
    target_script.chmod(0o755)
    print(f"Copied {source_script.name} to {target_script}")

    wrapper_name = write_wrapper(install_dir, python_executable, target_script)

    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    in_path = str(install_dir) in path_entries

    print("\nInstallation complete.")
    if in_path:
        print(f"{install_dir} is on your PATH. You can now run: {wrapper_name}")
    else:
        print(f"Add {install_dir} to your PATH to run the command from anywhere.")
        print("For example:")
        if platform.system() == "Windows":
            print(f"  setx PATH \"%PATH%;{install_dir}\"")
        else:
            print(f"  export PATH=\"{install_dir}:$PATH\"")
        print("Then open a new shell.")

    if platform.system() == "Windows":
        launcher_cmd = f"{wrapper_name}.cmd"
        print("\nRun the command:")
        print(f"  {launcher_cmd} --setup")
        print("Or use the full path if PATH is not updated:")
        print(f"  \"{install_dir / launcher_cmd}\" --setup")
    else:
        launcher_cmd = wrapper_name
        print("\nRun the command:")
        print(f"  {launcher_cmd} --setup")
        print("If PATH is not updated, run:")
        print(f"  \"{install_dir / launcher_cmd}\" --setup")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled.")
        sys.exit(1)
