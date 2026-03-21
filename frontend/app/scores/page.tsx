"use client";

import { Card } from "@/components/ui/card";

export default function ScoresPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Scores</h1>
        <p className="text-sm text-muted-foreground mt-2">Your daily productivity and wellness scores</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-sm text-muted-foreground mb-2">Today</p>
            <div className="text-4xl font-bold text-blue-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">/100</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-sm text-muted-foreground mb-2">Week</p>
            <div className="text-4xl font-bold text-green-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Average</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-sm text-muted-foreground mb-2">Month</p>
            <div className="text-4xl font-bold text-purple-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Average</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4 text-center">
            <p className="text-sm text-muted-foreground mb-2">Streak</p>
            <div className="text-4xl font-bold text-orange-600">0</div>
            <p className="text-xs text-muted-foreground mt-2">Days</p>
          </div>
        </Card>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Score Composition</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-foreground">Productivity</span>
              <div className="w-32 bg-gray-200 rounded h-2"></div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-foreground">Wellness</span>
              <div className="w-32 bg-gray-200 rounded h-2"></div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-foreground">Balance</span>
              <div className="w-32 bg-gray-200 rounded h-2"></div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
