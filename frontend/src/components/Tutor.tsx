"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { postJSON, getJSON } from "../lib/api";
import { Telemetry } from "./Telemetry";
import WebcamFeatures from "./WebcamFeatures";
import "./Tutor.css";

export default function Tutor() {
  // state
  const [sessionId, setSessionId] = useState<string>(""); // empty on first render
  const [consentWebcam, setConsentWebcam] = useState(false);
  const webcamBuf = useRef<any[]>([]);
  const [load, setLoad] = useState<{
    load_score: number;
    label: string;
    confidence: number;
    recommended_action?: string;
  } | null>(null);

  const [code, setCode] = useState(`function sum(a, b) {\n  // TODO\n}\n`);
  const [effort, setEffort] = useState(4);

  // Create sessionId ONLY once on the client
  useEffect(() => {
    setSessionId(window.crypto.randomUUID());
  }, []);

  // Create telemetry object once sessionId exists
  const telemetry = useMemo(() => {
    return sessionId ? new Telemetry(sessionId) : null;
  }, [sessionId]);

  // Create/update session on backend (only when sessionId exists)
  useEffect(() => {
    if (!sessionId) return;
    (async () => {
      try {
        await postJSON("/sessions", {
          session_id: sessionId,
          consent_telemetry: true,
          consent_webcam: consentWebcam,
        });
      } catch (e) {
        console.log("Session create failed:", e);
      }
    })();
  }, [sessionId, consentWebcam]);

  // Start telemetry batching (only when telemetry/sessionId exist)
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

  // Poll load estimate every 3s
  useEffect(() => {
    if (!sessionId) return;

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

  // -------------------------
  // Render (safe conditional UI)
  // -------------------------
  const ready = Boolean(sessionId && telemetry);

  if (!ready) {
    return (
      <div className="tutor-init-container">
        <h1 className="tutor-title">Adaptive CS Tutor (Cognitive Load)</h1>
        <p className="tutor-init-text">Initializing session…</p>
      </div>
    );
  }

  // telemetry is guaranteed now
  const tlog = (name: string, payload: Record<string, any> = {}) => telemetry!.log(name, payload);

  return (
    <div className="tutor-container">
      <div className="tutor-header-row">
        <div>
          <h1 className="tutor-title-main">Adaptive CS Tutor (Cognitive Load)</h1>
          <div className="tutor-session-id">Session: {sessionId}</div>
        </div>

        <div className="tutor-load-meter">
          <div className="tutor-load-meter-title">Load meter</div>
          {load ? (
            <div className="tutor-load-meter-data">
              <div>
                Label: <b>{load.label}</b>
              </div>
              <div>Score: {load.load_score.toFixed(2)}</div>
              <div>Confidence: {load.confidence.toFixed(2)}</div>
              {load.recommended_action ? (
                <div className="tutor-load-meter-action">
                  Action: <b>{load.recommended_action}</b>
                </div>
              ) : null}
            </div>
          ) : (
            <div className="tutor-load-meter-waiting">Waiting for data…</div>
          )}
        </div>
      </div>

      <div className="tutor-problem-container">
        <div className="tutor-problem-title">
          Problem: Implement <code>sum(a,b)</code>
        </div>
        <div className="tutor-problem-desc">
          Return the sum of two numbers. Then click “Run”.
        </div>

        <label htmlFor="code-editor" className="tutor-label">
          Code editor:
        </label>
        <textarea
          id="code-editor"
          className="tutor-code-editor"
          title="Enter your solution code here"
          placeholder="Write your solution here..."
          value={code}
          onChange={(e) => {
            setCode(e.target.value);
            tlog("keystroke_batch", {
              chars_typed: e.target.value.length,
              deletes: 0,
              pause_mean_ms: 200,
            });
          }}
        />

        <div className="tutor-action-row">
          <button
            onClick={() => {
              tlog("run_code", { code_len: code.length });
              const ok = code.includes("return") && code.includes("a") && code.includes("b");
              tlog(ok ? "correct_answer" : "wrong_answer", { ok });
              alert(ok ? "✅ Looks correct" : "❌ Try adding: return a + b;");
            }}
          >
            Run
          </button>

          <button
            onClick={() => {
              tlog("hint_open", { hint_id: "sum_return" });
              alert("Hint: return a + b;");
            }}
          >
            Hint
          </button>

          <div className="tutor-effort-row">
            <span className="tutor-effort-label">Effort (1–7):</span>
            <input
              type="number"
              min={1}
              max={7}
              value={effort}
              onChange={(e) => setEffort(parseInt(e.target.value || "4", 10))}
              className="tutor-effort-input"
              title="Enter your effort rating from 1 to 7"
              placeholder="Effort (1–7)"
            />
            <button
              onClick={async () => {
                tlog("effort_rating", { rating_1_7: effort });
                await postJSON("/labels/effort", { session_id: sessionId, ts_ms: Date.now(), rating_1_7: effort });
                alert("Saved effort rating ✅");
              }}
            >
              Submit
            </button>
          </div>
        </div>
      </div>

      <div className="tutor-webcam-container">
        <div className="tutor-webcam-header-row">
          <div className="tutor-webcam-title">Webcam (privacy-safe features only)</div>
          <label className="tutor-webcam-label">
            <input
              type="checkbox"
              checked={consentWebcam}
              onChange={(e) => {
                setConsentWebcam(e.target.checked);
                tlog("consent_webcam_changed", { enabled: e.target.checked });
              }}
            />{" "}
            Enable webcam features
          </label>
        </div>

        <div className="tutor-webcam-features">
          <WebcamFeatures enabled={consentWebcam} onFeatures={(f) => webcamBuf.current.push(f)} />
        </div>
      </div>
    </div>
  );
}
