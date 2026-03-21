import { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  sub?: string;
  color?: string;
  icon?: ReactNode;
}

export default function StatCard({ label, value, unit, sub, color = "#3b82f6", icon }: StatCardProps) {
  return (
    <div className="card p-8 flex flex-col justify-between min-h-40">
      <div className="flex items-center justify-between">
        <p className="stat-label text-xs uppercase tracking-wide">{label}</p>
        {icon && <div style={{ color }}>{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2 mt-6">
        <span className="stat-value text-4xl font-bold" style={{ color }}>{value}</span>
        {unit && <span className="text-base text-muted-foreground font-medium">{unit}</span>}
      </div>
      {sub && <p className="text-xs text-muted-foreground mt-4">{sub}</p>}
    </div>
  );
}
