"use client";

import { useState } from "react";
import { useGoals } from "@/lib/hooks/useAnalytics";
import { createGoal, updateGoal, deleteGoal } from "@/lib/api";
import useSWR from "swr";
import { Card } from "@/components/ui/card";
import { Plus, Trash2, CheckCircle, Clock } from "lucide-react";

export default function GoalsPage() {
  const { data: goalsData, mutate } = useSWR("goals", () => fetch("http://localhost:8080/api/goals").then(r => r.json()), { refreshInterval: 60000 });
  const [showForm, setShowForm] = useState(false);
  const [newGoal, setNewGoal] = useState({ title: "", description: "", category: "health", target_date: "", priority: "medium" });
  const [creating, setCreating] = useState(false);
  const [msg, setMsg] = useState("");

  const goals = goalsData || [];
  const activeGoals = goals.filter((g: any) => !g.completed);
  const completedGoals = goals.filter((g: any) => g.completed);

  const handleCreate = async () => {
    if (!newGoal.title.trim()) return;
    setCreating(true);
    try {
      await createGoal(newGoal);
      setMsg("✅ Goal created!");
      setNewGoal({ title: "", description: "", category: "health", target_date: "", priority: "medium" });
      setShowForm(false);
      mutate();
    } catch (e: any) {
      setMsg("❌ Error creating goal");
    } finally {
      setCreating(false);
      setTimeout(() => setMsg(""), 3000);
    }
  };

  const handleComplete = async (id: number) => {
    try {
      await updateGoal(id, { completed: true });
      mutate();
    } catch (e) {
      setMsg("❌ Error updating goal");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteGoal(id);
      mutate();
    } catch (e) {
      setMsg("❌ Error deleting goal");
    }
  };

  const categories = ["health", "productivity", "learning", "financial", "personal", "social"];
  const priorities = [
    { value: "low", label: "Low", color: "bg-blue-100 text-blue-700" },
    { value: "medium", label: "Medium", color: "bg-yellow-100 text-yellow-700" },
    { value: "high", label: "High", color: "bg-red-100 text-red-700" },
  ];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Goals</h1>
        <p className="text-sm text-muted-foreground mt-2">Set and track your personal goals</p>
      </div>

      {msg && (
        <div className="p-4 rounded-lg bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm">
          {msg}
        </div>
      )}

      {/* Create Goal Form */}
      {showForm && (
        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Create New Goal</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Goal title (e.g., Run 3x per week)"
                value={newGoal.title}
                onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                className="col-span-1 md:col-span-2 border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              />
              <textarea
                placeholder="Description (optional)"
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                className="col-span-1 md:col-span-2 border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
                rows={3}
              />
              <select
                value={newGoal.category}
                onChange={(e) => setNewGoal({ ...newGoal, category: e.target.value })}
                className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
              <select
                value={newGoal.priority}
                onChange={(e) => setNewGoal({ ...newGoal, priority: e.target.value })}
                className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              >
                {priorities.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
              <input
                type="date"
                value={newGoal.target_date}
                onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
                className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              />
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreate}
                disabled={creating || !newGoal.title.trim()}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
              >
                <Plus size={18} />
                Create Goal
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-6 py-2 rounded-lg text-sm font-semibold border border-border hover:bg-muted transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </Card>
      )}

      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors w-fit"
        >
          <Plus size={18} />
          Create Goal
        </button>
      )}

      {/* Active Goals */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Clock size={20} className="text-blue-600" />
          <h2 className="text-xl font-bold text-foreground">Active Goals ({activeGoals.length})</h2>
        </div>
        {activeGoals.length === 0 ? (
          <Card>
            <div className="p-8 flex items-center justify-center text-center">
              <p className="text-muted-foreground">No active goals yet. Create one to get started!</p>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {activeGoals.map((goal: any) => (
              <Card key={goal.id} className="p-6 border-l-4 border-l-blue-600">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-foreground">{goal.title}</h3>
                    {goal.description && <p className="text-sm text-muted-foreground mt-1">{goal.description}</p>}
                  </div>
                  <button
                    onClick={() => handleDelete(goal.id)}
                    className="text-red-600 hover:text-red-700 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-4 flex-wrap">
                  <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 px-2 py-1 rounded capitalize font-medium">
                    {goal.category}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded font-medium ${priorities.find(p => p.value === goal.priority)?.color}`}>
                    {goal.priority}
                  </span>
                  {goal.target_date && (
                    <span className="text-xs text-muted-foreground">Due: {new Date(goal.target_date).toLocaleDateString()}</span>
                  )}
                </div>
                <button
                  onClick={() => handleComplete(goal.id)}
                  className="mt-4 w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                >
                  <CheckCircle size={16} />
                  Mark Complete
                </button>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Completed Goals */}
      {completedGoals.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={20} className="text-green-600" />
            <h2 className="text-xl font-bold text-foreground">Completed Goals ({completedGoals.length})</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {completedGoals.map((goal: any) => (
              <Card key={goal.id} className="p-6 opacity-75 border-l-4 border-l-green-600">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground line-through">{goal.title}</h3>
                    {goal.description && <p className="text-sm text-muted-foreground mt-1">{goal.description}</p>}
                  </div>
                  <button
                    onClick={() => handleDelete(goal.id)}
                    className="text-red-600 hover:text-red-700 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-4 flex-wrap">
                  <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 px-2 py-1 rounded capitalize font-medium">
                    ✓ Completed
                  </span>
                  <span className={`text-xs px-2 py-1 rounded font-medium ${priorities.find(p => p.value === goal.priority)?.color}`}>
                    {goal.priority}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
