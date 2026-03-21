"use client";
import { useHistory, useStreaks } from "@/lib/hooks/useAnalytics";
import StatCard from "@/components/cards/StatCard";
import StreakCard from "@/components/cards/StreakCard";
import ActivityBarChart from "@/components/charts/ActivityBarChart";

export default function StudyPage() {
  const { data: studyHistory }   = useHistory("study", 30);
  const { data: leetHistory }    = useHistory("leetcode", 30);
  const { data: readingHistory } = useHistory("reading", 30);
  const { data: streaks }        = useStreaks();

  const studyData   = studyHistory?.data || [];
  const leetData    = leetHistory?.data || [];
  const readingData = readingHistory?.data || [];

  const totalStudy  = studyData.reduce((s: number, d: any) => s + d.value, 0);
  const totalLeet   = leetData.reduce((s: number, d: any) => s + d.value, 0);
  const totalPages  = readingData.reduce((s: number, d: any) => s + d.value, 0);
  const avgStudy    = studyData.length ? (totalStudy / studyData.length).toFixed(1) : 0;

  const studyStreak = streaks?.streaks?.find((s: any) => s.activity === "study");

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Study & Learning</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total study (30d)" value={totalStudy.toFixed(1)} unit="hrs" color="#8b5cf6" />
        <StatCard label="Daily average" value={avgStudy} unit="hrs" color="#a78bfa" />
        <StatCard label="LeetCode (30d)" value={totalLeet} unit="problems" color="#7c3aed" />
        <StatCard label="Pages read (30d)" value={totalPages} color="#6d28d9" />
      </div>

      {studyStreak && (
        <div className="grid grid-cols-4 gap-4">
          <StreakCard activity="study" current={studyStreak.current_streak} longest={studyStreak.longest_streak} />
        </div>
      )}

      <div className="card">
        <p className="stat-label mb-4">Study hours — last 30 days</p>
        <ActivityBarChart data={studyData} color="#8b5cf6" unit="hrs" height={200} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <p className="stat-label mb-4">LeetCode problems</p>
          <ActivityBarChart data={leetData} color="#7c3aed" unit="problems" height={160} />
        </div>
        <div className="card">
          <p className="stat-label mb-4">Pages read</p>
          <ActivityBarChart data={readingData} color="#6d28d9" unit="pages" height={160} />
        </div>
      </div>
    </div>
  );
}
