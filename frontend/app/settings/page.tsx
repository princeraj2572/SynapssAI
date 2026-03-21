"use client";
import { useState } from "react";
import { useActivities } from "@/lib/hooks/useAnalytics";
import { createActivity, getLLMStatus, getExportStats, exportJSON, exportSQL, createBackup } from "@/lib/api";
import useSWR from "swr";
import { CheckCircle, AlertCircle, Plus, Download, Database, Archive } from "lucide-react";
import { useExportStats } from "@/lib/hooks/useAnalytics";

function useActivitiesData() {
  return useSWR("activities", () => fetch("http://localhost:8080/api/activities").then(r => r.json()), { refreshInterval: 10000 });
}

export default function SettingsPage() {
  const { data: activitiesData, mutate } = useActivitiesData();
  const { data: llmStatus } = useSWR("llm-status", getLLMStatus, { refreshInterval: 30000 });
  const { data: exportStats } = useExportStats();

  const [newActivity, setNewActivity] = useState({ name: "", category: "general", unit: "count" });
  const [adding, setAdding] = useState(false);
  const [msg, setMsg] = useState("");
  const [exporting, setExporting] = useState<string | null>(null);
  const [exportMsg, setExportMsg] = useState("");

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

  const handleExport = async (format: "json" | "sql" | "backup") => {
    setExporting(format);
    try {
      let data: any;
      let filename = "";
      
      if (format === "json") {
        data = await exportJSON();
        filename = `personal-life-os-export-${new Date().toISOString().split("T")[0]}.json`;
      } else if (format === "sql") {
        data = await exportSQL();
        filename = `personal-life-os-export-${new Date().toISOString().split("T")[0]}.sql`;
      } else {
        data = await createBackup();
        setExportMsg("✅ Full backup created with all formats!");
        setTimeout(() => setExportMsg(""), 3000);
        return;
      }

      // Convert to blob and download
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);

      setExportMsg(`✅ ${format.toUpperCase()} exported successfully!`);
      setTimeout(() => setExportMsg(""), 3000);
    } catch (e: any) {
      setExportMsg(`❌ Export failed: ${e.message}`);
      setTimeout(() => setExportMsg(""), 3000);
    } finally {
      setExporting(null);
    }
  };

  const categories = ["productivity", "health", "nutrition", "mental", "screen", "general"];
  const units = ["hours", "count", "score", "pages", "km", "glasses", "cups", "minutes"];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-2">Configure your Personal Life OS</p>
      </div>

      {/* LLM Status */}
      <div className="card p-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground">AI Coach Status</h2>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${llmStatus?.ollama_running ? "bg-green-100 dark:bg-green-900" : "bg-red-100 dark:bg-red-900"}`}>
            <div className={`w-2 h-2 rounded-full ${llmStatus?.ollama_running ? "bg-green-600" : "bg-red-600"}`} />
            <span className={`text-xs font-semibold ${llmStatus?.ollama_running ? "text-green-700 dark:text-green-200" : "text-red-700 dark:text-red-200"}`}>
              {llmStatus?.ollama_running ? "Running" : "Offline"}
            </span>
          </div>
        </div>
        <p className="text-sm text-muted-foreground mb-4">{llmStatus?.message || "Checking..."}</p>
        {!llmStatus?.ollama_running && (
          <div className="mt-4 p-4 bg-muted rounded-lg border border-border">
            <p className="text-xs font-semibold text-foreground mb-3">To start Ollama, run:</p>
            <pre className="text-xs text-muted-foreground bg-background rounded p-3 overflow-x-auto">
              <code>ollama serve</code>
              <br />
              <code>ollama pull llama3.1:8b</code>
            </pre>
          </div>
        )}
      </div>

      {/* Data Export & Backup */}
      <div className="card p-8 border-blue-200 bg-gradient-to-br from-blue-50 to-card dark:from-blue-950 dark:to-card">
        <div className="flex items-center gap-2 mb-6">
          <Archive size={20} className="text-blue-600" />
          <h2 className="text-lg font-semibold text-foreground">Data Export & Backup</h2>
        </div>
        
        {exportStats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-background rounded-lg border border-border">
              <p className="text-xs text-muted-foreground font-medium">Total Records</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">{(exportStats as any).total_records || 0}</p>
            </div>
            <div className="p-4 bg-background rounded-lg border border-border">
              <p className="text-xs text-muted-foreground font-medium">Estimated Size</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">{(exportStats as any).estimated_size_mb?.toFixed(2) || 0} MB</p>
            </div>
            <div className="p-4 bg-background rounded-lg border border-border">
              <p className="text-xs text-muted-foreground font-medium">Date Range</p>
              <p className="text-xs text-foreground mt-2">From: {(exportStats as any).earliest_date || "N/A"}</p>
              <p className="text-xs text-foreground">To: {(exportStats as any).latest_date || "N/A"}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => handleExport("json")}
            disabled={exporting !== null}
            className="flex flex-col items-start gap-2 p-4 bg-background rounded-lg border-2 border-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900 hover:border-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-center gap-2">
              <Download size={18} className="text-blue-600" />
              <span className="font-semibold text-foreground">{exporting === "json" ? "Exporting..." : "JSON Export"}</span>
            </div>
            <p className="text-xs text-muted-foreground">Structured data with metadata</p>
          </button>

          <button
            onClick={() => handleExport("sql")}
            disabled={exporting !== null}
            className="flex flex-col items-start gap-2 p-4 bg-background rounded-lg border-2 border-green-300 hover:bg-green-50 dark:hover:bg-green-900 hover:border-green-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-center gap-2">
              <Database size={18} className="text-green-600" />
              <span className="font-semibold text-foreground">{exporting === "sql" ? "Exporting..." : "SQL Backup"}</span>
            </div>
            <p className="text-xs text-muted-foreground">Database INSERT statements</p>
          </button>

          <button
            onClick={() => handleExport("backup")}
            disabled={exporting !== null}
            className="flex flex-col items-start gap-2 p-4 bg-background rounded-lg border-2 border-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900 hover:border-purple-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-center gap-2">
              <Archive size={18} className="text-purple-600" />
              <span className="font-semibold text-foreground">{exporting === "backup" ? "Creating..." : "Full Backup"}</span>
            </div>
            <p className="text-xs text-muted-foreground">All formats with timestamp</p>
          </button>
        </div>

        {exportMsg && (
          <div className="mt-4 p-3 rounded-lg bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm">
            {exportMsg}
          </div>
        )}
      </div>

      {/* Add custom trackable */}
      <div className="card p-8">
        <div className="flex items-center gap-2 mb-6">
          <Plus size={20} className="text-blue-600" />
          <h2 className="text-lg font-semibold text-foreground">Add Custom Activity</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-foreground">Activity Name</label>
            <input
              className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              placeholder="e.g. meditation"
              value={newActivity.name}
              onChange={e => setNewActivity(p => ({ ...p, name: e.target.value }))}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-foreground">Category</label>
            <select
              className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              value={newActivity.category}
              onChange={e => setNewActivity(p => ({ ...p, category: e.target.value }))}
            >
              <option value="">Select category</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-foreground">Unit</label>
            <select
              className="border border-border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-600 bg-background text-foreground"
              value={newActivity.unit}
              onChange={e => setNewActivity(p => ({ ...p, unit: e.target.value }))}
            >
              <option value="">Select unit</option>
              {units.map(u => <option key={u} value={u}>{u}</option>)}
            </select>
          </div>
        </div>
        <div className="flex items-center gap-3 mt-6">
          <button
            onClick={handleAdd}
            disabled={adding || !newActivity.name.trim()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus size={18} />
            Add Activity
          </button>
          {msg && <p className="text-sm font-medium text-green-600 flex items-center gap-2"><CheckCircle size={16} />{msg}</p>}
        </div>
      </div>

      {/* All activities */}
      <div className="card p-8">
        <h2 className="text-lg font-semibold text-foreground mb-6">All Custom Activities ({activities.length})</h2>
        <div className="flex flex-col gap-3 max-h-96 overflow-y-auto">
          {activities.length === 0 ? (
            <p className="text-sm text-muted-foreground italic">No custom activities yet. Add one above to get started.</p>
          ) : (
            activities.map((a: any) => (
              <div key={a.id} className="flex items-center justify-between p-4 bg-muted rounded-lg border border-border hover:border-blue-400 transition-colors">
                <div className="flex items-center gap-4 flex-1">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-foreground capitalize">{a.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{a.category}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs font-medium text-muted-foreground">{a.unit}</span>
                  {a.is_auto && (
                    <span className="text-xs bg-blue-600 text-white px-2.5 py-1 rounded-full font-semibold">
                      auto
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Privacy note */}
      <div className="card p-8 border-green-200 bg-gradient-to-br from-green-50 to-card dark:from-green-950 dark:to-card">
        <div className="flex items-center gap-2 mb-6">
          <CheckCircle size={20} className="text-green-600" />
          <h2 className="text-lg font-semibold text-foreground">Privacy & Security</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-foreground">All data stored on your machine only</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-foreground">API runs on localhost — not exposed to internet</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-foreground">LLM runs locally via Ollama — no cloud calls</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-foreground">No telemetry or analytics sent anywhere</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-foreground">No third-party services or external dependencies</span>
          </div>
        </div>
      </div>
    </div>
  );
}
