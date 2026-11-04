"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import {
  CalendarCheck,
  Filter,
  Search,
  Edit2,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

interface AttendanceRecord {
  id: number;
  date: string;
  student: {
    id: number;
    reg_no: string;
    full_name: string;
  };
  period: {
    id: number;
    period_number: number;
    name: string;
  };
  subject: {
    id: number;
    code: string;
    name: string;
  };
  class_section_id: number;
  status: "PRESENT" | "ABSENT" | "LATE";
  timestamp: string;
  confidence: number | null;
  verification_method: string;
  marked_by: string;
}

export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState(new Date().toISOString().split("T")[0]);
  const [periodFilter, setPeriodFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // Correction Modal State
  const [selectedRecord, setSelectedRecord] = useState<AttendanceRecord | null>(null);
  const [newStatus, setNewStatus] = useState<"PRESENT" | "ABSENT" | "LATE">("PRESENT");
  const [correctionReason, setCorrectionReason] = useState("");
  const [submittingCorrection, setSubmittingCorrection] = useState(false);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      let url = `/attendance/?date=${dateFilter}`;
      if (periodFilter) url += `&period_id=${periodFilter}`;
      const data = await apiRequest<AttendanceRecord[]>(url);
      setRecords(data);
    } catch (err) {
      console.error("Failed to load records", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [dateFilter, periodFilter]);

  const handleApplyCorrection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRecord) return;
    setSubmittingCorrection(true);
    try {
      await apiRequest("/attendance/correction", {
        method: "POST",
        body: JSON.stringify({
          attendance_id: selectedRecord.id,
          new_status: newStatus,
          reason: correctionReason,
        }),
      });
      setSelectedRecord(null);
      setCorrectionReason("");
      fetchRecords();
    } catch (err: any) {
      alert(err.message || "Failed to update attendance status");
    } finally {
      setSubmittingCorrection(false);
    }
  };

  const filteredRecords = records.filter((r) => {
    const matchesStatus = !statusFilter || r.status === statusFilter;
    const matchesSearch =
      !searchQuery ||
      r.student?.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.student?.reg_no.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.subject?.code.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Attendance Records</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Period-wise attendance verification, duplicate prevention, and faculty audit log
          </p>
        </div>

        <button
          onClick={fetchRecords}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-sm transition-all self-start md:self-auto"
        >
          <RefreshCw className="w-4 h-4 text-slate-500" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-4 gap-3">
        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Date
          </label>
          <input
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
          />
        </div>

        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Period
          </label>
          <select
            value={periodFilter}
            onChange={(e) => setPeriodFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
          >
            <option value="">All Periods</option>
            <option value="1">Period 1 (09:00 - 09:50)</option>
            <option value="2">Period 2 (09:50 - 10:40)</option>
            <option value="3">Period 3 (10:55 - 11:45)</option>
            <option value="4">Period 4 (11:45 - 12:35)</option>
            <option value="6">Period 5 (13:25 - 14:15)</option>
            <option value="7">Period 6 (14:15 - 15:05)</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
          >
            <option value="">All Statuses</option>
            <option value="PRESENT">PRESENT</option>
            <option value="LATE">LATE</option>
            <option value="ABSENT">ABSENT</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Search Student / Subject
          </label>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Name, Reg No, CS601..."
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
            />
          </div>
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Period</th>
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4">Reg No</th>
                <th className="py-3 px-4">Student Name</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Method</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    Loading attendance records...
                  </td>
                </tr>
              ) : filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    No attendance records found matching filters.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-700">
                      P{r.period?.period_number} ({r.period?.name})
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-800">
                      <span className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-mono text-[11px] mr-1.5">
                        {r.subject?.code}
                      </span>
                      {r.subject?.name}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-700">
                      {r.student?.reg_no}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">
                      {r.student?.full_name}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px] ${
                          r.status === "PRESENT"
                            ? "bg-emerald-100 text-emerald-800"
                            : r.status === "LATE"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-rose-100 text-rose-800"
                        }`}
                      >
                        {r.status === "PRESENT" && <CheckCircle className="w-3 h-3 mr-1" />}
                        {r.status === "LATE" && <Clock className="w-3 h-3 mr-1" />}
                        {r.status === "ABSENT" && <XCircle className="w-3 h-3 mr-1" />}
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono">
                      {r.timestamp ? new Date(r.timestamp).toLocaleTimeString() : "N/A"}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      {r.confidence !== null ? `${(r.confidence * 100).toFixed(0)}%` : "N/A"}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 font-medium">
                        {r.verification_method}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => {
                          setSelectedRecord(r);
                          setNewStatus(r.status);
                        }}
                        className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Faculty Manual Correction"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Correction Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-100">
            <div className="flex items-center space-x-3 text-indigo-600 mb-4">
              <div className="p-2 bg-indigo-50 rounded-xl">
                <Edit2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-800">Faculty Manual Correction</h3>
                <p className="text-xs text-slate-500">Traceable change logged to audit trail</p>
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs space-y-1 mb-4">
              <p>
                <span className="font-bold text-slate-600">Student: </span>
                {selectedRecord.student?.full_name} ({selectedRecord.student?.reg_no})
              </p>
              <p>
                <span className="font-bold text-slate-600">Period: </span>
                {selectedRecord.period?.name} - {selectedRecord.subject?.name}
              </p>
              <p>
                <span className="font-bold text-slate-600">Current Status: </span>
                <span className="font-bold uppercase text-indigo-600">{selectedRecord.status}</span>
              </p>
            </div>

            <form onSubmit={handleApplyCorrection} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                  New Status
                </label>
                <select
                  value={newStatus}
                  onChange={(e: any) => setNewStatus(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="PRESENT">PRESENT</option>
                  <option value="LATE">LATE</option>
                  <option value="ABSENT">ABSENT</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                  Audit Reason (Mandatory)
                </label>
                <textarea
                  required
                  rows={3}
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  placeholder="e.g. Student presented medical certificate / laboratory pass slip..."
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                ></textarea>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedRecord(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingCorrection}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50"
                >
                  {submittingCorrection ? "Logging..." : "Confirm & Log to Audit"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
