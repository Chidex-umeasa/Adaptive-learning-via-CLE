"use client";

interface FeatureCorrelationProps {
  correlations: Record<string, number>;
}

function cellColor(r: number): string {
  // Map correlation value to a color: green for positive, red for negative
  const abs = Math.min(Math.abs(r), 1);
  const opacity = Math.round(abs * 100);

  if (r >= 0) {
    return `rgba(34, 197, 94, ${(opacity / 100).toFixed(2)})`;
  }
  return `rgba(239, 68, 68, ${(opacity / 100).toFixed(2)})`;
}

function textColor(r: number): string {
  return Math.abs(r) > 0.5 ? "text-white" : "text-gray-200";
}

export default function FeatureCorrelation({
  correlations,
}: FeatureCorrelationProps) {
  const entries = Object.entries(correlations);

  if (entries.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        No correlation data available.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
      {entries.map(([feature, value]) => (
        <div
          key={feature}
          className={`rounded-lg p-3 text-center border border-slate-600 ${textColor(value)}`}
          style={{ backgroundColor: cellColor(value) }}
        >
          <div className="text-xs font-medium truncate" title={feature}>
            {feature}
          </div>
          <div className="text-lg font-bold mt-1">{value.toFixed(3)}</div>
        </div>
      ))}
    </div>
  );
}
