"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex flex-col items-center justify-center min-h-screen gap-4">
            <div className="bg-red-950/60 border border-red-700 rounded-xl p-8 max-w-md text-center">
              <h2 className="text-red-400 text-lg font-semibold mb-2">Something went wrong</h2>
              <p className="text-gray-400 text-sm mb-4">{this.state.message || "An unexpected error occurred."}</p>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg text-sm transition"
              >
                Reload
              </button>
            </div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
