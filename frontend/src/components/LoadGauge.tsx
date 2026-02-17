"use client";

import type { LoadEstimate } from "../lib/types";

const ACTION_LABELS: Record<string, string> = {
  DECOMPOSE_TASK: "Breaking down task",
  WORKED_EXAMPLE: "Showing worked example",
  HARDER_NEXT: "Increasing difficulty",
};

function scoreToColor(score: number): string {
  if (score < 0.33) return "#22c55e";
  if (score < 0.66) return "#f59e0b";
  return "#ef4444";
}

export default function LoadGauge({ load }: { load: LoadEstimate | null }) {
  if (!load) {
    return (
      <div className="flex flex-col items-center py-6">
        <div className="text-gray-500 text-sm">Collecting data...</div>
      </div>
    );
  }

  const { load_score, label, confidence, recommended_action } = load;
  const angle = load_score * 180;
  const color = scoreToColor(load_score);

  // SVG semi-circular gauge
  const cx = 100;
  const cy = 100;
  const r = 80;
  const startAngle = Math.PI;
  const endAngle = Math.PI + (angle * Math.PI) / 180;

  const x1 = cx + r * Math.cos(startAngle);
  const y1 = cy + r * Math.sin(startAngle);
  const x2 = cx + r * Math.cos(endAngle);
  const y2 = cy + r * Math.sin(endAngle);
  const largeArc = angle > 180 ? 1 : 0;

  const bgX2 = cx + r * Math.cos(2 * Math.PI);
  const bgY2 = cy + r * Math.sin(2 * Math.PI);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 120" className="w-48 h-auto">
        {/* Background arc */}
        <path
          d={`M ${x1} ${y1} A ${r} ${r} 0 1 1 ${bgX2} ${bgY2}`}
          fill="none"
          stroke="#334155"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Active arc */}
        {load_score > 0.01 && (
          <path
            d={`M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        )}
        {/* Score text */}
        <text x={cx} y={cy - 10} textAnchor="middle" fill={color} fontSize="28" fontWeight="bold">
          {(load_score * 100).toFixed(0)}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fill="#94a3b8" fontSize="12">
          {label}
        </text>
      </svg>

      <div className="text-xs text-gray-400 mt-1">
        Confidence: {(confidence * 100).toFixed(0)}%
      </div>

      {recommended_action && (
        <div
          className="mt-2 px-3 py-1 rounded-full text-xs font-medium"
          style={{ backgroundColor: `${color}22`, color }}
        >
          {ACTION_LABELS[recommended_action] || recommended_action}
        </div>
      )}
    </div>
  );
}
