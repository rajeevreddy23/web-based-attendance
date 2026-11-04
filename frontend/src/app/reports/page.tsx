"use client";

import React, { useState } from "react";
import { apiRequest } from "@/lib/api";
import {
  FileSpreadsheet,
  Download,
  Calendar,
  CheckCircle2,
  FileText,
  Clock,
  Sparkles,
} from "lucide-react";

export default function ReportsPage() {
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);
  const [sectionId, setSectionId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [generating, setGenerating] = useState(false);
  const [lastGenerated, setLastGenerated] = useState<string | null>(null);

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setLastGenerated(null);

    try {
      let url = `/reports/generate?start_date=${startDate}&end_date=${endDate}`;
      if (sectionId) url += `&class_section_id=${sectionId}`;
      if (subjectId) url += `&subject_id=${subjectId}`;

      const res = await apiRequest<{
        filename: string;
        download_url: string;
        total_records: number;
      }>(url, { method: "POST" });

      setLastGenerated(res.filename);

      // Trigger automatic browser download
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const downloadLink = `${API_URL}/reports/download/${res.filename}`;
      
      const a = document.createElement("a");
      a.href = downloadLink;
      a.download = res.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err: any) {
      alert(err.message || "Failed to generate report");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Title Bar */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Automated Excel Reports</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Generate period-wise attendance spreadsheets with multi-sheet executive summaries and audit details
        </p>
      </div>

      {/* Generator Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3 text-indigo-600 mb-6">
          <div className="p-3 bg-indigo-50 rounded-xl">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">Export Parameters</h2>
            <p className="text-xs text-slate-500">Select date range and criteria for .xlsx generation</p>
          </div>
        </div>

        <form onSubmit={handleGenerateReport} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                From Date
              </label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                To Date
              </label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                Class Section Filter
              </label>
              <select
                value={sectionId}
                onChange={(e) => setSectionId(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Class Sections</option>
                <option value="1">CSE-6A</option>
                <option value="2">CSE-6B</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                Subject Filter
              </label>
              <select
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Subjects</option>
                <option value="1">CS601: Machine Learning</option>
                <option value="2">CS602: Cloud Computing</option>
                <option value="3">CS603: Computer Networks</option>
                <option value="4">CS604: Database Management</option>
              </select>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <div className="text-xs text-slate-500 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Multi-sheet workbook formatted with styled headers and status badges</span>
            </div>

            <button
              type="submit"
              disabled={generating}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              <span>{generating ? "Compiling Excel Sheet..." : "Download Excel Report (.xlsx)"}</span>
            </button>
          </div>
        </form>
      </div>

      {lastGenerated && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between text-emerald-900 text-xs">
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <div>
              <p className="font-bold">Report Generated & Downloaded Successfully</p>
              <p className="text-slate-600 font-mono mt-0.5">{lastGenerated}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
