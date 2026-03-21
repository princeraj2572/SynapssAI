// Personal Life OS — Browser Extension Background Service Worker
// Tracks active tab URL + time spent, sends to local API every 30 seconds

const API_URL = "http://localhost:8080/api/track/batch";
const SEND_INTERVAL_SECS = 30;
const MIN_SESSION_SECS = 5;

let currentTab = null;
let sessionStart = Date.now();
let eventBuffer = [];
let enabled = true;

// ── Domain categories ──────────────────────────────────────────
const DOMAIN_CATEGORIES = {
  // Coding
  "github.com": "coding", "gitlab.com": "coding", "stackoverflow.com": "coding",
  "leetcode.com": "coding", "codeforces.com": "coding", "codepen.io": "coding",
  "replit.com": "coding", "codesandbox.io": "coding", "npmjs.com": "coding",
  "developer.mozilla.org": "coding", "docs.python.org": "coding",
  // Learning
  "coursera.org": "learning", "udemy.com": "learning", "edx.org": "learning",
  "khanacademy.org": "learning", "freecodecamp.org": "learning",
  "youtube.com": "learning",
  // Social / Distraction
  "twitter.com": "social", "x.com": "social", "instagram.com": "social",
  "facebook.com": "social", "reddit.com": "social", "tiktok.com": "social",
  // Communication
  "mail.google.com": "communication", "outlook.com": "communication",
  "slack.com": "communication", "discord.com": "communication",
  "web.whatsapp.com": "communication",
  // Productivity
  "notion.so": "productivity", "trello.com": "productivity",
  "linear.app": "productivity", "figma.com": "productivity",
  "docs.google.com": "productivity",
};

function getDomain(url) {
  try {
    return new URL(url).hostname.replace("www.", "");
  } catch {
    return null;
  }
}

function categorize(domain) {
  if (!domain) return "browsing";
  return DOMAIN_CATEGORIES[domain] || "browsing";
}

function categoryToActivity(category, domain) {
  const map = {
    coding: "coding_auto",
    learning: "browser_learning",
    social: "social_media",
    communication: "communication",
    productivity: "browser_productivity",
    browsing: "browser_time",
  };
  return map[category] || "browser_time";
}

function closeSession(tab, endTime) {
  if (!tab || !tab.url) return;
  const domain = getDomain(tab.url);
  if (!domain || domain === "newtab") return;

  const durationSecs = (endTime - sessionStart) / 1000;
  if (durationSecs < MIN_SESSION_SECS) return;

  const category = categorize(domain);
  const activity = categoryToActivity(category, domain);
  const hours = parseFloat((durationSecs / 3600).toFixed(4));

  eventBuffer.push({
    activity,
    value: hours,
    start: new Date(sessionStart).toISOString(),
    end: new Date(endTime).toISOString(),
    source: "browser_extension",
    notes: `${domain}: ${(tab.title || "").slice(0, 80)}`,
  });
}

// ── Tab listeners ──────────────────────────────────────────────
chrome.tabs.onActivated.addListener(async (info) => {
  if (!enabled) return;
  const now = Date.now();
  closeSession(currentTab, now);
  try {
    const tab = await chrome.tabs.get(info.tabId);
    currentTab = tab;
    sessionStart = now;
  } catch {
    currentTab = null;
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (!enabled) return;
  if (changeInfo.status !== "complete") return;
  if (currentTab && currentTab.id === tabId) {
    const now = Date.now();
    closeSession(currentTab, now);
    currentTab = tab;
    sessionStart = now;
  }
});

chrome.windows.onFocusChanged.addListener((windowId) => {
  if (!enabled) return;
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    closeSession(currentTab, Date.now());
    currentTab = null;
  }
});

// ── Periodic sender ────────────────────────────────────────────
chrome.alarms.create("send_events", { periodInMinutes: SEND_INTERVAL_SECS / 60 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "send_events") return;
  if (eventBuffer.length === 0) return;

  const toSend = [...eventBuffer];
  eventBuffer = [];

  try {
    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ events: toSend }),
    });
    if (!resp.ok) {
      eventBuffer.unshift(...toSend);
    }
  } catch {
    // API not running — keep events for next attempt
    eventBuffer.unshift(...toSend);
  }
});

// ── Message from popup ─────────────────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "GET_STATUS") {
    sendResponse({ enabled, buffered: eventBuffer.length, currentDomain: getDomain(currentTab?.url) });
  }
  if (msg.type === "TOGGLE") {
    enabled = !enabled;
    sendResponse({ enabled });
  }
});
