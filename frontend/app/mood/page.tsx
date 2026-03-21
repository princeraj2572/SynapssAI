"use client";
import { useState } from "react";
import { useHistory } from "@/lib/hooks/useAnalytics";
import { saveJournal, getJournal } from "@/lib/api";
import { today } from "@/lib/utils";
import StatCard from "@/components/cards/StatCard";
import ActivityLineChart from "@/components/charts/ActivityLineChart";

export default function MoodPage() {
  const { data: moodHistory }   = useHistory("mood", 30);
  const { data: energyHistory } = useHistory("energy", 30);

  const [journal, setJournal] = useState("");
  const [moodScore, setMoodScore] = useState<number>(3);
  const [saved, setSaved] = useState(false);

  const moodData   = moodHistory?.data || [];
  const energyData = energyHistory?.data || [];

  const avgMood   = moodData.length ? (moodData.reduce((s: number, d: any) => s + d.value, 0) / moodData.length).toFixed(1) : 0;
  const avgEnergy = energyData.length ? (energyData.reduce((s: number, d: any) => s + d.value, 0) / energyData.length).toFixed(1) : 0;

  const handleSave = async () => {
    if (!journal.trim()) return;
    await saveJournal(today(), journal, moodScore);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Mood & Mental</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Avg mood (30d)" value={avgMood} unit="/5" color="#ec4899" />
        <StatCard label="Avg energy (30d)" value={avgEnergy} unit="/5" color="#f43f5e" />
      </div>

      {/* Journal */}
      <div className="card flex flex-col gap-3">
        <p className="stat-label">Today&apos;s journal</p>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">Mood today:</span>
          {[1,2,3,4,5].map(n => (
            <button key={n} onClick={() => setMoodScore(n)}
              className={`w-8 h-8 rounded-full text-sm font-semibold transition-all ${moodScore === n ? "bg-pink-500 text-white" : "bg-gray-100 text-gray-500 hover:bg-gray-200"}`}>
              {n}
            </button>
          ))}
        </div>
        <textarea
          className="w-full border border-gray-200 rounded-xl p-3 text-sm resize-none outline-none focus:border-pink-300 transition-colors min-h-[120px]"
          placeholder="How are you feeling today? What happened? What's on your mind..."
          value={journal}
          onChange={e => setJournal(e.target.value)}
        />
        <div className="flex items-center gap-3">
          <button onClick={handleSave}
            className="bg-pink-500 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-pink-600 transition-colors">
            Save entry
          </button>
          {saved && <span className="text-xs text-green-600 font-medium">✓ Saved</span>}
        </div>
      </div>

      <div className="card">
        <p className="stat-label mb-4">Mood trend — last 30 days</p>
        <ActivityLineChart data={moodData} color="#ec4899" unit="/5" height={200} />
      </div>

      <div className="card">
        <p className="stat-label mb-4">Energy trend — last 30 days</p>
        <ActivityLineChart data={energyData} color="#f43f5e" unit="/5" height={160} />
      </div>
    </div>
  );
}
