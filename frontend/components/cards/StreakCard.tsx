interface StreakCardProps {
  activity: string;
  current: number;
  longest: number;
  lastDate?: string;
}

export default function StreakCard({ activity, current, longest, lastDate }: StreakCardProps) {
  return (
    <div className="card p-8 flex flex-col justify-between min-h-40">
      <div>
        <p className="stat-label text-xs uppercase tracking-wide capitalize">{activity} Streak</p>
      </div>
      <div className="mt-6">
        <div className="flex items-baseline gap-3 mb-6">
          <span className="text-4xl font-bold text-orange-500">{current}</span>
          <span className="text-base text-muted-foreground font-medium">days</span>
        </div>
        <div className="text-sm text-muted-foreground">
          Best: <span className="font-semibold text-foreground">{longest} days</span>
        </div>
        {lastDate && (
          <div className="text-xs text-muted-foreground mt-3">Last: {lastDate}</div>
        )}
      </div>
    </div>
  );
}
