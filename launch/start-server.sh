#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="$ROOT/server-26.2"

if [[ ! -f "$SERVER_DIR/paper.jar" ]]; then
  echo "Server not set up yet. First run: python3 launch/setup.py"
  exit 1
fi

cd "$SERVER_DIR"
echo "Starting Eaglercraft Survival SMP on port 25565."
echo "Leave this terminal open while players are connected."
echo "Stop the server with Ctrl+C."
exec java -Xms1G -Xmx3G -jar paper.jar --nogui
