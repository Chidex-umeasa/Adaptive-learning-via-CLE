import { postJSON, getJSON, API_BASE } from '../lib/api';

// Mock global fetch
const mockFetch = jest.fn();
(global as any).fetch = mockFetch;

// Mock localStorage
const mockLocalStorage: Record<string, string> = {};
Object.defineProperty(global, 'localStorage', {
  value: {
    getItem: (key: string) => mockLocalStorage[key] ?? null,
    setItem: (key: string, val: string) => { mockLocalStorage[key] = val; },
    removeItem: (key: string) => { delete mockLocalStorage[key]; },
  },
  writable: true,
});

beforeEach(() => {
  mockFetch.mockReset();
  for (const key in mockLocalStorage) delete mockLocalStorage[key];
});

describe('postJSON', () => {
  it('sends POST with correct headers and body', async () => {
    const responseBody = { ingested: 3 };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseBody,
      text: async () => JSON.stringify(responseBody),
    });

    const result = await postJSON('/events/batch', { session_id: 's1', events: [] });

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/events/batch`);
    expect(options.method).toBe('POST');
    expect(options.headers['Content-Type']).toBe('application/json');
    expect(JSON.parse(options.body)).toEqual({ session_id: 's1', events: [] });
    expect(result).toEqual(responseBody);
  });
});

describe('getJSON', () => {
  it('sends GET request', async () => {
    const responseBody = { ok: true };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseBody,
      text: async () => JSON.stringify(responseBody),
    });

    const result = await getJSON('/health');

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe(`${API_BASE}/health`);
    // GET should not have a method set explicitly (defaults to GET), or could be undefined
    expect(options.method).toBeUndefined();
    expect(result).toEqual(responseBody);
  });
});

describe('error handling', () => {
  it('throws on error response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      text: async () => 'Internal Server Error',
    });

    await expect(getJSON('/bad-endpoint')).rejects.toThrow('Internal Server Error');
  });
});
