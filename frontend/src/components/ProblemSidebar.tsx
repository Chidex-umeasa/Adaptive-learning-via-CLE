"use client";

import type { ProblemListItem } from "../lib/types";

export default function ProblemSidebar({
  problems,
  solvedIds,
  currentId,
  onSelect,
}: {
  problems: ProblemListItem[];
  solvedIds: Set<string>;
  currentId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="space-y-1">
      <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Problems</h3>
      {problems.map((p) => {
        const solved = solvedIds.has(p.id);
        const active = p.id === currentId;
        return (
          <button
            key={p.id}
            onClick={() => onSelect(p.id)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition flex items-center gap-2 ${
              active
                ? "bg-blue-600/20 text-blue-300 border border-blue-500/30"
                : "hover:bg-slate-700/50 text-gray-300"
            }`}
          >
            <span className={`text-xs ${solved ? "text-green-400" : "text-gray-600"}`}>
              {solved ? "✓" : "○"}
            </span>
            <span className="flex-1 truncate">{p.title}</span>
            <span className="text-[10px] text-amber-400">{"★".repeat(p.difficulty)}</span>
          </button>
        );
      })}
    </div>
  );
}
