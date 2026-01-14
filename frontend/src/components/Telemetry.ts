type TelemetryEvent = { ts_ms: number; name: string; payload?: Record<string, any> };

export class Telemetry {
  sessionId: string;
  buffer: TelemetryEvent[] = [];
  flushEveryMs = 1500;
  maxBatch = 50;
  timer: any = null;

  constructor(sessionId: string) {
    this.sessionId = sessionId;
  }

  start(flushFn: (batch: TelemetryEvent[]) => Promise<void>) {
    this.timer = setInterval(async () => {
      if (this.buffer.length === 0) return;
      const batch = this.buffer.splice(0, this.maxBatch);
      try {
        await flushFn(batch);
      } catch {
        // If offline/error, requeue (simple)
        this.buffer.unshift(...batch);
      }
    }, this.flushEveryMs);
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }

  log(name: string, payload: Record<string, any> = {}) {
    this.buffer.push({ ts_ms: Date.now(), name, payload });
  }
}
