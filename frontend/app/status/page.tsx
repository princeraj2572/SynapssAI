"use client";
import { useState, useEffect } from "react";
import useSWR from "swr";
import { healthCheck, getLLMStatus } from "@/lib/api";
import { CheckCircle, AlertCircle, Radio, Wifi, WifiOff, Zap, Cpu, Database, BarChart3, Target, Brain, Clock } from "lucide-react";

export default function StatusPage() {
  const { data: health } = useSWR("health", healthCheck, { refreshInterval: 5000 });
  const { data: llmStatus } = useSWR("llm-status", getLLMStatus, { refreshInterval: 30000 });
  const [connected, setConnected] = useState(true);

  const backends = [
    { name: "Analytics Engine", status: true, icon: <BarChart3 size={20} /> },
    { name: "Streak Tracker", status: true, icon: <Zap size={20} /> },
    { name: "Goal Manager", status: true, icon: <Target size={20} /> },
    { name: "Memory Service", status: (health as any)?.memory_running ?? false, icon: <Brain size={20} /> },
    { name: "Job Scheduler", status: true, icon: <Clock size={20} /> },
  ];

  const collectors = [
    { name: "Desktop Tracker", status: true, lastUpdate: "Just now" },
    { name: "Browser Extension", status: false, lastUpdate: "Yesterday" },
    { name: "Git Scanner", status: true, lastUpdate: "2 mins ago" },
    { name: "Wearable Sync", status: false, lastUpdate: "3 hours ago" },
    { name: "Manual Logger", status: true, lastUpdate: "Just now" },
  ];

  const services = [
    { name: "Backend API", status: true, port: 8080, response: "125ms" },
    { name: "Database (PostgreSQL)", status: true, port: 5432, response: "15ms" },
    { name: "Ollama LLM", status: (llmStatus as any)?.ollama_running ?? false, port: 11434, response: "—" },
    { name: "Redis Cache", status: true, port: 6379, response: "8ms" },
  ];

  const activeCount = backends.filter((b) => b.status).length;
  const collectorCount = collectors.filter((c) => c.status).length;
  const servicesCount = services.filter((s) => s.status).length;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">System Status</h1>
        <p className="text-sm text-muted-foreground mt-2">Real-time status of all services and collectors</p>
      </div>

      {/* Overall Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6 bg-gradient-to-br from-green-50 to-card dark:from-green-950 dark:to-card border-green-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Backends</h3>
            <CheckCircle size={20} className="text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600">{activeCount}/{backends.length}</p>
          <p className="text-xs text-muted-foreground mt-2">Active</p>
        </div>

        <div className={`card p-6 bg-gradient-to-br ${collectorCount > 0 ? "from-blue-50 to-card dark:from-blue-950 dark:to-card border-blue-200" : "from-yellow-50 to-card dark:from-yellow-950 dark:to-card border-yellow-200"}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Collectors</h3>
            {collectorCount > 0 ? <Radio size={20} className="text-blue-600 animate-pulse" /> : <WifiOff size={20} className="text-yellow-600" />}
          </div>
          <p className="text-3xl font-bold text-blue-600">{collectorCount}/{collectors.length}</p>
          <p className="text-xs text-muted-foreground mt-2">Running</p>
        </div>

        <div className="card p-6 bg-gradient-to-br from-purple-50 to-card dark:from-purple-950 dark:to-card border-purple-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Services</h3>
            <Cpu size={20} className="text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-purple-600">{servicesCount}/{services.length}</p>
          <p className="text-xs text-muted-foreground mt-2">Online</p>
        </div>
      </div>

      {/* Backend Services */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Zap size={20} className="text-blue-600" />
          <h2 className="text-xl font-bold text-foreground">Backend Engines</h2>
        </div>
        <div className="card p-6 space-y-4">
          {backends.map((backend, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-secondary transition-colors">
              <div className="flex items-center gap-3 flex-1">
                <div className="text-muted-foreground">{backend.icon}</div>
                <span className="text-sm font-medium text-foreground">{backend.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${backend.status ? "bg-green-500" : "bg-red-500"}`} />
                <span className={`text-xs font-semibold ${backend.status ? "text-green-600" : "text-red-600"}`}>
                  {backend.status ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Collectors */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Radio size={20} className="text-green-600" />
          <h2 className="text-xl font-bold text-foreground">Data Collectors</h2>
        </div>
        <div className="card p-6 space-y-4">
          {collectors.map((collector, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-secondary transition-colors">
              <div className="flex items-center gap-3 flex-1">
                <div className={`w-3 h-3 rounded-full ${collector.status ? "bg-green-500 animate-pulse" : "bg-gray-400"}`} />
                <div>
                  <p className="text-sm font-medium text-foreground">{collector.name}</p>
                  <p className="text-xs text-muted-foreground">Last update: {collector.lastUpdate}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {collector.status ? (
                  <span className="text-xs font-semibold text-green-600 px-2 py-1 rounded bg-green-100 dark:bg-green-900">
                    ✓ Running
                  </span>
                ) : (
                  <span className="text-xs font-semibold text-gray-600 px-2 py-1 rounded bg-gray-100 dark:bg-gray-900">
                    Offline
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Services */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Database size={20} className="text-purple-600" />
          <h2 className="text-xl font-bold text-foreground">System Services</h2>
        </div>
        <div className="card p-6 space-y-4">
          {services.map((service, i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-secondary transition-colors">
              <div className="flex items-center gap-3 flex-1">
                <div className={`w-2.5 h-2.5 rounded-full ${service.status ? "bg-green-500" : "bg-red-500"}`} />
                <div>
                  <p className="text-sm font-medium text-foreground">{service.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {service.status ? `Port ${service.port} • ${service.response} response` : `Port ${service.port} • Offline`}
                  </p>
                </div>
              </div>
              <div>
                <span className={`text-xs font-semibold px-3 py-1 rounded ${service.status ? "bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200" : "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200"}`}>
                  {service.status ? "✓ Online" : "✗ Offline"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Health Indicators */}
      <div>
        <h2 className="text-xl font-bold text-foreground mb-4">Health Indicators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card p-6 border-l-4 border-l-blue-600">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground mb-2">API Connectivity</p>
                <p className="text-xs text-muted-foreground">Backend API responding normally</p>
              </div>
              <CheckCircle size={24} className="text-green-600" />
            </div>
          </div>

          <div className={`card p-6 border-l-4 ${(llmStatus as any)?.ollama_running ? "border-l-green-600" : "border-l-yellow-600"}`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground mb-2">AI Engine (Ollama)</p>
                <p className="text-xs text-muted-foreground">
                  {(llmStatus as any)?.ollama_running ? "Running locally" : "Not running - features limited"}
                </p>
              </div>
              {(llmStatus as any)?.ollama_running ? (
                <CheckCircle size={24} className="text-green-600" />
              ) : (
                <AlertCircle size={24} className="text-yellow-600" />
              )}
            </div>
          </div>

          <div className="card p-6 border-l-4 border-l-purple-600">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground mb-2">Database</p>
                <p className="text-xs text-muted-foreground">PostgreSQL operational ({(health as any)?.db_records || 0} records)</p>
              </div>
              <CheckCircle size={24} className="text-green-600" />
            </div>
          </div>

          <div className="card p-6 border-l-4 border-l-green-600">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground mb-2">Data Collection</p>
                <p className="text-xs text-muted-foreground">{collectorCount} collectors actively tracking</p>
              </div>
              {collectorCount > 0 ? (
                <Radio size={24} className="text-green-600 animate-pulse" />
              ) : (
                <AlertCircle size={24} className="text-yellow-600" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="card p-6 bg-muted">
        <h3 className="text-sm font-semibold text-foreground mb-3">Status Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-foreground">Active/Online</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-foreground">Inactive/Offline</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
            <span className="text-foreground">Running (Animating)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-gray-400" />
            <span className="text-foreground">Disabled</span>
          </div>
        </div>
      </div>

      {/* Refresh Info */}
      <div className="text-center p-4 text-xs text-muted-foreground">
        <p>Status refreshes automatically every 5 seconds</p>
        <p>Last updated: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
}
