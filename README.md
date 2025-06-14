# Aero

Aero is a simple, extensible, and colorful command shell for macOS and Linux, written in Python.  
It supports plugins, user configuration, and a friendly installer.

---

## Features

- Basic shell commands: `ls`, `cd`, `mkdir`, `exit`, `quit`
- Plugin system: install, list, and delete plugins
- Colorful prompt and output (fully configurable)
- User configuration: username, color settings, and more
- Easy installation with our Installer
- Easy Updating with the handy Updater Plugin!

---

## Installation

1. **Install**

   - Download the install.sh script from the Repo

   > Click on the "install.sh" file in files
   >  then Navigate to the "Download raw file" Tab on the top right

   ```sh
   ./~/Downloads/install.sh
   ```

   > **Note:**  
   > The installer will guide you through selecting a version and will set up Aero in `~/aero`.

3. **After install:**

   - Open a **new terminal window** or run:
     ```sh
     source ~/.zshrc
     ```
     or
     ```sh
     source ~/.bashrc
     ```
   - Now you can launch Aero from anywhere by typing:
     ```sh
     aero
     ```

---

## Usage

When you start Aero, you'll see a colorful prompt and a welcome message with your username.

### Built-in Commands

| Command                | Description                       |
|------------------------|-----------------------------------|
| `ls`                   | List files in the current directory |
| `cd [dir]`             | Change directory                  |
| `mkdir <dir>`          | Make a new directory              |
| `exit` or `quit`       | Exit Aero                         |
| `installist`           | List installed and available plugins |
| `install <name>`       | Install a plugin by name          |
| `installdelete <name>` | Delete an installed plugin        |
| `config`               | Show and change configuration     |

---

## Configuration

Aero stores its configuration in `~/aero/config.json`.

You can view and change settings using the `config` command inside Aero:

- Show all config options:
  ```
  config
  ```
- Change your username:
  ```
  config username YourName
  ```
- Turn color on or off:
  ```
  config color on
  config color off
  ```
- Change a color (use ANSI codes, e.g. `\033[35m` for magenta):
  ```
  config color prompt \033[35m
  config color error \033[31m
  ```
- Show the raw config file:
  ```
  config show
  ```

---

## Plugins

- To see available plugins:
  ```
  installist
  ```
- To install a plugin:
  ```
  install <pluginname>
  ```
- To delete a plugin:
  ```
  installdelete <pluginname>
  ```

Plugins are loaded from the `~/aero/plugins` directory at startup.

---

## Troubleshooting

- **Command not found:**  
  Make sure you opened a new terminal window or sourced your shell config after install.
- **Wrong Python version:**  
  The installer sets up Aero to use the correct Python. If you have issues, check your alias in `~/.zshrc` or `~/.bashrc`.
- **Config not saving:**  
  Make sure you have write permissions to `~/aero/config.json`.

---

## Uninstall

To remove Aero, simply delete the `~/aero` directory and remove the `aero` alias from your shell config (`~/.zshrc` or `~/.bashrc`).

---

## License

MIT License

---

## Credits

Aero Installer and Shell by Holden  
See [https://github.com/nebuff/aero](https://github.com/nebuff/aero) for updates.
