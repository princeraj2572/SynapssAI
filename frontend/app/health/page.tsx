"use client";
import { useHistory } from "@/lib/hooks/useAnalytics";
import StatCard from "@/components/cards/StatCard";
import ActivityLineChart from "@/components/charts/ActivityLineChart";
import ActivityBarChart from "@/components/charts/ActivityBarChart";

export default function HealthPage() {
  const { data: sleepHistory } = useHistory("sleep", 30);
  const { data: gymHistory }   = useHistory("gym", 30);
  const { data: stepsHistory } = useHistory("steps", 30);

  const sleepData = sleepHistory?.data || [];
  const gymData   = gymHistory?.data || [];
  const stepsData = stepsHistory?.data || [];

  const avgSleep   = sleepData.length ? (sleepData.reduce((s: number, d: any) => s + d.value, 0) / sleepData.length).toFixed(1) : 0;
  const gymDays    = gymData.filter((d: any) => d.value > 0).length;
  const avgSteps   = stepsData.length ? Math.round(stepsData.reduce((s: number, d: any) => s + d.value, 0) / stepsData.length) : 0;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Health</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Avg sleep (30d)" value={avgSleep} unit="hrs/night" color="#3b82f6" />
        <StatCard label="Gym sessions (30d)" value={gymDays} unit="days" color="#10b981" />
        <StatCard label="Avg daily steps" value={avgSteps.toLocaleString()} color="#f59e0b" />
      </div>

      <div className="card">
        <p className="stat-label mb-4">Sleep — last 30 days</p>
        <ActivityLineChart data={sleepData} color="#3b82f6" unit="hrs" height={200} />
        <p className="text-xs text-gray-400 mt-2">Target: 7–8 hours. Red zone: below 6.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <p className="stat-label mb-4">Gym sessions</p>
          <ActivityBarChart data={gymData} color="#10b981" unit="hrs" height={160} />
        </div>
        <div className="card">
          <p className="stat-label mb-4">Daily steps</p>
          <ActivityBarChart data={stepsData} color="#f59e0b" unit="steps" height={160} />
        </div>
      </div>
    </div>
  );
}
