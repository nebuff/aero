#!/bin/sh
# update.sh - Update only the Aero binary (no configs or app-list.txt)
set -e

# Download latest aero binary to a temp location
TMP_AERO="/tmp/aero-$$"

# Try to detect OS for binary compatibility (currently only builds from source)
# Download latest aero.c and build
curl -fsSL https://raw.githubusercontent.com/nebuff/aero/refs/heads/main/src/aero.c -o "$TMP_AERO.c"

# Build the binary
cc "$TMP_AERO.c" -o "$TMP_AERO" -lncurses

# Move to /usr/local/bin (requires sudo)
sudo mv "$TMP_AERO" /usr/local/bin/aero
sudo chmod +x /usr/local/bin/aero

# Clean up	rm -f "$TMP_AERO.c"

echo "Aero updated! Run 'aero' to launch."
