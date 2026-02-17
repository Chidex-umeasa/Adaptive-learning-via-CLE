"use client";

import { useEffect, useState } from "react";
import { getJSON } from "../../lib/api";

interface Session {
  session_id: string;
  user_email: string;
  created_at: string;
  event_count: number;
  mean_load: number;
  problems_attempted: number;
  problems_solved: number;
}

interface SessionsTableProps {
  onSelectSession: (sessionId: string) => void;
  selectedSessionId?: string | null;
}

export default function SessionsTable({
  onSelectSession,
  selectedSessionId,
}: SessionsTableProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getJSON("/analytics/sessions")
      .then((data: Session[]) => {
        setSessions(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-400">
        Loading sessions...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12 text-red-400">
        Error: {error}
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        No sessions found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-gray-400 uppercase border-b border-slate-600">
          <tr>
            <th className="px-4 py-3">Session ID</th>
            <th className="px-4 py-3">User</th>
            <th className="px-4 py-3">Start Time</th>
            <th className="px-4 py-3 text-right">Events</th>
            <th className="px-4 py-3 text-right">Problems Attempted</th>
            <th className="px-4 py-3 text-right">Problems Solved</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((s) => {
            const isSelected = s.session_id === selectedSessionId;
            return (
              <tr
                key={s.session_id}
                onClick={() => onSelectSession(s.session_id)}
                className={`cursor-pointer border-b border-slate-700 transition ${
                  isSelected
                    ? "bg-blue-900/30 text-white"
                    : "hover:bg-slate-700/50 text-gray-300"
                }`}
              >
                <td className="px-4 py-3 font-mono text-xs">
                  {s.session_id.slice(0, 8)}
                </td>
                <td className="px-4 py-3">{s.user_email}</td>
                <td className="px-4 py-3">
                  {new Date(s.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right">{s.event_count}</td>
                <td className="px-4 py-3 text-right">{s.problems_attempted}</td>
                <td className="px-4 py-3 text-right">{s.problems_solved}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
