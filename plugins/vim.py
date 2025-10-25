__PLUGIN_VERSION__ = "1.0.0"

def vim_cmd(args):
    import os
    if not args:
        print("vim: missing filename")
        return
    filename = args[0]
    editor = os.environ.get("EDITOR", "vim")
    try:
        os.system(f'{editor} "{filename}"')
    except Exception as e:
        print(f"vim: {e}")

def vim_help(args=None):
    print("vim <filename>")
    print("  Open <filename> in Vim (or $EDITOR if set).")

def register(COMMANDS):
    COMMANDS["vim"] = vim_cmd
    COMMANDS["help_vim"] = vim_help
