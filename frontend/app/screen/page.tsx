"use client";
import { useHistory } from "@/lib/hooks/useAnalytics";
import StatCard from "@/components/cards/StatCard";
import ActivityBarChart from "@/components/charts/ActivityBarChart";

export default function ScreenPage() {
  const { data: phoneHistory }  = useHistory("phone_usage", 30);
  const { data: socialHistory } = useHistory("social_media", 30);
  const { data: browserHistory }= useHistory("browser_time", 30);

  const phoneData  = phoneHistory?.data || [];
  const socialData = socialHistory?.data || [];
  const browserData= browserHistory?.data || [];

  const avgPhone  = phoneData.length ? (phoneData.reduce((s: number, d: any) => s + d.value, 0) / phoneData.length).toFixed(1) : 0;
  const avgSocial = socialData.length ? (socialData.reduce((s: number, d: any) => s + d.value, 0) / socialData.length).toFixed(1) : 0;
  const totalBrowser = browserData.reduce((s: number, d: any) => s + d.value, 0).toFixed(1);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Screen & Focus</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Avg phone/day" value={avgPhone} unit="hrs" color="#ef4444" />
        <StatCard label="Avg social/day" value={avgSocial} unit="hrs" color="#f97316" />
        <StatCard label="Browser (30d)" value={totalBrowser} unit="hrs total" color="#eab308" />
      </div>

      <div className="card">
        <p className="stat-label mb-1">Phone usage — last 30 days</p>
        <p className="text-xs text-gray-400 mb-4">Target: under 2 hours/day</p>
        <ActivityBarChart data={phoneData} color="#ef4444" unit="hrs" height={200} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <p className="stat-label mb-4">Social media time</p>
          <ActivityBarChart data={socialData} color="#f97316" unit="hrs" height={160} />
        </div>
        <div className="card">
          <p className="stat-label mb-4">Browser time</p>
          <ActivityBarChart data={browserData} color="#eab308" unit="hrs" height={160} />
        </div>
      </div>
    </div>
  );
}
