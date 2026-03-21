import { scoreColor } from "@/lib/utils";

interface ScoreCardProps {
  score: number;
  breakdown?: Record<string, number>;
}

export default function ScoreCard({ score, breakdown }: ScoreCardProps) {
  const color = scoreColor(score);
  return (
    <div className="card p-8 flex flex-col justify-between min-h-40">
      <div>
        <p className="stat-label text-xs uppercase tracking-wide">Daily Score</p>
      </div>
      <div className="flex items-center gap-8 mt-6">
        <div className="relative w-28 h-28">
          <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="currentColor" strokeWidth="3" className="text-secondary" />
            <circle cx="18" cy="18" r="15.9" fill="none" stroke={color} strokeWidth="3"
              strokeDasharray={`${score} 100`} strokeLinecap="round" className="transition-all" />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-3xl font-bold" style={{ color }}>
            {Math.round(score)}
          </span>
        </div>
        {breakdown && (
          <div className="flex-1 space-y-3">
            {Object.entries(breakdown).map(([k, v]) => (
              <div key={k} className="flex justify-between items-center">
                <span className="text-xs font-medium text-muted-foreground capitalize">{k}</span>
                <span className={`text-sm font-semibold ${v < 0 ? "text-red-500" : "text-green-500"}`}>
                  {v > 0 ? "+" : ""}{v}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
