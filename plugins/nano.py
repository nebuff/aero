import os

def nano_cmd(args):
    if not args:
        print("nano: missing filename")
        return
    filename = args[0]
    editor = os.environ.get("EDITOR", "nano")
    try:
        os.system(f'{editor} "{filename}"')
    except Exception as e:
        print(f"nano: {e}")

def register(commands):
    commands["nano"] = nano_cmd
