interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  sub?: string;
  color?: string;
}

export default function StatCard({ label, value, unit, sub, color = "#3b82f6" }: StatCardProps) {
  return (
    <div className="card p-8 flex flex-col justify-between min-h-40">
      <div>
        <p className="stat-label text-xs uppercase tracking-wide">{label}</p>
      </div>
      <div className="flex items-baseline gap-2 mt-6">
        <span className="stat-value text-4xl font-bold" style={{ color }}>{value}</span>
        {unit && <span className="text-base text-muted-foreground font-medium">{unit}</span>}
      </div>
      {sub && <p className="text-xs text-muted-foreground mt-4">{sub}</p>}
    </div>
  );
}
