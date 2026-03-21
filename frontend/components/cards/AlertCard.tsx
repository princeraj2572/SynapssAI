"use client";
import { dismissAlert } from "@/lib/api";
import { mutate } from "swr";

interface AlertCardProps {
  id: number;
  type: string;
  message: string;
  triggeredAt: string;
}

export default function AlertCard({ id, type, message, triggeredAt }: AlertCardProps) {
  const handleDismiss = async () => {
    await dismissAlert(id);
    mutate("alerts");
  };

  const colors: Record<string, string> = {
    burnout: "border-red-300 bg-red-50",
    streak_risk: "border-orange-300 bg-orange-50",
    goal_missed: "border-yellow-300 bg-yellow-50",
  };

  return (
    <div className={`rounded-xl border p-4 ${colors[type] || "border-gray-200 bg-gray-50"}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs font-semibold uppercase text-red-600 mb-1">{type.replace("_", " ")}</p>
          <p className="text-sm text-gray-700">{message}</p>
        </div>
        <button onClick={handleDismiss} className="text-xs text-gray-400 hover:text-gray-600 ml-4 shrink-0">
          dismiss
        </button>
      </div>
    </div>
  );
}
