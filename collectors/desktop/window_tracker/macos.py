def get_window() -> str:
    try:
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().activeApplication()
        return app.get('NSApplicationName', 'unknown')
    except Exception as e:
        return f"unknown ({e})"
