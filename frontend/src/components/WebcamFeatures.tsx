"use client";

import { useEffect, useRef, useState } from "react";
import { FaceMeshProcessor } from "../lib/faceMeshProcessor";
import type { WebcamFeature } from "../lib/types";

export default function WebcamFeatures({
  enabled,
  onFeatures,
}: {
  enabled: boolean;
  onFeatures: (f: WebcamFeature) => void;
}) {
  const [status, setStatus] = useState<"off" | "starting" | "on" | "blocked">("off");
  const videoRef = useRef<HTMLVideoElement>(null);
  const processorRef = useRef<FaceMeshProcessor | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (processorRef.current) {
        processorRef.current.stop();
        processorRef.current = null;
      }
      setStatus("off");
      return;
    }

    let cancelled = false;

    async function start() {
      if (!videoRef.current) return;
      setStatus("starting");

      try {
        const processor = new FaceMeshProcessor(videoRef.current, onFeatures);
        await processor.initialize();
        if (cancelled) {
          processor.stop();
          return;
        }
        processorRef.current = processor;
        setStatus("on");
      } catch (err: any) {
        if (!cancelled) {
          setStatus("blocked");
          console.warn("Webcam access denied:", err.message);
        }
      }
    }

    start();

    return () => {
      cancelled = true;
      if (processorRef.current) {
        processorRef.current.stop();
        processorRef.current = null;
      }
    };
  }, [enabled, onFeatures]);

  return (
    <div className="text-sm space-y-2">
      <div className="flex items-center gap-2">
        <span
          className={`inline-block w-2.5 h-2.5 rounded-full ${
            status === "on" ? "bg-green-400 animate-pulse" :
            status === "starting" ? "bg-yellow-400 animate-pulse" :
            status === "blocked" ? "bg-red-400" :
            "bg-gray-500"
          }`}
        />
        <span className="font-medium">
          Webcam: {status === "on" ? "Active" : status === "starting" ? "Starting..." : status === "blocked" ? "Permission denied" : "Off"}
        </span>
      </div>
      <p className="text-xs text-gray-400">
        Privacy-safe: only numeric features extracted. No video data is stored or transmitted.
      </p>
      <video ref={videoRef} className="hidden" playsInline muted />
    </div>
  );
}
