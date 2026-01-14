"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { postJSON, getJSON } from "../lib/api";import { Telemetry } from "./Telemetry";
import WebcamFeatures from "./WebcamFeatures";

function uuid() {
  return crypto.randomUUID();
}

export default function Tutor() {
  const [sessionId] = useState(() => uuid());
  const [consentWebcam, setConsentWebcam] = useState(false);

  const telemetry = useMemo(() => new Telemetry(sessionId), [sessionId]);
  const webcamBuf = useRef<any[]>([]);
  const [load, setLoad] = useState<{ load_score: number; label: string; confidence: number; recommended_action?: string } | null>(null);

  // create session
  useEffect(() => {
    (async () => {
      await postJSON("/sessions", {
        session_id: sessionId,
        consent_telemetry: true,
        consent_webcam: consentWebcam,
      });
    })();
  }, [sessionId, consentWebcam]);

  // start telemetry flush loop
  useEffect(() => {
    telemetry.start(async (batch) => {
      await postJSON("/events/batch", { session_id: sessionId, events: batch });
    });
    telemetry.log("session_start", { consent_webcam: consentWebcam });
    return () => telemetry.stop();
  }, [telemetry, sessionId, consentWebcam]);

  // flush webcam features every ~3s
  useEffect(() => {
    const t = setInterval(async () => {
      if (!consentWebcam) return;
      if (webcamBuf.current.length === 0) return;
      const features = webcamBuf.current.splice(0, 20);
      try {
        await postJSON("/webcam/batch", { session_id: sessionId, features });
      } catch {
        webcamBuf.current.unshift(...features);
      }
    }, 3000);
    return () => clearInterval(t);
  }, [sessionId, consentWebcam]);

  // poll load estimate every 3s
  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const end = Date.now();
        const data = await getJSON(`/load/${sessionId}?end_ts_ms=${end}`);
        setLoad(data);
      } catch {
        // ignore
      }
    }, 3000);
    return () => clearInterval(t);
  }, [sessionId]);

  // minimal “CS task”
  const [code, setCode] = useState(`function sum(a, b) {\n  // TODO\n}\n`);
  const [effort, setEffort] = useState(4);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Adaptive CS Tutor (Cognitive Load)</h1>
          <div className="text-sm opacity-70">Session: {sessionId}</div>
        </div>

        <div className="border rounded-lg p-3 min-w-[240px]">
          <div className="font-medium">Load meter</div>
          {load ? (
            <div className="mt-2 text-sm">
              <div>Label: <b>{load.label}</b></div>
              <div>Score: {load.load_score.toFixed(2)}</div>
              <div>Confidence: {load.confidence.toFixed(2)}</div>
              {load.recommended_action && (
                <div className="mt-1">Action: <b>{load.recommended_action}</b></div>
              )}
            </div>
          ) : (
            <div className="text-sm opacity-70 mt-2">Waiting for data…</div>
          )}
        </div>
      </div>

      <div className="border rounded-lg p-4 space-y-2">
        <div className="font-medium">Problem: Implement <code>sum(a,b)</code></div>
        <div className="text-sm opacity-70">Return the sum of two numbers. Then “Run”.</div>

        <label htmlFor="code-editor" className="sr-only">Code editor for sum(a, b) implementation</label>
        <textarea
          id="code-editor"
          className="w-full h-40 border rounded p-3 font-mono text-sm"
          value={code}
          onChange={(e) => {
            setCode(e.target.value);
            telemetry.log("keystroke_batch", {
              chars_typed: e.target.value.length,
              deletes: 0,
              pause_mean_ms: 200, // TODO replace with real typing pause stats
            });
          }}
          onFocus={() => telemetry.log("editor_focus")}
          onBlur={() => telemetry.log("editor_blur")}
          placeholder="Write your implementation of sum(a, b) here"
          title="Code editor for sum(a, b) implementation"
        />

        <div className="flex gap-3 items-center">
          <button
            className="px-3 py-2 border rounded"
            onClick={() => {
              telemetry.log("run_code", { code_len: code.length });
              // fake feedback
              const ok = code.includes("return") && code.includes("a") && code.includes("b");
              telemetry.log(ok ? "correct_answer" : "wrong_answer", { ok });
            }}
          >
            Run
          </button>

          <button
            className="px-3 py-2 border rounded"
            onClick={() => {
              telemetry.log("hint_open", { hint_id: "sum_return" });
              alert("Hint: return a + b;");
            }}
          >
            Hint
          </button>

          <div className="ml-auto flex items-center gap-2 text-sm">
            <span>Effort (1–7):</span>
            <label htmlFor="effort-input" className="sr-only">Effort rating (1–7)</label>
            <input
              id="effort-input"
              type="number"
              min={1}
              max={7}
              value={effort}
              onChange={(e) => setEffort(parseInt(e.target.value || "4", 10))}
              className="w-16 border rounded p-1"
              placeholder="1–7"
              title="Effort rating from 1 to 7"
            />
            <button
              className="px-3 py-2 border rounded"
              onClick={async () => {
                telemetry.log("effort_rating", { rating_1_7: effort });
                await postJSON("/labels/effort", { session_id: sessionId, ts_ms: Date.now(), rating_1_7: effort });
              }}
            >
              Submit
            </button>
          </div>
        </div>
      </div>

      <div className="border rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="font-medium">Webcam (privacy-safe features only)</div>
          <label className="text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={consentWebcam}
              onChange={(e) => {
                setConsentWebcam(e.target.checked);
                telemetry.log("consent_webcam_changed", { enabled: e.target.checked });
              }}
            />
            Enable webcam features
          </label>
        </div>

        <WebcamFeatures
          enabled={consentWebcam}
          onFeatures={(f) => {
            webcamBuf.current.push(f);
          }}
        />
      </div>
    </div>
  );
}
