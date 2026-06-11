import React from "react";

interface ConfidenceMeterProps {
  score: number;
  label: "High" | "Medium" | "Low";
}

export default function ConfidenceMeter({ score, label }: ConfidenceMeterProps) {
  const percentage = Math.min(Math.max(Math.round(score * 100), 0), 100);

  const colors = {
    High: { text: "text-emerald-400", bg: "bg-emerald-500" },
    Medium: { text: "text-amber-400", bg: "bg-amber-500" },
    Low: { text: "text-rose-400", bg: "bg-rose-500" },
  };

  const currentStyle = colors[label] || colors.Medium;

  return (
    <div className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-zinc-400">Context Confidence Score</span>
        <span className={`text-sm font-bold ${currentStyle.text}`}>
          {label} ({percentage}%)
        </span>
      </div>
      <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
        <div 
          className={`h-full transition-all duration-500 ${currentStyle.bg}`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}