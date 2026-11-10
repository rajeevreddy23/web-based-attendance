"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api";
import {
  GraduationCap,
  CalendarCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  BookOpen,
  Camera,
  Clock,
  Sparkles,
  ShieldCheck,
  Award,
} from "lucide-react";

interface StudentPortalData {
  student: {
    id: number;
    reg_no: string;
    first_name: string;
    last_name: string;
    full_name: string;
    email: string;
    class_section: string;
    department: string;
    semester: number;
    has_face_registered: boolean;
  };
  metrics: {
    total_classes: number;
    attended_classes: number;
    absent_classes: number;
    attendance_percentage: number;
    is_eligible: boolean;
    threshold_required: number;
    status_label: string;
  };
  subject_breakdown: Array<{
    subject_id: number;
    name: string;
    code: string;
    total: number;
    attended: number;
    absent: number;
    percentage: number;
    status: string;
  }>;
  history: Array<{
    id: number;
    date: string;
    period_name: string;
    period_number: number;
    subject_name: string;
    subject_code: string;
    status: string;
    confidence: number | null;
    verification_method: string;
    timestamp: string;
  }>;
}

export default function StudentPortalPage() {
  const { user } = useAuth();
  const [data, setData] = useState<StudentPortalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortalData = async () => {
    try {
      const res = await apiRequest<StudentPortalData>("/students/portal/me");
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load your student attendance records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortalData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-500 font-medium text-sm">Loading your attendance records...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 max-w-xl mx-auto text-center space-y-4">
        <div className="w-16 h-16 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mx-auto">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-800">Attendance Portal</h2>
        <p className="text-slate-600 text-sm">{error || "Could not retrieve student attendance."}</p>
        <button
          onClick={fetchPortalData}
          className="px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-xl text-sm shadow hover:bg-indigo-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  const { student, metrics, subject_breakdown, history } = data;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* 1. Student Profile Header Card */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-white/5 rounded-full blur-2xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center space-x-5">
            <div className="w-20 h-20 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center shadow-inner">
              <GraduationCap className="w-10 h-10 text-indigo-300" />
            </div>
            <div>
              <div className="flex items-center space-x-3 mb-1">
                <h1 className="text-2xl font-bold tracking-tight">{student.full_name}</h1>
                <span className="px-3 py-1 bg-indigo-500/30 border border-indigo-400/30 rounded-full text-xs font-semibold text-indigo-200">
                  {student.reg_no}
                </span>
              </div>
              <p className="text-indigo-200 text-xs">
                {student.department} • Semester {student.semester} • Section {student.class_section}
              </p>
              <p className="text-slate-400 text-xs mt-0.5">{student.email}</p>
            </div>
          </div>

          {/* Biometric Status Pill */}
          <div className="flex flex-wrap items-center gap-3">
            <div
              className={`px-4 py-2 rounded-2xl border flex items-center space-x-2 text-xs font-semibold backdrop-blur-md ${
                student.has_face_registered
                  ? "bg-emerald-500/20 border-emerald-400/40 text-emerald-300"
                  : "bg-amber-500/20 border-amber-400/40 text-amber-300"
              }`}
            >
              <Camera className="w-4 h-4" />
              <span>
                {student.has_face_registered
                  ? "Face Biometrics Registered & Active"
                  : "Biometric Face Registration Pending"}
              </span>
            </div>

            <div
              className={`px-4 py-2 rounded-2xl border flex items-center space-x-2 text-xs font-semibold backdrop-blur-md ${
                metrics.is_eligible
                  ? "bg-emerald-500/20 border-emerald-400/40 text-emerald-300"
                  : "bg-rose-500/20 border-rose-400/40 text-rose-300"
              }`}
            >
              <Award className="w-4 h-4" />
              <span>{metrics.status_label}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Key Metrics Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* Metric 1: Overall Percentage */}
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Overall Attendance
            </span>
            <div
              className={`p-2 rounded-xl ${
                metrics.is_eligible ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
              }`}
            >
              <CalendarCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span
              className={`text-4xl font-extrabold tracking-tight ${
                metrics.is_eligible ? "text-slate-900" : "text-rose-600"
              }`}
            >
              {metrics.attendance_percentage}%
            </span>
            <span className="text-xs text-slate-400 font-medium">
              (Min {metrics.threshold_required}% required)
            </span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                metrics.is_eligible ? "bg-emerald-500" : "bg-rose-500"
              }`}
              style={{ width: `${Math.min(100, metrics.attendance_percentage)}%` }}
            ></div>
          </div>
        </div>

        {/* Metric 2: Classes Attended */}
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Classes Attended
            </span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
              {metrics.attended_classes}
            </span>
            <span className="text-xs text-slate-500 ml-2">Sessions Present</span>
          </div>
          <p className="text-xs text-slate-400 mt-4">Verified via optical face detection</p>
        </div>

        {/* Metric 3: Classes Missed */}
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Classes Missed
            </span>
            <div className="p-2 bg-rose-50 text-rose-600 rounded-xl">
              <XCircle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-extrabold text-rose-600 tracking-tight">
              {metrics.absent_classes}
            </span>
            <span className="text-xs text-slate-500 ml-2">Sessions Absent</span>
          </div>
          <p className="text-xs text-slate-400 mt-4">Automated period-end absent markers</p>
        </div>

        {/* Metric 4: Total Conducted */}
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Total Lectures
            </span>
            <div className="p-2 bg-slate-50 text-slate-600 rounded-xl">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
              {metrics.total_classes}
            </span>
            <span className="text-xs text-slate-500 ml-2">Conducted Periods</span>
          </div>
          <p className="text-xs text-slate-400 mt-4">Synchronized with academic timetable</p>
        </div>
      </div>

      {/* 3. Subject-Wise Attendance Progress */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Subject-Wise Attendance Breakdown</h2>
              <p className="text-xs text-slate-500">
                Track your attendance percentage per curricular subject
              </p>
            </div>
          </div>
        </div>

        {subject_breakdown.length === 0 ? (
          <p className="text-xs text-slate-400 italic text-center py-6">
            No subject records recorded yet for this academic semester.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {subject_breakdown.map((sub) => {
              const isSafe = sub.percentage >= 75.0;
              return (
                <div
                  key={sub.subject_id}
                  className="p-5 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:shadow-md transition-all space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                        {sub.code}
                      </span>
                      <h3 className="font-bold text-slate-800 text-sm">{sub.name}</h3>
                    </div>
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        isSafe ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                      }`}
                    >
                      {sub.percentage}%
                    </span>
                  </div>

                  <div className="w-full bg-slate-200/80 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isSafe ? "bg-emerald-500" : "bg-rose-500"
                      }`}
                      style={{ width: `${Math.min(100, sub.percentage)}%` }}
                    ></div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>
                      Attended: <strong className="text-slate-700">{sub.attended}</strong> / {sub.total}
                    </span>
                    <span
                      className={`font-semibold ${
                        isSafe ? "text-emerald-600" : "text-rose-600"
                      }`}
                    >
                      {isSafe ? "✓ Eligible" : "⚠ Shortage Warning"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 4. Detailed Period Attendance History */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Recent Attendance History</h2>
              <p className="text-xs text-slate-500">
                Period-wise logs recorded during classroom sessions
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-slate-400">
            Showing latest {history.length} records
          </span>
        </div>

        {history.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No attendance records logged yet for your profile.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200/60">
                <tr>
                  <th className="py-3 px-6">Date</th>
                  <th className="py-3 px-6">Period</th>
                  <th className="py-3 px-6">Subject</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Verification</th>
                  <th className="py-3 px-6">Time Recorded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((row) => {
                  const isPresent = row.status === "PRESENT";
                  const isLate = row.status === "LATE";
                  return (
                    <tr key={row.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-6 font-semibold text-slate-800">{row.date}</td>
                      <td className="py-3.5 px-6 text-slate-600">
                        <span className="font-semibold text-slate-700">{row.period_name}</span>
                      </td>
                      <td className="py-3.5 px-6">
                        <span className="font-semibold text-slate-800">{row.subject_name}</span>{" "}
                        <span className="text-slate-400">({row.subject_code})</span>
                      </td>
                      <td className="py-3.5 px-6">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${
                            isPresent
                              ? "bg-emerald-50 text-emerald-700"
                              : isLate
                              ? "bg-amber-50 text-amber-700"
                              : "bg-rose-50 text-rose-700"
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-6 text-slate-500">
                        <div className="flex items-center space-x-1.5">
                          <Camera className="w-3.5 h-3.5 text-indigo-500" />
                          <span>{row.verification_method}</span>
                          {row.confidence && (
                            <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-mono">
                              {(row.confidence * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-6 text-slate-400 font-mono">{row.timestamp || "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
