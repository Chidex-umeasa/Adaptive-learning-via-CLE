"use client";

import { useAuth } from "../context/AuthContext";
import AuthModal from "../components/AuthModal";
import Tutor from "../components/Tutor";
import ErrorBoundary from "../components/ErrorBoundary";

export default function Page() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <AuthModal />;
  }

  return (
    <ErrorBoundary>
      <Tutor />
    </ErrorBoundary>
  );
}
