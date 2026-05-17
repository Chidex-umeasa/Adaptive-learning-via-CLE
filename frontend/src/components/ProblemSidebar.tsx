"use client";

import { useState, useMemo } from "react";
import type { ProblemListItem } from "../lib/types";

const DIFF_COLORS = ["", "text-green-400", "text-yellow-400", "text-orange-400", "text-red-400", "text-purple-400"];

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
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  const categories = useMemo(() => {
    const cats = Array.from(new Set(problems.map((p) => p.category))).sort();
    return ["all", ...cats];
  }, [problems]);

  const filtered = useMemo(() => {
    return problems.filter((p) => {
      const matchCat = category === "all" || p.category === category;
      const matchSearch = p.title.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [problems, category, search]);

  const solvedCount = problems.filter((p) => solvedIds.has(p.id)).length;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-xs font-semibold text-gray-400 uppercase">Problems</h3>
        <span className="text-xs text-gray-500">{solvedCount}/{problems.length}</span>
      </div>

      <input
        type="text"
        placeholder="Search..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-2 py-1.5 text-xs bg-slate-900 border border-slate-700 rounded-md text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
      />

      {categories.length > 2 && (
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full px-2 py-1.5 text-xs bg-slate-900 border border-slate-700 rounded-md text-gray-300 focus:outline-none focus:border-blue-500"
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              {c === "all" ? "All categories" : c}
            </option>
          ))}
        </select>
      )}

      <div className="space-y-0.5">
        {filtered.length === 0 && (
          <div className="text-xs text-gray-600 py-2 text-center">No problems match</div>
        )}
        {filtered.map((p) => {
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
              <span className={`text-[10px] ${DIFF_COLORS[p.difficulty] || "text-gray-500"}`}>
                {"●".repeat(p.difficulty)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
