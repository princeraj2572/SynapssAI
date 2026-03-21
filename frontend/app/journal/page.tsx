"use client";

import { Card } from "@/components/ui/card";

export default function JournalPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Journal</h1>
        <p className="text-sm text-muted-foreground mt-2">Reflections and notes about your day</p>
      </div>

      <Card>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Today's Entry</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
              + New Entry
            </button>
          </div>
          <p className="text-sm text-muted-foreground">No entries yet. Start your first journal entry to reflect on your day.</p>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Past Entries</h2>
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground text-center py-8">No entries found. Your first journal entry will appear here.</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
