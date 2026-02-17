"use client";

import { useEffect, useState } from "react";
import { getJSON } from "../../lib/api";
import Navbar from "../../components/Navbar";
import AggregateStats from "../../components/dashboard/AggregateStats";
import SessionsTable from "../../components/dashboard/SessionsTable";
import LoadTimeline from "../../components/dashboard/LoadTimeline";
import FeatureCorrelation from "../../components/dashboard/FeatureCorrelation";
import ABResultsChart from "../../components/dashboard/ABResultsChart";

interface AggregateData {
  total_sessions: number;
  total_events: number;
  total_users: number;
  mean_load_score: number;
}

interface CorrelationData {
  correlations: Record<string, number>;
  sample_size: number;
}

interface ABVariant {
  sessions: number;
  completion_rate: number;
  correct_submissions: number;
}

export default function DashboardPage() {
  const [aggregate, setAggregate] = useState<AggregateData | null>(null);
  const [correlations, setCorrelations] = useState<CorrelationData | null>(null);
  const [abVariants, setAbVariants] = useState<Record<string, ABVariant>>({});
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      getJSON("/analytics/aggregate"),
      getJSON("/analytics/feature_correlations"),
      getJSON("/analytics/ab_results"),
    ]).then(([aggResult, corrResult, abResult]) => {
      if (aggResult.status === "fulfilled") setAggregate(aggResult.value);
      if (corrResult.status === "fulfilled") setCorrelations(corrResult.value);
      if (abResult.status === "fulfilled") setAbVariants(abResult.value.variants ?? {});
      setLoading(false);
    });
  }, []);

  return (
    <>
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Page title */}
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
          <p className="mt-1 text-gray-400">
            Monitor sessions, cognitive load trends, and experiment results.
          </p>
        </div>

        {/* Aggregate stat cards */}
        {loading ? (
          <div className="text-gray-400">Loading aggregate stats...</div>
        ) : aggregate ? (
          <AggregateStats stats={aggregate} />
        ) : (
          <div className="text-gray-500">Could not load aggregate stats.</div>
        )}

        {/* Sessions table */}
        <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Sessions</h2>
          <SessionsTable
            onSelectSession={setSelectedSession}
            selectedSessionId={selectedSession}
          />
        </section>

        {/* Grid: Timeline, Correlations, A/B Results */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Load Timeline */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              Load Timeline
              {selectedSession && (
                <span className="ml-2 text-sm font-mono text-gray-400">
                  ({selectedSession.slice(0, 8)})
                </span>
              )}
            </h2>
            {selectedSession ? (
              <LoadTimeline sessionId={selectedSession} />
            ) : (
              <div className="flex items-center justify-center py-12 text-gray-500">
                Select a session above to view its load timeline.
              </div>
            )}
          </section>

          {/* Feature Correlations */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              Feature Correlations
            </h2>
            {correlations ? (
              <FeatureCorrelation correlations={correlations.correlations} />
            ) : (
              <div className="flex items-center justify-center py-12 text-gray-500">
                {loading ? "Loading..." : "No correlation data available."}
              </div>
            )}
          </section>

          {/* A/B Results */}
          <section className="bg-slate-800 border border-slate-700 rounded-xl p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-white mb-4">
              A/B Experiment Results
            </h2>
            {Object.keys(abVariants).length > 0 ? (
              <ABResultsChart variants={abVariants} />
            ) : (
              <div className="flex items-center justify-center py-12 text-gray-500">
                {loading ? "Loading..." : "No A/B test results available."}
              </div>
            )}
          </section>
        </div>
      </main>
    </>
  );
}
