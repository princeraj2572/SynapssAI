"use client";
import { useScore, useStreaks, useAlerts, useDaily } from "@/lib/hooks/useAnalytics";
import { useExportStats } from "@/lib/hooks/useAnalytics";
import { today } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import StatCard from "@/components/cards/StatCard";
import ScoreCard from "@/components/cards/ScoreCard";
import StreakCard from "@/components/cards/StreakCard";
import AlertCard from "@/components/cards/AlertCard";
import QuickLog from "@/components/forms/QuickLog";
import Link from "next/link";
import { Code2, Moon, Smile, Archive, BookOpen, Target, BarChart3 } from "lucide-react";

export default function Home() {
  const { data: score }   = useScore();
  const { data: streaks } = useStreaks();
  const { data: alerts }  = useAlerts();
  const { data: daily }   = useDaily(today());
  const { data: exportStats } = useExportStats();

  const topStreaks = (streaks as any)?.streaks?.slice(0, 4) || [];
  const activeAlerts = (alerts as any)?.alerts || [];
  const activities = (daily as any)?.activities || [];
  const stats = exportStats as any;

  const getVal = (name: string) =>
    (activities as any[]).find((a: any) => a.activity === name)?.total_value ?? 0;

  const currentHour = new Date().getHours();
  const greeting = currentHour < 12 ? 'Good morning' : currentHour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 text-white rounded-lg p-8">
        <h1 className="text-4xl font-bold">{greeting}</h1>
        <p className="text-blue-100 mt-2 text-lg">{new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</p>
      </div>

      {/* Feature Quick Links */}
      <div>
        <h2 className="text-lg font-semibold mb-4 text-foreground">Quick Access</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Link href="/analytics" className="p-4 rounded-lg border border-border hover:bg-secondary hover:border-blue-400 transition-all text-center group">
            <BarChart3 size={20} className="mx-auto mb-2 text-blue-600 group-hover:scale-110 transition-transform" />
            <p className="text-xs font-semibold text-foreground">Analytics</p>
          </Link>
          <Link href="/digest" className="p-4 rounded-lg border border-border hover:bg-secondary hover:border-purple-400 transition-all text-center group">
            <BookOpen size={20} className="mx-auto mb-2 text-purple-600 group-hover:scale-110 transition-transform" />
            <p className="text-xs font-semibold text-foreground">Digest</p>
          </Link>
          <Link href="/goals" className="p-4 rounded-lg border border-border hover:bg-secondary hover:border-green-400 transition-all text-center group">
            <Target size={20} className="mx-auto mb-2 text-green-600 group-hover:scale-110 transition-transform" />
            <p className="text-xs font-semibold text-foreground">Goals</p>
          </Link>
          <Link href="/settings" className="p-4 rounded-lg border border-border hover:bg-secondary hover:border-amber-400 transition-all text-center group">
            <Archive size={20} className="mx-auto mb-2 text-amber-600 group-hover:scale-110 transition-transform" />
            <p className="text-xs font-semibold text-foreground">Export</p>
          </Link>
        </div>
      </div>

      {/* Alerts */}
      {activeAlerts.length > 0 && (
        <div className="space-y-3">
          {activeAlerts.map((a: any) => (
            <AlertCard key={a.id} id={a.id} type={a.type} message={a.message} triggeredAt={a.triggered_at} />
          ))}
        </div>
      )}

      {/* Data Summary Card */}
      {stats && (
        <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 border-blue-200">
          <div className="flex items-center gap-2 mb-4">
            <Archive size={20} className="text-blue-600" />
            <h2 className="text-lg font-bold text-foreground">Your Data</h2>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-muted-foreground font-medium">Total Records</p>
              <p className="text-2xl font-bold text-blue-600">{stats.total_records || 0}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Database Size</p>
              <p className="text-2xl font-bold text-indigo-600">{stats.estimated_size_mb?.toFixed(2) || 0} MB</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Time Span</p>
              <p className="text-xs text-foreground mt-2">{stats.earliest_date ? new Date(stats.earliest_date).toLocaleDateString() : "N/A"}</p>
            </div>
          </div>
          <Link href="/settings" className="inline-block mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium">
            Manage & Export Data →
          </Link>
        </Card>
      )}

      {/* Score + Key Metrics */}
      <div>
        <h2 className="text-2xl font-semibold mb-6 text-foreground">Today's Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {score ? <ScoreCard score={(score as any).score} breakdown={(score as any).breakdown} /> : null}
          <StatCard 
            label="Coding" 
            value={getVal("coding_auto") || getVal("coding")} 
            unit="hrs" 
            color="#3b82f6"
            icon={<Code2 size={24} />}
          />
          <StatCard 
            label="Sleep" 
            value={getVal("sleep")} 
            unit="hrs" 
            color="#8b5cf6"
            icon={<Moon size={24} />}
          />
          <StatCard 
            label="Mood" 
            value={getVal("mood") || "—"} 
            unit="/5" 
            color="#ec4899"
            icon={<Smile size={24} />}
          />
        </div>
      </div>

      {/* Streaks */}
      {topStreaks.length > 0 && (
        <div>
          <h2 className="text-2xl font-semibold mb-6 text-foreground">Active Streaks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {topStreaks.map((s: any) => (
              <StreakCard key={s.activity} activity={s.activity} current={s.current_streak} longest={s.longest_streak} lastDate={s.last_date} />
            ))}
          </div>
        </div>
      )}

      {/* Quick Log */}
      <div>
        <h2 className="text-2xl font-semibold mb-6 text-foreground">Quick Actions</h2>
        <QuickLog />
      </div>

      {/* Activity Breakdown */}
      {activities.length > 0 && (
        <div>
          <h2 className="text-2xl font-semibold mb-6 text-foreground">Activity Breakdown</h2>
          <Card className="p-8">
            <div className="space-y-6">
              {activities.map((a: any) => (
                <div key={a.activity} className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold capitalize text-foreground">{a.activity}</span>
                    <span className="text-lg font-bold text-blue-600">
                      {a.total_value} <span className="text-sm text-muted-foreground font-normal">{a.unit}</span>
                    </span>
                  </div>
                  <div className="h-3 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all"
                      style={{ width: `${Math.min((a.total_value / (a.target_value || 10)) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {activities.length === 0 && (
        <Card className="p-8 text-center">
          <p className="font-medium">No data logged today yet.</p>
          <p className="text-sm text-muted-foreground mt-2">Start the desktop agent or use Quick Log above to begin tracking.</p>
        </Card>
      )}
    </div>
  );
}
