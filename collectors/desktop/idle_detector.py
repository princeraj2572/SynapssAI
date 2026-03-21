import time

_last_input = time.time()

try:
    from pynput import mouse, keyboard

    def on_activity(*args):
        global _last_input
        _last_input = time.time()

    mouse.Listener(on_move=on_activity, on_click=on_activity).start()
    keyboard.Listener(on_press=on_activity).start()
except ImportError:
    pass  # pynput not installed — idle detection disabled

def is_idle(threshold_seconds: int) -> bool:
    return (time.time() - _last_input) > threshold_seconds
