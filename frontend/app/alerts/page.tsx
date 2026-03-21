"use client";

import { Card } from "@/components/ui/card";
import { AlertCircle, AlertTriangle, Info } from "lucide-react";

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
            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-red-600" />
            <p className="text-sm font-medium text-foreground">Active Alerts</p>
            <div className="text-2xl font-bold text-red-600 mt-2">0</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
            <p className="text-sm font-medium text-foreground">Warnings</p>
            <div className="text-2xl font-bold text-yellow-600 mt-2">0</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <Info className="w-8 h-8 mx-auto mb-2 text-blue-600" />
            <p className="text-sm font-medium text-foreground">Info</p>
            <div className="text-2xl font-bold text-blue-600 mt-2">0</div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Recent Alerts</h2>
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground text-center py-8">No alerts at the moment. You're doing well!</p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-2">Alert Types</h2>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <AlertCircle size={16} className="text-red-600" />
              <span><strong>Burnout Risk</strong> — High workload with low recovery</span>
            </li>
            <li className="flex items-center gap-2">
              <AlertTriangle size={16} className="text-yellow-600" />
              <span><strong>Sleep Warning</strong> — Insufficient sleep detected</span>
            </li>
            <li className="flex items-center gap-2">
              <Info size={16} className="text-blue-600" />
              <span><strong>Activity Goal Miss</strong> — Goals not met</span>
            </li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
