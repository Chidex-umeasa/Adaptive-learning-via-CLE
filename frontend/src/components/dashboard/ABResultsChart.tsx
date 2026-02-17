"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface VariantData {
  sessions: number;
  completion_rate: number;
  correct_submissions: number;
}

interface ABResultsChartProps {
  variants: Record<string, VariantData>;
}

export default function ABResultsChart({ variants }: ABResultsChartProps) {
  const data = Object.entries(variants).map(([name, v]) => ({
    variant: name,
    sessions: v.sessions,
    completion_rate: v.completion_rate,
    correct_submissions: v.correct_submissions,
  }));

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        No A/B test results available.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="variant"
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
        />
        <YAxis
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "0.5rem",
            color: "#e2e8f0",
          }}
        />
        <Legend wrapperStyle={{ color: "#e2e8f0" }} />
        <Bar dataKey="sessions" fill="#3b82f6" name="Sessions" />
        <Bar dataKey="completion_rate" fill="#22c55e" name="Completion Rate" />
        <Bar dataKey="correct_submissions" fill="#f59e0b" name="Correct Submissions" />
      </BarChart>
    </ResponsiveContainer>
  );
}
