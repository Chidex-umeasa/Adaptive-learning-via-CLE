"use client";

import { useRef, useCallback, useEffect } from "react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onKeystrokeMetrics: (metrics: {
    chars_typed: number;
    deletes: number;
    pause_mean_ms: number;
  }) => void;
}

export default function CodeEditor({ value, onChange, onKeystrokeMetrics }: CodeEditorProps) {
  const prevLenRef = useRef(value.length);
  const keystrokeTimes = useRef<number[]>([]);
  const deletesRef = useRef(0);
  const charsRef = useRef(0);
  const metricsTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newVal = e.target.value;
      const now = Date.now();

      const diff = newVal.length - prevLenRef.current;
      if (diff < 0) {
        deletesRef.current += Math.abs(diff);
      } else {
        charsRef.current += diff;
      }
      prevLenRef.current = newVal.length;
      keystrokeTimes.current.push(now);

      onChange(newVal);
    },
    [onChange]
  );

  useEffect(() => {
    metricsTimerRef.current = setInterval(() => {
      const times = keystrokeTimes.current;
      let pauseMean = 0;
      if (times.length > 1) {
        const pauses = [];
        for (let i = 1; i < times.length; i++) {
          pauses.push(times[i] - times[i - 1]);
        }
        pauseMean = pauses.reduce((a, b) => a + b, 0) / pauses.length;
      }

      if (charsRef.current > 0 || deletesRef.current > 0) {
        onKeystrokeMetrics({
          chars_typed: charsRef.current,
          deletes: deletesRef.current,
          pause_mean_ms: Math.round(pauseMean),
        });
      }

      keystrokeTimes.current = [];
      deletesRef.current = 0;
      charsRef.current = 0;
    }, 2000);

    return () => {
      if (metricsTimerRef.current) clearInterval(metricsTimerRef.current);
    };
  }, [onKeystrokeMetrics]);

  return (
    <textarea
      value={value}
      onChange={handleChange}
      spellCheck={false}
      className="w-full min-h-[300px] p-4 bg-slate-950 border border-slate-700 rounded-lg font-mono text-sm text-green-300 resize-y focus:outline-none focus:border-blue-500 transition leading-relaxed"
      placeholder="Write your solution here..."
    />
  );
}
