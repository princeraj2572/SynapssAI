"use client";
import { useCorrelations } from "@/lib/hooks/useAnalytics";

const INTERP_COLORS: Record<string, string> = {
  "strong positive":   "bg-green-100 text-green-700",
  "moderate positive": "bg-green-50 text-green-600",
  "weak positive":     "bg-gray-50 text-gray-500",
  "weak negative":     "bg-orange-50 text-orange-500",
  "moderate negative": "bg-red-50 text-red-500",
  "strong negative":   "bg-red-100 text-red-700",
};

export default function AnalyticsPage() {
  const { data: corrData, isLoading } = useCorrelations();
  const correlations = (corrData as any)?.correlations || [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-400 mt-1">Automatically discovered patterns in your life data</p>
      </div>

      <div className="card">
        <p className="stat-label mb-1">Correlation discovery</p>
        <p className="text-xs text-gray-400 mb-4">Based on last 60 days of data. Requires 14+ days of events per activity.</p>

        {isLoading && <p className="text-sm text-gray-400">Computing correlations...</p>}

        {!isLoading && correlations.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-400 text-sm">Not enough data yet for correlations.</p>
            <p className="text-gray-300 text-xs mt-1">Keep logging — correlations appear after 2+ weeks of data.</p>
          </div>
        )}

        {correlations.length > 0 && (
          <div className="flex flex-col gap-3">
            {correlations.map((c: any, i: number) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-xl bg-gray-50">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">
                    <span className="capitalize">{c.activity_a}</span>
                    <span className="text-gray-400 mx-2">↔</span>
                    <span className="capitalize">{c.activity_b}</span>
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24 bg-gray-200 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full"
                      style={{
                        width: `${Math.abs(c.correlation) * 100}%`,
                        background: c.correlation > 0 ? "#10b981" : "#ef4444",
                      }}
                    />
                  </div>
                  <span className="text-sm font-mono font-medium text-gray-700 w-12 text-right">
                    {c.correlation > 0 ? "+" : ""}{c.correlation}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${INTERP_COLORS[c.interpretation] || "bg-gray-100 text-gray-500"}`}>
                    {c.interpretation}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <p className="stat-label mb-2">How to read this</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-500">
          <p>+0.7 to +1.0 = Strong positive — when A goes up, B goes up</p>
          <p>+0.4 to +0.7 = Moderate positive — noticeable pattern</p>
          <p>-0.4 to -0.7 = Moderate negative — when A goes up, B goes down</p>
          <p>-0.7 to -1.0 = Strong negative — clear inverse relationship</p>
        </div>
        <p className="text-xs text-gray-400 mt-3">Correlation does not mean causation. Use these as starting points for investigation, not conclusions.</p>
      </div>
    </div>
  );
}
