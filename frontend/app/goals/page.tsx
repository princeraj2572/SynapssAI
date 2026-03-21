"use client";

import { Card } from "@/components/ui/card";

export default function GoalsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Goals</h1>
        <p className="text-sm text-muted-foreground mt-2">Set and track your personal goals</p>
      </div>

      <Card>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Active Goals</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
              + Create Goal
            </button>
          </div>
          <p className="text-sm text-muted-foreground">No goals created yet. Start by creating your first goal.</p>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Completed Goals</h2>
          <p className="text-sm text-muted-foreground">Your completed goals will appear here.</p>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-2">Goal Categories</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
            {["Health", "Learning", "Work", "Personal"].map((cat) => (
              <div key={cat} className="p-3 rounded-lg border border-border hover:bg-secondary cursor-pointer transition-colors text-center">
                <p className="text-sm font-medium text-foreground">{cat}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
