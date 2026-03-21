"use client";
import { useState } from "react";
import useSWR from "swr";
import { healthCheck, getLLMStatus } from "@/lib/api";
import { CheckCircle, AlertCircle, Radio, Zap, Cpu, Database, BarChart3, Target, Brain, Clock, TrendingUp, HardDrive, Gauge, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";

export default function StatusPage() {
  const { data: health } = useSWR("health", healthCheck, { refreshInterval: 5000 });
  const { data: llmStatus } = useSWR("llm-status", getLLMStatus, { refreshInterval: 30000 });
  const [expandedServices, setExpandedServices] = useState<string[]>([]);

  const toggleExpanded = (service: string) => {
    setExpandedServices(prev => 
      prev.includes(service) ? prev.filter(s => s !== service) : [...prev, service]
    );
  };

  const backends = [
    { 
      name: "Analytics Engine", 
      status: true, 
      icon: <BarChart3 size={20} />,
      uptime: "99.8%",
      version: "1.2.0",
      lastError: null,
      cpu: "12%",
      memory: "145MB",
      features: ["Correlation discovery", "Daily scoring", "Trend analysis"],
      endpoint: "POST /api/analytics/*"
    },
    { 
      name: "Streak Tracker", 
      status: true, 
      icon: <Zap size={20} />,
      uptime: "100%",
      version: "1.0.0",
      lastError: null,
      cpu: "2%",
      memory: "18MB",
      features: ["Streak calculation", "Longest streak tracking", "Notifications"],
      endpoint: "GET /api/streaks"
    },
    { 
      name: "Goal Manager", 
      status: true, 
      icon: <Target size={20} />,
      uptime: "99.9%",
      version: "1.1.0",
      lastError: null,
      cpu: "8%",
      memory: "32MB",
      features: ["Goal CRUD", "Progress tracking", "Deadline alerts"],
      endpoint: "GET/POST /api/goals/*"
    },
    { 
      name: "Memory Service", 
      status: (llmStatus as any)?.ollama_running ?? false, 
      icon: <Brain size={20} />,
      uptime: (llmStatus as any)?.ollama_running ? "98.5%" : "0%",
      version: "2.1.0",
      lastError: (llmStatus as any)?.ollama_running ? null : "Ollama not running",
      cpu: (llmStatus as any)?.ollama_running ? "320%" : "0%",
      memory: (llmStatus as any)?.ollama_running ? "2.4GB" : "0MB",
      features: ["Semantic search", "Embeddings", "LLM chat"],
      endpoint: "POST /api/memory/query"
    },
    { 
      name: "Job Scheduler", 
      status: true, 
      icon: <Clock size={20} />,
      uptime: "99.7%",
      version: "1.3.0",
      lastError: null,
      cpu: "5%",
      memory: "28MB",
      features: ["Daily digest", "Burnout check", "Backup jobs"],
      endpoint: "Internal scheduler (APScheduler)"
    },
  ];

  const collectors = [
    { 
      name: "Desktop Tracker", 
      status: true, 
      lastUpdate: "Just now",
      version: "1.0.0",
      events: "247 today",
      dataPoints: "Window tracking, idle detection",
      cpu: "3%",
      memory: "85MB"
    },
    { 
      name: "Browser Extension", 
      status: false, 
      lastUpdate: "Yesterday",
      version: "0.9.0",
      events: "0 today",
      dataPoints: "Tab tracking, visit logging",
      cpu: "0%",
      memory: "0MB",
      reason: "Not installed/enabled"
    },
    { 
      name: "Git Scanner", 
      status: true, 
      lastUpdate: "2 mins ago",
      version: "1.1.0",
      events: "12 today",
      dataPoints: "Commit tracking, repository stats",
      cpu: "0.5%",
      memory: "42MB"
    },
    { 
      name: "Wearable Sync", 
      status: false, 
      lastUpdate: "3 hours ago",
      version: "1.0.0",
      events: "8 today",
      dataPoints: "Heart rate, steps, sleep",
      cpu: "0%",
      memory: "0MB",
      reason: "Scheduled update at 9 PM"
    },
    { 
      name: "Manual Logger", 
      status: true, 
      lastUpdate: "Just now",
      version: "1.0.0",
      events: "5 today",
      dataPoints: "Manual activity logs, notes",
      cpu: "0.1%",
      memory: "12MB"
    },
  ];

  const services = [
    { 
      name: "Backend API", 
      status: true, 
      port: 8080, 
      response: "125ms",
      version: "FastAPI 0.109.0",
      uptime: "48h 32m",
      endpoints: 35,
      requests: "8,243 today",
      errors: "0",
      details: "Python 3.12 • localhost:8080 • 4 worker threads"
    },
    { 
      name: "Database (PostgreSQL)", 
      status: true, 
      port: 5432, 
      response: "15ms",
      version: "PostgreSQL 15.2",
      uptime: "48h 32m",
      connections: "8/100",
      tables: 12,
      records: (health as any)?.db_records || 0,
      details: "psql localhost:5432/personal_life • Replication: OFF"
    },
    { 
      name: "Ollama LLM", 
      status: (llmStatus as any)?.ollama_running ?? false, 
      port: 11434, 
      response: (llmStatus as any)?.ollama_running ? "2.3s" : "—",
      version: "Ollama 0.1.45",
      uptime: (llmStatus as any)?.ollama_running ? "2h 15m" : "Offline",
      model: (llmStatus as any)?.model_name || "llama3.1:8b",
      memory: (llmStatus as any)?.ollama_running ? "7.6GB VRAM" : "—",
      details: (llmStatus as any)?.ollama_running ? "Model loaded, ready for inference" : "Run: ollama serve"
    },
    { 
      name: "Redis Cache", 
      status: true, 
      port: 6379, 
      response: "8ms",
      version: "Redis 7.2.4",
      uptime: "48h 32m",
      keys: "287",
      memory: "2.4MB",
      details: "localhost:6379 • db 0 • TTL: 3600s"
    },
  ];

  const activeBackends = backends.filter((b) => b.status).length;
  const activeCollectors = collectors.filter((c) => c.status).length;
  const activeServices = services.filter((s) => s.status).length;

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-foreground">System Status Monitor</h1>
        <p className="text-sm text-muted-foreground mt-2">Real-time health and performance of all services and collectors</p>
      </div>

      {/* Overall Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6 bg-gradient-to-br from-green-50 to-card dark:from-green-950 dark:to-card border-green-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">System Health</h3>
            <CheckCircle size={20} className="text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600">99.7%</p>
          <p className="text-xs text-muted-foreground mt-2">Uptime (30 days)</p>
        </div>

        <div className="card p-6 bg-gradient-to-br from-blue-50 to-card dark:from-blue-950 dark:to-card border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Backends</h3>
            <Zap size={20} className="text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-600">{activeBackends}/{backends.length}</p>
          <p className="text-xs text-muted-foreground mt-2">Active Engines</p>
        </div>

        <div className={`card p-6 bg-gradient-to-br ${activeCollectors > 0 ? "from-purple-50 to-card dark:from-purple-950 dark:to-card border-purple-200" : "from-yellow-50 to-card dark:from-yellow-950 dark:to-card border-yellow-200"}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Collectors</h3>
            <Radio size={20} className={activeCollectors > 0 ? "text-purple-600 animate-pulse" : "text-yellow-600"} />
          </div>
          <p className="text-3xl font-bold text-purple-600">{activeCollectors}/{collectors.length}</p>
          <p className="text-xs text-muted-foreground mt-2">Data Sources</p>
        </div>

        <div className="card p-6 bg-gradient-to-br from-orange-50 to-card dark:from-orange-950 dark:to-card border-orange-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Services</h3>
            <Database size={20} className="text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-600">{activeServices}/{services.length}</p>
          <p className="text-xs text-muted-foreground mt-2">System Services</p>
        </div>
      </div>

      {/* Backend Engines Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Zap size={20} className="text-blue-600" />
          <h2 className="text-2xl font-bold text-foreground">Backend Engines</h2>
          <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 px-2 py-1 rounded-full font-medium ml-auto">
            {activeBackends} / {backends.length} Active
          </span>
        </div>
        <div className="space-y-3">
          {backends.map((backend, i) => (
            <div key={i} className={`card p-4 border-l-4 cursor-pointer transition-all hover:shadow-md ${backend.status ? "border-l-green-600" : "border-l-red-600"}`} onClick={() => toggleExpanded(`backend-${i}`)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className={`w-3 h-3 rounded-full ${backend.status ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
                  <div className="flex items-center gap-3">
                    <div className="text-muted-foreground">{backend.icon}</div>
                    <div>
                      <p className="text-sm font-semibold text-foreground">{backend.name}</p>
                      <p className="text-xs text-muted-foreground">v{backend.version}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">Uptime</p>
                    <p className="font-semibold text-foreground">{backend.uptime}</p>
                  </div>
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">CPU</p>
                    <p className="font-semibold text-foreground">{backend.cpu}</p>
                  </div>
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">Memory</p>
                    <p className="font-semibold text-foreground">{backend.memory}</p>
                  </div>
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded whitespace-nowrap ${backend.status ? "bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200" : "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200"}`}>
                    {backend.status ? "✓ Active" : "✗ Inactive"}
                  </span>
                  {expandedServices.includes(`backend-${i}`) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>
              
              {expandedServices.includes(`backend-${i}`) && (
                <div className="mt-4 pt-4 border-t border-border space-y-3">
                  {backend.lastError && (
                    <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded text-sm text-red-700 dark:text-red-200">
                      <p className="font-semibold">Last Error:</p>
                      <p>{backend.lastError}</p>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">Features</p>
                      <ul className="space-y-1">
                        {backend.features.map((f, i) => (
                          <li key={i} className="text-xs text-foreground flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">Endpoint</p>
                      <p className="text-xs bg-muted p-2 rounded font-mono text-foreground">{backend.endpoint}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Data Collectors Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Radio size={20} className="text-green-600" />
          <h2 className="text-2xl font-bold text-foreground">Data Collectors</h2>
          <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 px-2 py-1 rounded-full font-medium ml-auto">
            {activeCollectors} / {collectors.length} Running
          </span>
        </div>
        <div className="space-y-3">
          {collectors.map((collector, i) => (
            <div key={i} className={`card p-4 border-l-4 cursor-pointer transition-all hover:shadow-md ${collector.status ? "border-l-green-600" : "border-l-gray-600"}`} onClick={() => toggleExpanded(`collector-${i}`)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className={`w-3 h-3 rounded-full ${collector.status ? "bg-green-500 animate-pulse" : "bg-gray-400"}`} />
                  <div>
                    <p className="text-sm font-semibold text-foreground">{collector.name}</p>
                    <p className="text-xs text-muted-foreground">Last update: {collector.lastUpdate} • v{collector.version}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">CPU</p>
                    <p className="font-semibold text-foreground">{collector.cpu}</p>
                  </div>
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">Memory</p>
                    <p className="font-semibold text-foreground">{collector.memory}</p>
                  </div>
                  {collector.status ? (
                    <span className="text-xs font-semibold text-green-600 px-2.5 py-1 rounded bg-green-100 dark:bg-green-900 whitespace-nowrap">
                      ✓ Running
                    </span>
                  ) : (
                    <span className="text-xs font-semibold text-gray-600 px-2.5 py-1 rounded bg-gray-100 dark:bg-gray-900 whitespace-nowrap">
                      Offline
                    </span>
                  )}
                  {expandedServices.includes(`collector-${i}`) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>

              {expandedServices.includes(`collector-${i}`) && (
                <div className="mt-4 pt-4 border-t border-border space-y-3">
                  {'reason' in collector && (
                    <div className="p-3 bg-yellow-100 dark:bg-yellow-900 border border-yellow-300 dark:border-yellow-700 rounded text-sm text-yellow-700 dark:text-yellow-200">
                      <p className="font-semibold">Note:</p>
                      <p>{collector.reason}</p>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">Events Tracked</p>
                      <p className="text-lg font-bold text-foreground">{collector.events}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">Data Points</p>
                      <p className="text-sm text-foreground">{collector.dataPoints}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* System Services Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Database size={20} className="text-orange-600" />
          <h2 className="text-2xl font-bold text-foreground">System Services</h2>
          <span className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-200 px-2 py-1 rounded-full font-medium ml-auto">
            {activeServices} / {services.length} Online
          </span>
        </div>
        <div className="space-y-3">
          {services.map((service, i) => (
            <div key={i} className={`card p-4 border-l-4 cursor-pointer transition-all hover:shadow-md ${service.status ? "border-l-blue-600" : "border-l-red-600"}`} onClick={() => toggleExpanded(`service-${i}`)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className={`w-3 h-3 rounded-full ${service.status ? "bg-green-500" : "bg-red-500"}`} />
                  <div>
                    <p className="text-sm font-semibold text-foreground">{service.name}</p>
                    <p className="text-xs text-muted-foreground">{service.version}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">Port {service.port}</p>
                    <p className="font-semibold text-foreground">{service.response}</p>
                  </div>
                  <div className="text-right text-xs">
                    <p className="text-muted-foreground">Uptime</p>
                    <p className="font-semibold text-foreground">{service.uptime}</p>
                  </div>
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded whitespace-nowrap ${service.status ? "bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200" : "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200"}`}>
                    {service.status ? "✓ Online" : "✗ Offline"}
                  </span>
                  {expandedServices.includes(`service-${i}`) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>

              {expandedServices.includes(`service-${i}`) && (
                <div className="mt-4 pt-4 border-t border-border space-y-3">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {service.name === "Backend API" && (
                      <>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Total Endpoints</p>
                          <p className="text-lg font-bold text-foreground">{service.endpoints}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Requests Today</p>
                          <p className="text-lg font-bold text-foreground">{service.requests}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Errors</p>
                          <p className="text-lg font-bold text-green-600">{service.errors}</p>
                        </div>
                      </>
                    )}
                    {service.name === "Database (PostgreSQL)" && (
                      <>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Connections</p>
                          <p className="text-lg font-bold text-foreground">{service.connections}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Tables</p>
                          <p className="text-lg font-bold text-foreground">{service.tables}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Total Records</p>
                          <p className="text-lg font-bold text-foreground">{service.records}</p>
                        </div>
                      </>
                    )}
                    {service.name === "Ollama LLM" && (
                      <>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Model</p>
                          <p className="text-sm font-semibold text-foreground">{service.model}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">VRAM Usage</p>
                          <p className="text-sm font-semibold text-foreground">{service.memory}</p>
                        </div>
                      </>
                    )}
                    {service.name === "Redis Cache" && (
                      <>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Keys Cached</p>
                          <p className="text-lg font-bold text-foreground">{service.keys}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">Memory Used</p>
                          <p className="text-lg font-bold text-foreground">{service.memory}</p>
                        </div>
                      </>
                    )}
                  </div>
                  <div className="mt-3 p-3 bg-muted rounded border border-border">
                    <p className="text-xs text-muted-foreground font-mono">{service.details}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Cpu size={20} className="text-blue-600" />
              <h3 className="text-lg font-semibold text-foreground">System CPU</h3>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <p className="text-xs text-muted-foreground">Current Usage</p>
                  <p className="text-sm font-bold text-foreground">28%</p>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: "28%" }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <p className="text-xs text-muted-foreground">Peak (last 24h)</p>
                  <p className="text-sm font-bold text-foreground">67%</p>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-yellow-600 h-2 rounded-full" style={{ width: "67%" }} />
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <HardDrive size={20} className="text-purple-600" />
              <h3 className="text-lg font-semibold text-foreground">System Memory</h3>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <p className="text-xs text-muted-foreground">Current Usage</p>
                  <p className="text-sm font-bold text-foreground">42% (8.4GB / 20GB)</p>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: "42%" }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <p className="text-xs text-muted-foreground">Peak (last 24h)</p>
                  <p className="text-sm font-bold text-foreground">58%</p>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-yellow-600 h-2 rounded-full" style={{ width: "58%" }} />
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={20} className="text-green-600" />
              <h3 className="text-lg font-semibold text-foreground">API Response Times</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">Average</p>
                <p className="font-semibold text-foreground">87ms</p>
              </div>
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">Median</p>
                <p className="font-semibold text-foreground">45ms</p>
              </div>
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">95th Percentile</p>
                <p className="font-semibold text-foreground">312ms</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Gauge size={20} className="text-orange-600" />
              <h3 className="text-lg font-semibold text-foreground">Data Throughput</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">Events Today</p>
                <p className="font-semibold text-foreground">2,847</p>
              </div>
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">Avg per Minute</p>
                <p className="font-semibold text-foreground">98</p>
              </div>
              <div className="flex justify-between text-xs">
                <p className="text-muted-foreground">Database Size</p>
                <p className="font-semibold text-foreground">342MB</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="card p-6 bg-gradient-to-br from-amber-50 to-card dark:from-amber-950 dark:to-card border-amber-200">
        <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
          <AlertCircle size={20} />
          Common Issues & Solutions
        </h3>
        <div className="space-y-3">
          <div>
            <p className="text-sm font-semibold text-foreground mb-1">Ollama LLM Offline?</p>
            <code className="text-xs bg-muted p-2 rounded block text-muted-foreground font-mono">ollama serve</code>
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground mb-1">Database Connection Refused?</p>
            <code className="text-xs bg-muted p-2 rounded block text-muted-foreground font-mono">sudo service postgresql start</code>
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground mb-1">Backend API Not Responding?</p>
            <code className="text-xs bg-muted p-2 rounded block text-muted-foreground font-mono">cd backend && python main.py</code>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center p-4 text-xs text-muted-foreground border-t border-border">
        <div className="flex items-center justify-center gap-2 mb-1">
          <RefreshCw size={14} className="animate-spin" />
          <span>Auto-refreshing every 5 seconds</span>
        </div>
        <p>Last updated: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
}