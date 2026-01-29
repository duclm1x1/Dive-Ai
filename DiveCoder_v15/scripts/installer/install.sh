#!/usr/bin/env bash
set -euo pipefail

DIVE_BASE_URL="${DIVE_BASE_URL:-https://aicoding.io.vn/v1}"
INSTALL_DIR="${HOME}/.dive/bin"
CONFIG_DIR="${HOME}/.config/dive"
CONFIG_PATH="${CONFIG_DIR}/config.json"

mkdir -p "${INSTALL_DIR}" "${CONFIG_DIR}"

cat > "${INSTALL_DIR}/dive" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(pwd)"
python3 "${REPO_ROOT}/.shared/vibe-coder-v13/vibe.py" "$@"
EOF
chmod +x "${INSTALL_DIR}/dive"

cat > "${CONFIG_PATH}" <<EOF
{
  "provider": "openai-compatible",
  "base_url": "${DIVE_BASE_URL}",
  "api_key": "<set-via-env:DIVE_API_KEY>",
  "model": "claude-sonnet-4-5-20250929"
}
EOF

echo ""
echo "Installed shim: ${INSTALL_DIR}/dive"
echo "Config written: ${CONFIG_PATH}"
echo ""
echo "Next:"
echo "  1) export DIVE_API_KEY=YOUR_KEY"
echo "  2) export PATH=\"${INSTALL_DIR}:$PATH\""
echo "  3) dive doctor --repo ."
