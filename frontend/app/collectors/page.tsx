"use client";

import { Card } from "@/components/ui/card";

export default function CollectorsPage() {
  const collectors = [
    {
      name: "Desktop Agent",
      icon: "💻",
      status: "inactive",
      description: "Tracks active window and time spent on applications",
      docs: "Start the agent with: python collectors/desktop/agent.py"
    },
    {
      name: "Browser Extension",
      icon: "🌐",
      status: "inactive",
      description: "Captures visited websites and time spent browsing",
      docs: "Load extension from: collectors/browser-extension/"
    },
    {
      name: "Git Scanner",
      icon: "📝",
      status: "inactive",
      description: "Monitors Git commits and coding activity",
      docs: "Run with: python collectors/git-scanner/scanner.py"
    },
    {
      name: "Wearable Sync",
      icon: "⌚",
      status: "inactive",
      description: "Syncs health data from wearables and fitness trackers",
      docs: "Coming soon"
    }
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Data Collectors</h1>
        <p className="text-sm text-muted-foreground mt-2">Manage automatic data collection from your devices</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {collectors.map((collector, idx) => (
          <Card key={idx} size="sm">
            <div className="px-6 py-4">
              <div className="flex items-start justify-between mb-2">
                <span className="text-2xl">{collector.icon}</span>
                <span className="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                  {collector.status}
                </span>
              </div>
              <h3 className="font-semibold text-foreground">{collector.name}</h3>
              <p className="text-xs text-muted-foreground mt-2">{collector.description}</p>
              <p className="text-xs text-muted-foreground mt-3 bg-muted/50 p-2 rounded">
                {collector.docs}
              </p>
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-2">Privacy First</h2>
          <p className="text-sm text-muted-foreground">All data collectors run locally on your machine. No data is ever sent to external servers.</p>
        </div>
      </Card>
    </div>
  );
}
