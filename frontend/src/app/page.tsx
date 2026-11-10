"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { GraduationCap, Lock, Mail, ArrowRight, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const { login, user } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("admin@college.edu");
  const [password, setPassword] = useState("Admin@123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      if (user.role === "student") {
        router.push("/portal");
      } else {
        router.push("/dashboard");
      }
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await apiRequest<{
        access_token: string;
        role: "admin" | "faculty" | "student";
        full_name: string;
        email: string;
        student_id?: number;
        reg_no?: string;
      }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      login(data.access_token, {
        email: data.email,
        full_name: data.full_name,
        role: data.role,
        student_id: data.student_id,
        reg_no: data.reg_no,
      });
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Check email/roll number and password.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (role: "admin" | "faculty" | "student") => {
    if (role === "admin") {
      setEmail("admin@college.edu");
      setPassword("Admin@123");
    } else if (role === "faculty") {
      setEmail("dr.sharma@college.edu");
      setPassword("Faculty@123");
    } else {
      setEmail("21CS001");
      setPassword("Student@123");
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
        {/* Header Banner */}
        <div className="bg-gradient-to-r from-indigo-900 to-indigo-700 p-8 text-white text-center">
          <div className="w-14 h-14 bg-white/10 backdrop-blur rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/20 shadow-inner">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">SmartAttend Portal</h1>
          <p className="text-indigo-200 text-xs mt-1">
            Real-Time Facial Recognition Attendance System
          </p>
        </div>

        {/* Form Body */}
        <div className="p-8">
          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Email or Roll Number
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@college.edu or 21CS001"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <span>{loading ? "Authenticating..." : "Sign In"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Pre-fill */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center mb-3">
              One-Click Role Login
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin")}
                className="px-2 py-2 text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors text-center"
              >
                Host / Admin
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin("faculty")}
                className="px-2 py-2 text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors text-center"
              >
                Professor
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin("student")}
                className="px-2 py-2 text-[11px] bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg transition-colors text-center border border-indigo-200/50"
              >
                Student (Aarav)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
