"use client";

interface AggregateStatsProps {
  stats: {
    total_sessions: number;
    total_events: number;
    total_users: number;
    mean_load_score: number;
  };
}

const cards = [
  { key: "total_sessions", label: "Total Sessions" },
  { key: "total_events", label: "Total Events" },
  { key: "total_users", label: "Total Users" },
  { key: "mean_load_score", label: "Mean Load Score" },
] as const;

export default function AggregateStats({ stats }: AggregateStatsProps) {
  const format = (key: string, value: number) =>
    key === "mean_load_score" ? value.toFixed(3) : value.toLocaleString();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map(({ key, label }) => (
        <div
          key={key}
          className="bg-slate-700 border border-slate-600 rounded-xl p-6 flex flex-col items-center justify-center"
        >
          <span className="text-3xl font-bold text-white">
            {format(key, stats[key])}
          </span>
          <span className="mt-2 text-sm text-gray-400">{label}</span>
        </div>
      ))}
    </div>
  );
}
