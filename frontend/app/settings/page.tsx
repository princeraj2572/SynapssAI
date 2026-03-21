"use client";
import { useState } from "react";
import { useActivities } from "@/lib/hooks/useAnalytics";
import { createActivity, getLLMStatus } from "@/lib/api";
import useSWR from "swr";

function useActivitiesData() {
  return useSWR("activities", () => fetch("http://localhost:8080/api/activities").then(r => r.json()), { refreshInterval: 10000 });
}

export default function SettingsPage() {
  const { data: activitiesData, mutate } = useActivitiesData();
  const { data: llmStatus } = useSWR("llm-status", getLLMStatus, { refreshInterval: 30000 });

  const [newActivity, setNewActivity] = useState({ name: "", category: "general", unit: "count" });
  const [adding, setAdding] = useState(false);
  const [msg, setMsg] = useState("");

  const activities = activitiesData || [];

  const handleAdd = async () => {
    if (!newActivity.name.trim()) return;
    setAdding(true);
    try {
      await createActivity(newActivity);
      setMsg(`Activity "${newActivity.name}" added`);
      setNewActivity({ name: "", category: "general", unit: "count" });
      mutate();
    } catch (e: any) {
      setMsg("Error: name may already exist");
    } finally {
      setAdding(false);
      setTimeout(() => setMsg(""), 3000);
    }
  };

  const categories = ["productivity", "health", "nutrition", "mental", "screen", "general"];
  const units = ["hours", "count", "score", "pages", "km", "glasses", "cups", "minutes"];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {/* LLM Status */}
      <div className="card">
        <p className="stat-label mb-3">AI Status</p>
        <div className="flex items-center gap-3">
          <div className={`w-2.5 h-2.5 rounded-full ${llmStatus?.ollama_running ? "bg-green-500" : "bg-red-400"}`} />
          <p className="text-sm text-gray-700">{llmStatus?.message || "Checking..."}</p>
        </div>
        {!llmStatus?.ollama_running && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg font-mono text-xs text-gray-600">
            <p># To start Ollama:</p>
            <p>ollama serve</p>
            <p>ollama pull llama3.1:8b</p>
          </div>
        )}
      </div>

      {/* Add custom trackable */}
      <div className="card">
        <p className="stat-label mb-4">Add custom trackable</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400">Activity name</label>
            <input
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-400"
              placeholder="e.g. meditation"
              value={newActivity.name}
              onChange={e => setNewActivity(p => ({ ...p, name: e.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400">Category</label>
            <select
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-400"
              value={newActivity.category}
              onChange={e => setNewActivity(p => ({ ...p, category: e.target.value }))}
            >
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400">Unit</label>
            <select
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-400"
              value={newActivity.unit}
              onChange={e => setNewActivity(p => ({ ...p, unit: e.target.value }))}
            >
              {units.map(u => <option key={u} value={u}>{u}</option>)}
            </select>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-3">
          <button
            onClick={handleAdd}
            disabled={adding || !newActivity.name.trim()}
            className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
          >
            Add activity
          </button>
          {msg && <p className="text-xs font-medium text-green-600">{msg}</p>}
        </div>
      </div>

      {/* All activities */}
      <div className="card">
        <p className="stat-label mb-4">All trackables ({activities.length})</p>
        <div className="flex flex-col gap-1 max-h-80 overflow-y-auto">
          {activities.map((a: any) => (
            <div key={a.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-800 capitalize">{a.name}</span>
                <span className="text-xs text-gray-400">{a.unit}</span>
                {a.is_auto && <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">auto</span>}
              </div>
              <span className="text-xs text-gray-400 capitalize">{a.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Privacy note */}
      <div className="card border-green-100">
        <p className="stat-label text-green-600 mb-2">Privacy audit</p>
        <div className="text-sm text-gray-600 flex flex-col gap-1">
          <p>✓ All data stored on your machine only</p>
          <p>✓ API runs on localhost — not exposed to internet</p>
          <p>✓ LLM runs locally via Ollama — no cloud calls</p>
          <p>✓ No telemetry or analytics sent anywhere</p>
          <p>✓ No third-party services</p>
        </div>
      </div>
    </div>
  );
}
