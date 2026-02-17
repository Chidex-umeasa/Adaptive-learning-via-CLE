import { Telemetry } from '../components/Telemetry';

describe('Telemetry', () => {
  it('constructor sets sessionId', () => {
    const t = new Telemetry('sess-123');
    expect(t.sessionId).toBe('sess-123');
  });

  it('buffer accumulates events via .log()', () => {
    const t = new Telemetry('sess-456');
    expect(t.buffer.length).toBe(0);

    t.log('compile_error', { line: 5 });
    t.log('run_code');
    t.log('hint_open', { hintId: 'h1' });

    expect(t.buffer.length).toBe(3);
    expect(t.buffer[0].name).toBe('compile_error');
    expect(t.buffer[0].payload).toEqual({ line: 5 });
    expect(t.buffer[1].name).toBe('run_code');
    expect(t.buffer[2].name).toBe('hint_open');

    // Each event should have a ts_ms timestamp
    for (const evt of t.buffer) {
      expect(typeof evt.ts_ms).toBe('number');
      expect(evt.ts_ms).toBeGreaterThan(0);
    }
  });
});
