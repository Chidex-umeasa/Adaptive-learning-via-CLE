"use client";

import { useState } from "react";

interface Hint {
  id: string;
  text: string;
  level: number;
}

export default function HintPanel({
  hints,
  onHintOpen,
}: {
  hints: Hint[];
  onHintOpen: (hintId: string) => void;
}) {
  const [revealedLevel, setRevealedLevel] = useState(0);

  const sorted = [...hints].sort((a, b) => a.level - b.level);

  function revealNext() {
    const nextLevel = revealedLevel + 1;
    setRevealedLevel(nextLevel);
    const hint = sorted.find((h) => h.level === nextLevel);
    if (hint) onHintOpen(hint.id);
  }

  const visibleHints = sorted.filter((h) => h.level <= revealedLevel);
  const hasMore = revealedLevel < sorted.length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-300">Hints</h3>
        {hasMore && (
          <button
            onClick={revealNext}
            className="text-xs px-3 py-1 bg-amber-600/20 text-amber-400 rounded-full hover:bg-amber-600/30 transition"
          >
            Reveal hint ({revealedLevel}/{sorted.length})
          </button>
        )}
      </div>

      {visibleHints.length === 0 ? (
        <p className="text-xs text-gray-500">No hints revealed yet. Click to get help.</p>
      ) : (
        <div className="space-y-2">
          {visibleHints.map((h) => (
            <div
              key={h.id}
              className="p-3 bg-slate-700/50 rounded-lg border border-slate-600 text-sm text-gray-200"
            >
              <span className="text-xs text-amber-400 font-medium mr-2">Level {h.level}:</span>
              {h.text}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
