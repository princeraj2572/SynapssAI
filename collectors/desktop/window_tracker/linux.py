def get_window() -> str:
    import subprocess
    try:
        wid = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
        name = subprocess.check_output(['xdotool', 'getwindowname', wid]).decode().strip()
        return name
    except Exception as e:
        return f"unknown ({e})"
