"use client";
import { useHistory, useStreaks } from "@/lib/hooks/useAnalytics";
import StatCard from "@/components/cards/StatCard";
import StreakCard from "@/components/cards/StreakCard";
import ActivityBarChart from "@/components/charts/ActivityBarChart";
import ActivityLineChart from "@/components/charts/ActivityLineChart";

export default function CodingPage() {
  const { data: codingHistory } = useHistory("coding_auto", 30);
  const { data: commitsHistory } = useHistory("git_commits", 30);
  const { data: streaks } = useStreaks();

  const codingData = codingHistory?.data || [];
  const commitsData = commitsHistory?.data || [];

  const totalHours = codingData.reduce((s: number, d: any) => s + d.value, 0);
  const avgHours   = codingData.length ? (totalHours / codingData.length).toFixed(1) : 0;
  const maxDay     = codingData.reduce((m: any, d: any) => d.value > (m?.value || 0) ? d : m, null);
  const totalCommits = commitsData.reduce((s: number, d: any) => s + d.value, 0);

  const codingStreak = streaks?.streaks?.find((s: any) => s.activity.includes("coding"));

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Coding</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total (30d)" value={totalHours.toFixed(1)} unit="hrs" color="#6366f1" />
        <StatCard label="Daily average" value={avgHours} unit="hrs/day" color="#8b5cf6" />
        <StatCard label="Best day" value={maxDay?.value?.toFixed(1) || 0} unit="hrs" color="#a78bfa" sub={maxDay?.date} />
        <StatCard label="Git commits" value={totalCommits} unit="total" color="#7c3aed" />
      </div>

      {codingStreak && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StreakCard activity="coding" current={codingStreak.current_streak} longest={codingStreak.longest_streak} />
        </div>
      )}

      <div className="card">
        <p className="stat-label mb-4">Coding hours — last 30 days</p>
        <ActivityBarChart data={codingData} color="#6366f1" unit="hrs" height={220} />
      </div>

      <div className="card">
        <p className="stat-label mb-4">Git commits — last 30 days</p>
        <ActivityBarChart data={commitsData} color="#7c3aed" unit="commits" height={180} />
      </div>
    </div>
  );
}
