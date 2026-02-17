"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceArea,
  ResponsiveContainer,
} from "recharts";
import { getJSON } from "../../lib/api";

interface TimelinePoint {
  ts_ms: number;
  seconds: number;
  load_score: number;
  label: string;
  confidence: number;
}

interface LoadTimelineProps {
  sessionId: string;
}

export default function LoadTimeline({ sessionId }: LoadTimelineProps) {
  const [points, setPoints] = useState<TimelinePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getJSON(`/analytics/sessions/${sessionId}/timeline`)
      .then((data: { session_id: string; points: TimelinePoint[] }) => {
        setPoints(data.points);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-400">
        Loading timeline...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12 text-red-400">
        Error: {error}
      </div>
    );
  }

  if (points.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        No timeline data for this session.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={points} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

        {/* Zone reference areas */}
        <ReferenceArea y1={0} y2={0.33} fill="#22c55e" fillOpacity={0.1} label="" />
        <ReferenceArea y1={0.33} y2={0.66} fill="#f59e0b" fillOpacity={0.1} label="" />
        <ReferenceArea y1={0.66} y2={1.0} fill="#ef4444" fillOpacity={0.1} label="" />

        <XAxis
          dataKey="seconds"
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          label={{ value: "Seconds", position: "insideBottomRight", offset: -5, fill: "#94a3b8" }}
        />
        <YAxis
          domain={[0, 1]}
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          label={{ value: "Load Score", angle: -90, position: "insideLeft", fill: "#94a3b8" }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "0.5rem",
            color: "#e2e8f0",
          }}
          formatter={(value: number) => [value.toFixed(3), "Load Score"]}
          labelFormatter={(label: number) => `${label.toFixed(1)}s`}
        />
        <Line
          type="monotone"
          dataKey="load_score"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 2, fill: "#3b82f6" }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
