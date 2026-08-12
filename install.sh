#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="nine_router_proxy.py"
INSTALL_DIR="${HOME}/.local/bin"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SRC_SCRIPT="${SRC_DIR}/${SCRIPT_NAME}"

WRAPPER_NAME="9router-proxy"
if command -v "${WRAPPER_NAME}" >/dev/null 2>&1; then
  WRAPPER_NAME="nineRouter-autoproxy"
fi

function fail() {
  echo "Error: $1" >&2
  exit 1
}

if [ ! -f "${SRC_SCRIPT}" ]; then
  fail "Source script not found: ${SRC_SCRIPT}. Run this from the repository root."
fi

PYTHON_CMD=""
for candidate in python3 python; do
  if command -v "${candidate}" >/dev/null 2>&1; then
    version="$(${candidate} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
    if [ -n "${version}" ]; then
      major="${version%%.*}"
      minor="${version#*.}"
      if [ "${major}" -gt 3 ] || { [ "${major}" -eq 3 ] && [ "${minor}" -ge 9 ]; }; then
        PYTHON_CMD="${candidate}"
        break
      fi
    fi
  fi
 done

if [ -z "${PYTHON_CMD}" ]; then
  echo "Could not find Python 3.9+. Falling back to install.py if available."
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
  else
    fail "Python 3.9+ is required. Install Python 3.9 or later and retry."
  fi
fi

if [ -z "${PYTHON_CMD}" ]; then
  fail "Python 3.9+ is required. Install Python 3.9 or later and retry."
fi

echo "Using Python: ${PYTHON_CMD}"

echo "Installing runtime dependencies..."
if ! "${PYTHON_CMD}" -m pip install --user requests mitmproxy rich; then
  fail "Dependency installation failed. Ensure pip is available: ${PYTHON_CMD} -m pip install --user requests mitmproxy rich"
fi

mkdir -p "${INSTALL_DIR}"
cp "${SRC_SCRIPT}" "${INSTALL_DIR}/${SCRIPT_NAME}"
chmod +x "${INSTALL_DIR}/${SCRIPT_NAME}"

PYTHON_EXEC="$(command -v "${PYTHON_CMD}")"
cat > "${INSTALL_DIR}/${WRAPPER_NAME}" <<EOF
#!/usr/bin/env bash
exec "${PYTHON_EXEC}" "$HOME/.local/bin/nine_router_proxy.py" "$@"
EOF
chmod +x "${INSTALL_DIR}/${WRAPPER_NAME}"

INSTALL_PATH="${INSTALL_DIR}/${WRAPPER_NAME}"

echo
echo "Installed ${SCRIPT_NAME} and launcher command '${WRAPPER_NAME}' to ${INSTALL_DIR}."

target_dir_in_path=false
IFS=":" read -ra PATH_ENTRIES <<< "${PATH}"
for entry in "${PATH_ENTRIES[@]}"; do
  if [ "${entry}" = "${INSTALL_DIR}" ]; then
    target_dir_in_path=true
    break
  fi
 done

if [ "${target_dir_in_path}" = true ]; then
  echo "${INSTALL_DIR} is already on your PATH."
else
  echo "Add ${INSTALL_DIR} to your PATH so you can run '${WRAPPER_NAME}' from anywhere."
  echo
  echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
  echo
  echo "Add that line to ~/.bashrc, ~/.bash_profile, or ~/.zshrc and open a new shell."
fi

echo
echo "Next steps:" 
echo "  ${WRAPPER_NAME} --setup"
echo "  ${WRAPPER_NAME} --run"
echo "  ${WRAPPER_NAME} --diag"
echo
echo "If '${WRAPPER_NAME}' is not on your PATH yet, run:" 
echo "  python3 \"${INSTALL_DIR}/${SCRIPT_NAME}\" --setup"
echo
echo "Configure 9Router to use HTTP proxy 127.0.0.1:8080 after setup."
