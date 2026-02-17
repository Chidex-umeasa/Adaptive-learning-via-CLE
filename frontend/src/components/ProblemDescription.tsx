"use client";

import type { Problem } from "../lib/types";

const CATEGORY_COLORS: Record<string, string> = {
  basics: "bg-green-600/20 text-green-400",
  strings: "bg-blue-600/20 text-blue-400",
  arrays: "bg-purple-600/20 text-purple-400",
  recursion: "bg-orange-600/20 text-orange-400",
  data_structures: "bg-red-600/20 text-red-400",
};

function DifficultyStars({ level }: { level: number }) {
  return (
    <span className="text-amber-400">
      {"★".repeat(level)}
      <span className="text-gray-600">{"★".repeat(5 - level)}</span>
    </span>
  );
}

export default function ProblemDescription({ problem }: { problem: Problem | null }) {
  if (!problem) {
    return (
      <div className="p-6 text-center text-gray-500">
        Loading problem...
      </div>
    );
  }

  const categoryClass = CATEGORY_COLORS[problem.category] || "bg-gray-600/20 text-gray-400";

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 flex-wrap">
        <h2 className="text-lg font-bold text-white">{problem.title}</h2>
        <DifficultyStars level={problem.difficulty} />
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${categoryClass}`}>
          {problem.category.replace("_", " ")}
        </span>
      </div>

      <p className="text-sm text-gray-300 leading-relaxed">{problem.description}</p>

      {problem.test_cases.length > 0 && (
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-gray-400 uppercase">Examples</h4>
          {problem.test_cases.slice(0, 2).map((tc, i) => (
            <div key={i} className="text-xs font-mono bg-slate-800 rounded px-3 py-1.5 text-gray-300">
              Input: {JSON.stringify(tc.input)} → Expected: {JSON.stringify(tc.expected)}
            </div>
          ))}
        </div>
      )}

      {problem.concepts.length > 0 && (
        <div className="flex gap-1.5 flex-wrap">
          {problem.concepts.map((c) => (
            <span key={c} className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-gray-400">
              {c}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
