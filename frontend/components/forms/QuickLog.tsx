"use client";
import { useState } from "react";
import { trackEvent } from "@/lib/api";
import { mutate } from "swr";

const QUICK_ACTIONS = [
  { label: "Gym",        activity: "gym",         value: 1 },
  { label: "Mood: Good", activity: "mood",        value: 5 },
  { label: "Mood: OK",   activity: "mood",        value: 3 },
  { label: "Mood: Bad",  activity: "mood",        value: 1 },
  { label: "Water",      activity: "water",       value: 1 },
  { label: "Coffee",     activity: "coffee",      value: 1 },
  { label: "Meal",       activity: "meal",        value: 1 },
  { label: "Sleep 8h",   activity: "sleep",       value: 8 },
];

export default function QuickLog() {
  const [sent, setSent] = useState<string | null>(null);

  const log = async (action: typeof QUICK_ACTIONS[0]) => {
    try {
      await trackEvent({ activity: action.activity, value: action.value, source: "quick_log" });
      setSent(action.label);
      setTimeout(() => setSent(null), 1500);
      mutate("score");
      mutate("daily");
    } catch {
      setSent("Error");
      setTimeout(() => setSent(null), 1500);
    }
  };

  return (
    <div className="card p-8">
      <div className="flex flex-wrap gap-3">
        {QUICK_ACTIONS.map(action => (
          <button
            key={action.label}
            onClick={() => log(action)}
            className="px-4 py-2.5 rounded-lg bg-secondary hover:bg-secondary/80 text-foreground font-medium text-sm transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {action.label}
          </button>
        ))}
      </div>
      {sent && (
        <p className="text-sm text-green-600 dark:text-green-400 mt-4 font-medium">✓ {sent} logged</p>
      )}
    </div>
  );
}
