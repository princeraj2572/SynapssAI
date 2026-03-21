"use client";

import { Card } from "@/components/ui/card";

export default function AlertsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Alerts</h1>
        <p className="text-sm text-muted-foreground mt-2">Critical notifications about your wellness and productivity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-3xl mb-2">🚨</p>
            <p className="text-sm font-medium text-foreground">Active Alerts</p>
            <div className="text-2xl font-bold text-red-600 mt-2">0</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-3xl mb-2">⚠️</p>
            <p className="text-sm font-medium text-foreground">Warnings</p>
            <div className="text-2xl font-bold text-yellow-600 mt-2">0</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-3xl mb-2">ℹ️</p>
            <p className="text-sm font-medium text-foreground">Info</p>
            <div className="text-2xl font-bold text-blue-600 mt-2">0</div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Recent Alerts</h2>
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground text-center py-8">No alerts at the moment. You're doing great! 🎉</p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-2">Alert Types</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>🔴 <strong>Burnout Risk</strong> — High workload with low recovery</li>
            <li>🟡 <strong>Sleep Warning</strong> — Insufficient sleep detected</li>
            <li>🟠 <strong>Activity Goal Miss</strong> — Goals not met</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
