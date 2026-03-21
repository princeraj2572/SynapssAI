"use client";
import { useState } from "react";
import { useWeekly } from "@/lib/hooks/useAnalytics";
import { queryMemory } from "@/lib/api";

export default function DigestPage() {
  const { data: weekly } = useWeekly();
  const [digest, setDigest] = useState("");
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      const prompt = `Generate my weekly digest based on this data: ${JSON.stringify(weekly)}. Write 3-4 paragraphs covering: what went well, patterns noticed, and 2-3 recommendations for next week. Be specific and personal.`;
      const res: any = await queryMemory(prompt, 10);
      setDigest(res.answer || "Could not generate digest. Make sure Ollama is running.");
    } catch {
      setDigest("Error generating digest. Is the API server running?");
    } finally {
      setLoading(false);
    }
  };

  const activities = weekly?.activities || [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Weekly Digest</h1>
        <p className="text-sm text-gray-400 mt-1">AI-generated narrative of your week</p>
      </div>

      {activities.length > 0 && (
        <div className="card">
          <p className="stat-label mb-4">This week at a glance</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {activities.slice(0, 6).map((a: any) => (
              <div key={a.activity} className="flex flex-col gap-0.5 p-3 bg-gray-50 rounded-xl">
                <p className="text-xs text-gray-400 capitalize">{a.activity}</p>
                <p className="text-sm font-semibold text-gray-800">{a.total_value} {a.unit}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <p className="stat-label">AI narrative</p>
          <button
            onClick={generate}
            disabled={loading}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
          >
            {loading ? "Generating..." : "Generate digest"}
          </button>
        </div>

        {digest ? (
          <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
            {digest}
          </div>
        ) : (
          <div className="text-center py-10 text-gray-300 text-sm">
            Click &quot;Generate digest&quot; to create your weekly narrative
          </div>
        )}
      </div>
    </div>
  );
}
