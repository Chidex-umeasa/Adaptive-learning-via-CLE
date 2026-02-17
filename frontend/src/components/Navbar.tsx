"use client";

import { useAuth } from "../context/AuthContext";
import Link from "next/link";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-slate-800 border-b border-slate-700 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-lg font-bold text-white hover:text-blue-400 transition">
          Adaptive Load Tutor
        </Link>
        {isAuthenticated && (
          <Link href="/dashboard" className="text-sm text-gray-400 hover:text-white transition">
            Dashboard
          </Link>
        )}
      </div>

      <div className="flex items-center gap-4">
        {isAuthenticated && user && (
          <>
            <span className="text-sm text-gray-300">{user.display_name}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-400 hover:text-red-400 transition"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
