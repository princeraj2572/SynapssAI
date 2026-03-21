"use client";

import { Card } from "@/components/ui/card";
import { Moon, Smile, Heart, Zap } from "lucide-react";

export default function WellnessPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Wellness</h1>
        <p className="text-sm text-muted-foreground mt-2">Monitor your health and well-being</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card size="sm">
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-2">
              <Moon className="w-5 h-5 text-indigo-600" />
              <h3 className="font-semibold text-foreground">Sleep Quality</h3>
            </div>
            <div className="mt-4 text-3xl font-bold text-indigo-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Hours tracked</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-2">
              <Smile className="w-5 h-5 text-pink-600" />
              <h3 className="font-semibold text-foreground">Mood</h3>
            </div>
            <div className="mt-4 text-3xl font-bold text-pink-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Today's rating</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-2">
              <Heart className="w-5 h-5 text-red-600" />
              <h3 className="font-semibold text-foreground">Health</h3>
            </div>
            <div className="mt-4 text-3xl font-bold text-red-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Status</p>
          </div>
        </Card>

        <Card size="sm">
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-5 h-5 text-yellow-600" />
              <h3 className="font-semibold text-foreground">Energy</h3>
            </div>
            <div className="mt-4 text-3xl font-bold text-yellow-600">--</div>
            <p className="text-xs text-muted-foreground mt-2">Energy level</p>
          </div>
        </Card>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Wellness Insights</h2>
          <p className="text-sm text-muted-foreground">Start logging your sleep, mood, and health metrics to see insights about your wellness patterns.</p>
        </div>
      </Card>
    </div>
  );
}
