CODING_APPS = [
    "code", "cursor", "pycharm", "intellij", "webstorm", "clion", "rider",
    "sublime text", "vim", "neovim", "nvim", "emacs", "atom",
    "terminal", "cmd", "powershell", "wsl", "bash", "zsh",
    "android studio", "xcode", "visual studio",
]

BROWSER_APPS = ["chrome", "firefox", "edge", "safari", "brave", "opera", "arc"]

COMMUNICATION_APPS = ["slack", "discord", "teams", "zoom", "skype", "telegram", "whatsapp"]

ENTERTAINMENT_APPS = ["vlc", "mpv", "spotify", "netflix", "prime", "steam", "epic games"]

PRODUCTIVITY_APPS = ["notion", "obsidian", "word", "excel", "powerpoint", "pages", "numbers", "figma", "photoshop"]


def categorize_app(app_name: str) -> str:
    a = app_name.lower()
    if any(k in a for k in CODING_APPS):
        return "coding"
    if any(k in a for k in BROWSER_APPS):
        return "browser"
    if any(k in a for k in COMMUNICATION_APPS):
        return "communication"
    if any(k in a for k in ENTERTAINMENT_APPS):
        return "entertainment"
    if any(k in a for k in PRODUCTIVITY_APPS):
        return "productivity"
    return "other"
