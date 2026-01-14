"use client";

import { useEffect, useRef, useState } from "react";

type WebcamFeature = {
  ts_ms: number;
  face_present: number;
  gaze_on_screen: number;
  gaze_dispersion: number;
  blink_rate: number;
  head_motion: number;
  away_events: number;
};

export default function WebcamFeatures({
  enabled,
  onFeatures,
}: {
  enabled: boolean;
  onFeatures: (f: WebcamFeature) => void;
}) {
  const [status, setStatus] = useState<"off" | "starting" | "on" | "blocked">("off");
  const intervalRef = useRef<any>(null);

  useEffect(() => {
    if (!enabled) {
      setStatus("off");
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    // MVP stub: simulate features every 2s
    setStatus("on");
    intervalRef.current = setInterval(() => {
      onFeatures({
        ts_ms: Date.now(),
        face_present: 0.9,
        gaze_on_screen: 0.8,
        gaze_dispersion: Math.random() * 0.4,
        blink_rate: 12 + Math.random() * 6,
        head_motion: Math.random() * 0.8,
        away_events: Math.random() < 0.1 ? 1 : 0,
      });
    }, 2000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled, onFeatures]);

  return (
    <div className="text-sm">
      <div className="font-medium">Webcam: {status}</div>
      <div className="opacity-70">
        MVP is simulated. Next step: MediaPipe Face Mesh → real face/blink/head motion features.
      </div>
    </div>
  );
}
