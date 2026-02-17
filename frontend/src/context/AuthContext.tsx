"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { API_BASE } from "../lib/api";

interface User {
  id: string;
  email: string;
  display_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("alt_token");
    if (saved) {
      setToken(saved);
      fetchMe(saved);
    }
  }, []);

  async function fetchMe(t: string) {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.ok) {
        setUser(await res.json());
      } else {
        localStorage.removeItem("alt_token");
        setToken(null);
      }
    } catch {
      // offline — keep token, try later
    }
  }

  async function login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    localStorage.setItem("alt_token", data.access_token);
    setToken(data.access_token);
    await fetchMe(data.access_token);
  }

  async function register(email: string, password: string, displayName: string) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, display_name: displayName }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    localStorage.setItem("alt_token", data.access_token);
    setToken(data.access_token);
    await fetchMe(data.access_token);
  }

  function logout() {
    localStorage.removeItem("alt_token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
