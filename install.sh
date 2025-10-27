#!/bin/bash

REPO_URL="https://github.com/nebuff/aero.git"
INSTALL_DIR="$HOME/aero"
VERSIONS_DIR="$INSTALL_DIR/versions"
AERO_TMP="/tmp/aero_tmp_exec"

clear
echo "Aero Installer <-> By Nebuff"
echo
echo "Using Python: $(detect_python)"

# Prevent running from inside the install directory
case "$PWD" in
    "$INSTALL_DIR"*)
        echo "Please run this installer from outside the $INSTALL_DIR directory."
        exit 1
        ;;
esac

# Function to detect Python
detect_python() {
    local python_cmd=""
    
    # Try different Python commands in order of preference
    for cmd in python3 python python3.13 python3.12 python3.11 python3.10; do
        if command -v "$cmd" >/dev/null 2>&1; then
            python_cmd="$cmd"
            break
        fi
    done
    
    if [ -z "$python_cmd" ]; then
        echo "Python not found. Please install Python 3.x first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Verify Python version is 3.x
    if ! "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info.major == 3 else 1)" 2>/dev/null; then
        echo "Python 3.x is required. Found: $($python_cmd --version 2>&1)"
        exit 1
    fi
    
    echo "$python_cmd"
}

# Function to clone and list versions
list_versions() {
    echo "Cloning into '$INSTALL_DIR'..."
    if [ -d "$INSTALL_DIR" ]; then
        echo "Removing existing directory: $INSTALL_DIR"
        rm -rf "$INSTALL_DIR"
    fi
    # Clone the repository
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    
    # Fetch all tags to list versions
    (cd "$INSTALL_DIR" && git fetch --tags > /dev/null 2>&1)
    
    # Extract tags and categorize
    TAGS=$(git -C "$INSTALL_DIR" tag -l --sort=-v:refname)
    
    PRE_RELEASE=()
    BETA=()
    STABLE=()
    
    for tag in $TAGS; do
        if [[ "$tag" == aero-pre-* ]]; then
            PRE_RELEASE+=("$tag")
        elif [[ "$tag" == aero-beta-* ]]; then
            BETA+=("$tag")
        elif [[ "$tag" == aero-stable-* ]]; then
            STABLE+=("$tag")
        fi
    done
    
    # Print the lists
    echo
    echo "- Pre Release -"
    for v in "${PRE_RELEASE[@]}"; do echo "$v"; done
    
    echo
    echo "- Beta -"
    for v in "${BETA[@]}"; do echo "$v"; done
    
    echo
    echo "- Stables (Recomended) -"
    for v in "${STABLE[@]}"; do echo "$v"; done
    echo
}

# Function to handle version selection
select_version() {
    local selected_version
    local tags
    
    tags=$(git -C "$INSTALL_DIR" tag -l)

    while true; do
        # --- MODIFIED PROMPT ---
        echo "Type the version you want to install (e.g. aero-stable-1.0) or press ENTER for latest Main Branch:"
        read -r selected_version
        
        # --- NEW LOGIC: Install Main Branch ---
        if [ -z "$selected_version" ] || [ "$selected_version" == "aero" ]; then
            echo "Installing latest version from Main Branch..."
            # The files are already cloned in $INSTALL_DIR, we just need to move aero.py
            # The name of the file to run the shell is 'aero.py' in the main branch
            if [ -f "$INSTALL_DIR/aero.py" ]; then
                # Move the executable into a temporary file for processing
                mv "$INSTALL_DIR/aero.py" "$AERO_TMP"
                echo "Successfully selected latest Main Branch."
                return 0
            else
                echo "Error: aero.py not found in the cloned repository root. Cannot install Main Branch."
                exit 1
            fi
        # --- Existing Tag Logic ---
        elif echo "$tags" | grep -q "^$selected_version$"; then
            echo "Installing version $selected_version..."
            
            # Checkout the specific version tag
            (cd "$INSTALL_DIR" && git checkout "$selected_version" > /dev/null 2>&1)
            
            # Check for the existence of the aero.py in the checked out tag
            if [ -f "$INSTALL_DIR/aero.py" ]; then
                 # Move the executable into a temporary file for processing
                mv "$INSTALL_DIR/aero.py" "$AERO_TMP"
                return 0
            else
                echo "Error: aero.py not found in the tag '$selected_version'. Reverting to main."
                (cd "$INSTALL_DIR" && git checkout main > /dev/null 2>&1)
                continue
            fi
        else
            echo "Version not found."
            # The list of versions is already shown, so we just ask again
        fi
    done
}

# Function to add $HOME/aero to PATH
add_to_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    local path_to_add="$INSTALL_DIR"
    local export_line
    local source_line

    if [ "$shell_type" == "fish" ]; then
        # Fish uses set -gx and does not use source ~/.profile
        export_line="set -gx PATH \$HOME/aero \$PATH"
    else
        # POSIX compliant (bash/zsh)
        export_line="export PATH=\$HOME/aero:\$PATH"
        source_line="# Source Aero completion scripts here if they exist"
    fi

    echo
    echo "--- Updating $config_file ---"

    if grep -q "# Aero Shell Path" "$config_file"; then
        echo "Aero PATH already configured in $config_file."
    else
        echo "Adding Aero PATH to $config_file..."
        {
            echo ""
            echo "# Aero Shell Path"
            echo "$export_line"
            if [ "$shell_type" != "fish" ]; then
                echo "$source_line"
            fi
        } >> "$config_file"
        echo "Updated."
    fi
}

# --- Main Execution Flow ---

# 1. Detect Python
PYTHON_CMD=$(detect_python)
echo "Python: $PYTHON_CMD"

# 2. Clone and List Versions
list_versions

# 3. Select Version (NEW LOGIC)
select_version

# 4. Prepare the final executable
# The executable is now in $AERO_TMP
# We check the shebang and prepend it if missing
if ! head -n 1 "$AERO_TMP" | grep -q "#!/"; then
    echo "#!$PYTHON_CMD" | cat - "$AERO_TMP" > "$AERO_TMP.new"
    mv "$AERO_TMP.new" "$AERO_TMP"
    echo "Added shebang to executable."
fi
# The new logic copies the main code file (aero.py) to a temp location.
# The core library is in $INSTALL_DIR/lib.

# Move executable back and rename to 'aero'
mv "$AERO_TMP" "$INSTALL_DIR/aero"
chmod +x "$INSTALL_DIR/aero"

echo
echo "Aero installed in $INSTALL_DIR as 'aero'."
echo "You can run it with: $INSTALL_DIR/aero"
echo

# Add to shell configurations
for config in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$config" ] || [ "$config" = "$HOME/.bashrc" ] || [ "$config" = "$HOME/.zshrc" ]; then
        add_to_shell_config "$config" "posix"
    fi
done

# Handle Fish shell configuration
if command -v fish >/dev/null 2>&1; then
    FISH_CONFIG="$HOME/.config/fish/config.fish"
    mkdir -p "$(dirname "$FISH_CONFIG")"
    add_to_shell_config "$FISH_CONFIG" "fish"
fi

# Export PATH for current session
export PATH="$HOME/aero:$PATH"

# Try to source the appropriate config for current shell
if [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.zshrc" 2>/dev/null || true
elif [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.bashrc" 2>/dev/null || true
fi

echo "Reloaded shell configuration. Please open a new terminal or run 'source ~/.bashrc' (or ~/.zshrc) to use 'aero' directly."
echo "Installation Complete!"
