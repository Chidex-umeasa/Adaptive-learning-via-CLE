"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { postJSON, getJSON } from "../lib/api";
import { Telemetry } from "./Telemetry";
import WebcamFeatures from "./WebcamFeatures";
import CodeEditor from "./CodeEditor";
import LoadGauge from "./LoadGauge";
import HintPanel from "./HintPanel";
import ProblemDescription from "./ProblemDescription";
import ProblemSidebar from "./ProblemSidebar";
import Navbar from "./Navbar";
import type { Problem, ProblemListItem, LoadEstimate, SubmissionResult } from "../lib/types";
import { useAuth } from "../context/AuthContext";

export default function Tutor() {
  const { isAuthenticated } = useAuth();
  const [sessionId, setSessionId] = useState<string>("");
  const [consentWebcam, setConsentWebcam] = useState(false);
  const webcamBuf = useRef<any[]>([]);
  const [load, setLoad] = useState<LoadEstimate | null>(null);

  // Problem state
  const [problems, setProblems] = useState<ProblemListItem[]>([]);
  const [currentProblem, setCurrentProblem] = useState<Problem | null>(null);
  const [code, setCode] = useState("");
  const [solvedIds, setSolvedIds] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<SubmissionResult | null>(null);

  const [effort, setEffort] = useState(4);

  // Initialize session
  useEffect(() => {
    setSessionId(window.crypto.randomUUID());
  }, []);

  // Load persisted solved problems for authenticated users
  useEffect(() => {
    if (!isAuthenticated) return;
    getJSON("/auth/me/solved")
      .then((ids: string[]) => setSolvedIds(new Set(ids)))
      .catch(() => {});
  }, [isAuthenticated]);

  const telemetry = useMemo(() => {
    return sessionId ? new Telemetry(sessionId) : null;
  }, [sessionId]);

  // Create session on backend
  useEffect(() => {
    if (!sessionId) return;
    postJSON("/sessions", {
      session_id: sessionId,
      consent_telemetry: true,
      consent_webcam: consentWebcam,
    }).catch(() => {});
  }, [sessionId, consentWebcam]);

  // Start telemetry batching
  useEffect(() => {
    if (!telemetry || !sessionId) return;
    telemetry.start(async (batch) => {
      await postJSON("/events/batch", { session_id: sessionId, events: batch });
    });
    telemetry.log("session_start", { consent_webcam: consentWebcam });
    return () => telemetry.stop();
  }, [telemetry, sessionId, consentWebcam]);

  // Flush webcam features every 3s
  useEffect(() => {
    if (!sessionId) return;
    const t = setInterval(async () => {
      if (!consentWebcam || webcamBuf.current.length === 0) return;
      const features = webcamBuf.current.splice(0, 20);
      try {
        await postJSON("/webcam/batch", { session_id: sessionId, features });
      } catch {
        webcamBuf.current.unshift(...features);
      }
    }, 3000);
    return () => clearInterval(t);
  }, [sessionId, consentWebcam]);

  // Poll load estimate every 3s
  useEffect(() => {
    if (!sessionId) return;
    const t = setInterval(async () => {
      try {
        const data = await getJSON(`/load/${sessionId}?end_ts_ms=${Date.now()}`);
        setLoad(data);
      } catch {}
    }, 3000);
    return () => clearInterval(t);
  }, [sessionId]);

  // Fetch problems list
  useEffect(() => {
    getJSON("/problems").then(setProblems).catch(() => {});
  }, []);

  // Fetch first/next problem
  useEffect(() => {
    if (!sessionId) return;
    getJSON(`/problems/next/${sessionId}`)
      .then((p: Problem) => {
        setCurrentProblem(p);
        setCode(p.starter_code);
        setLastResult(null);
      })
      .catch(() => {});
  }, [sessionId]);

  const tlog = useCallback(
    (name: string, payload: Record<string, any> = {}) => telemetry?.log(name, payload),
    [telemetry]
  );

  async function selectProblem(id: string) {
    try {
      const p = await getJSON(`/problems/${id}`);
      setCurrentProblem(p);
      setCode(p.starter_code);
      setLastResult(null);
    } catch {}
  }

  async function handleSubmit() {
    if (!currentProblem || !sessionId) return;
    setSubmitting(true);
    tlog("run_code", { code_len: code.length, problem_id: currentProblem.id });

    try {
      const result: SubmissionResult = await postJSON("/problems/submit", {
        session_id: sessionId,
        problem_id: currentProblem.id,
        code,
      });
      setLastResult(result);
      tlog(result.correct ? "correct_answer" : "wrong_answer", {
        problem_id: currentProblem.id,
        tests_passed: result.tests_passed,
        tests_total: result.tests_total,
      });

      if (result.correct) {
        setSolvedIds((prev) => new Set([...prev, currentProblem.id]));
      }
    } catch (err: any) {
      setLastResult({ correct: false, tests_passed: 0, tests_total: 0, errors: [err.message], next_problem_id: null });
    } finally {
      setSubmitting(false);
    }
  }

  async function loadNextProblem() {
    if (!sessionId) return;
    try {
      const p = await getJSON(`/problems/next/${sessionId}`);
      setCurrentProblem(p);
      setCode(p.starter_code);
      setLastResult(null);
    } catch {}
  }

  const onKeystrokeMetrics = useCallback(
    (metrics: { chars_typed: number; deletes: number; pause_mean_ms: number }) => {
      tlog("keystroke_batch", metrics);
    },
    [tlog]
  );

  const ready = Boolean(sessionId && telemetry);

  if (!ready) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-400 text-lg">Initializing session...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1 flex">
        {/* Left sidebar — problem list */}
        <aside className="w-56 bg-slate-800/50 border-r border-slate-700 p-4 overflow-y-auto hidden lg:block">
          <ProblemSidebar
            problems={problems}
            solvedIds={solvedIds}
            currentId={currentProblem?.id || null}
            onSelect={selectProblem}
          />
        </aside>

        {/* Main area — two columns */}
        <main className="flex-1 flex flex-col lg:flex-row gap-4 p-4 overflow-y-auto">
          {/* Left column: problem + editor */}
          <div className="flex-[3] space-y-4 min-w-0">
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <ProblemDescription problem={currentProblem} />
            </div>

            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <CodeEditor value={code} onChange={setCode} onKeystrokeMetrics={onKeystrokeMetrics} />

              <div className="flex items-center gap-3 mt-4 flex-wrap">
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition"
                >
                  {submitting ? "Running..." : "Submit"}
                </button>

                {lastResult && (
                  <div className={`text-sm font-medium ${lastResult.correct ? "text-green-400" : "text-red-400"}`}>
                    {lastResult.correct
                      ? `Correct! (${lastResult.tests_passed}/${lastResult.tests_total} tests passed)`
                      : `Wrong (${lastResult.tests_passed}/${lastResult.tests_total} passed)`}
                  </div>
                )}

                {lastResult?.correct && lastResult.next_problem_id && (
                  <button
                    type="button"
                    onClick={loadNextProblem}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition"
                  >
                    Next Problem
                  </button>
                )}
              </div>

              {lastResult && lastResult.errors.length > 0 && (
                <div className="mt-3 p-3 bg-red-950/50 border border-red-800/50 rounded-lg">
                  <div className="text-xs text-red-400 font-semibold mb-1">Errors:</div>
                  {lastResult.errors.map((e, i) => (
                    <div key={i} className="text-xs text-red-300 font-mono">{e}</div>
                  ))}
                </div>
              )}
            </div>

            {/* Effort rating */}
            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 flex items-center gap-4">
              <span className="text-sm text-gray-400">Effort (1-7):</span>
              <input
                type="range"
                min={1}
                max={7}
                value={effort}
                onChange={(e) => setEffort(parseInt(e.target.value, 10))}
                className="flex-1 accent-blue-500"
                title="Effort rating from 1 to 7"
                aria-label="Effort rating"
              />
              <span className="text-lg font-bold text-white w-8 text-center">{effort}</span>
              <button
                type="button"
                onClick={async () => {
                  tlog("effort_rating", { rating_1_7: effort });
                  await postJSON("/labels/effort", { session_id: sessionId, ts_ms: Date.now(), rating_1_7: effort });
                }}
                className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-sm text-white rounded-lg transition"
              >
                Rate
              </button>
            </div>
          </div>

          {/* Right column: gauge + hints + webcam */}
          <div className="flex-[1.5] space-y-4 min-w-[280px]">
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3">Cognitive Load</h3>
              <LoadGauge load={load} />
            </div>

            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <HintPanel
                hints={currentProblem?.hints || []}
                onHintOpen={(hintId) => tlog("hint_open", { hint_id: hintId })}
              />
            </div>

            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold text-gray-400 uppercase">Webcam</h3>
                <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consentWebcam}
                    onChange={(e) => {
                      setConsentWebcam(e.target.checked);
                      tlog("consent_webcam_changed", { enabled: e.target.checked });
                    }}
                    className="accent-blue-500"
                  />
                  Enable
                </label>
              </div>
              <WebcamFeatures enabled={consentWebcam} onFeatures={(f) => webcamBuf.current.push(f)} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
