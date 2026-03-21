"use client";

import { Card } from "@/components/ui/card";

export default function ActivitiesPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Activities</h1>
        <p className="text-sm text-muted-foreground mt-2">Track and manage all your activities</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card size="sm">
          <div className="px-6 py-4">
            <h3 className="font-semibold text-foreground">💻 Coding</h3>
            <p className="text-sm text-muted-foreground mt-1">Programming and development time</p>
            <div className="mt-4 text-2xl font-bold text-blue-600">0h</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4">
            <h3 className="font-semibold text-foreground">📖 Reading</h3>
            <p className="text-sm text-muted-foreground mt-1">Learning and reading time</p>
            <div className="mt-4 text-2xl font-bold text-purple-600">0h</div>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4">
            <h3 className="font-semibold text-foreground">🏋️ Exercise</h3>
            <p className="text-sm text-muted-foreground mt-1">Physical activity and fitness</p>
            <div className="mt-4 text-2xl font-bold text-green-600">0h</div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Recent Activities</h2>
          <p className="text-sm text-muted-foreground">No activities logged yet. Start tracking your activities using the desktop agent, browser extension, or manual logging.</p>
        </div>
      </Card>
    </div>
  );
}
