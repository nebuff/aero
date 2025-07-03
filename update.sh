#!/bin/sh
# update.sh - Update only the Aero binary (no configs or app-list.txt)
set -e

# Download latest aero binary to a temp location
TMP_AERO="/tmp/aero-$$"

# Download latest aero.c and build
curl -fsSL https://raw.githubusercontent.com/nebuff/aero/refs/heads/main/src/aero.c -o "$TMP_AERO.c"

# Build the binary
cc "$TMP_AERO.c" -o "$TMP_AERO" -lncurses

# Move to /aero (no sudo required if user owns /aero)
mv "$TMP_AERO" /aero/aero
chmod +x /aero/aero

# Clean up
rm -f "$TMP_AERO.c"

echo "Aero updated! Run 'aero' to launch."
