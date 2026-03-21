function refresh() {
  chrome.runtime.sendMessage({ type: "GET_STATUS" }, (res) => {
    if (!res) return;
    const el = document.getElementById("status");
    el.textContent = res.enabled ? "Tracking" : "Paused";
    el.className = "pill " + (res.enabled ? "on" : "off");
    document.getElementById("domain").textContent = res.currentDomain || "—";
    document.getElementById("buffered").textContent = res.buffered;
  });
}

document.getElementById("toggle").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "TOGGLE" }, () => refresh());
});

refresh();
