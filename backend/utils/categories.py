# Domain → category mapping for browser extension
DOMAIN_CATEGORIES = {
    # Coding / Dev
    "github.com": "coding",
    "gitlab.com": "coding",
    "stackoverflow.com": "coding",
    "leetcode.com": "coding",
    "codeforces.com": "coding",
    "codepen.io": "coding",
    "replit.com": "coding",
    "codesandbox.io": "coding",
    "developer.mozilla.org": "coding",
    "docs.python.org": "coding",
    "npmjs.com": "coding",
    "pypi.org": "coding",

    # Learning
    "coursera.org": "learning",
    "udemy.com": "learning",
    "edx.org": "learning",
    "khanacademy.org": "learning",
    "freecodecamp.org": "learning",
    "codecademy.com": "learning",
    "youtube.com": "learning",   # refined by title NLP later

    # Distraction / Social
    "twitter.com": "social",
    "x.com": "social",
    "instagram.com": "social",
    "facebook.com": "social",
    "reddit.com": "social",
    "tiktok.com": "social",
    "snapchat.com": "social",

    # Communication
    "mail.google.com": "communication",
    "outlook.com": "communication",
    "slack.com": "communication",
    "discord.com": "communication",
    "web.whatsapp.com": "communication",
    "telegram.org": "communication",

    # Productivity
    "notion.so": "productivity",
    "trello.com": "productivity",
    "linear.app": "productivity",
    "figma.com": "productivity",
    "docs.google.com": "productivity",
}

APP_CATEGORIES = {
    # Coding
    "code": "coding",
    "cursor": "coding",
    "pycharm": "coding",
    "intellij": "coding",
    "webstorm": "coding",
    "sublime text": "coding",
    "vim": "coding",
    "neovim": "coding",
    "terminal": "coding",
    "cmd": "coding",
    "powershell": "coding",
    "wsl": "coding",
    "git": "coding",
    "postman": "coding",

    # Browser
    "chrome": "browser",
    "firefox": "browser",
    "edge": "browser",
    "safari": "browser",
    "brave": "browser",

    # Communication
    "slack": "communication",
    "discord": "communication",
    "teams": "communication",
    "zoom": "communication",
    "outlook": "communication",
    "thunderbird": "communication",

    # Entertainment
    "vlc": "entertainment",
    "netflix": "entertainment",
    "spotify": "entertainment",

    # Productivity
    "notion": "productivity",
    "obsidian": "productivity",
    "word": "productivity",
    "excel": "productivity",
}


def categorize_domain(domain: str) -> str:
    domain = domain.lower().replace("www.", "")
    return DOMAIN_CATEGORIES.get(domain, "browsing")


def categorize_app(app_name: str) -> str:
    app_lower = app_name.lower()
    for key, cat in APP_CATEGORIES.items():
        if key in app_lower:
            return cat
    return "other"
