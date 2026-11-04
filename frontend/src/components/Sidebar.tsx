"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CalendarCheck,
  Users,
  Calendar,
  FileSpreadsheet,
  Camera,
  Cpu,
  GraduationCap,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  // Don't show sidebar on login page
  if (pathname === "/") return null;

  const navItems = [
    { label: "Live Monitoring", href: "/dashboard", icon: Camera },
    { label: "Attendance Records", href: "/attendance", icon: CalendarCheck },
    { label: "Students & Capture", href: "/students", icon: Users },
    { label: "Class Timetable", href: "/timetable", icon: Calendar },
    { label: "Excel Reports", href: "/reports", icon: FileSpreadsheet },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-white min-h-screen flex flex-col border-r border-slate-800">
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <div className="p-2 bg-indigo-600 rounded-lg">
          <GraduationCap className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-base leading-tight">SmartAttend</h1>
          <p className="text-xs text-slate-400">Facial Recognition System</p>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
          <div className="flex items-center space-x-2 text-xs text-emerald-400 font-semibold mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>MobileNet + SSA-SVM</span>
          </div>
          <p className="text-[11px] text-slate-400">Active Real-Time Gating</p>
        </div>
      </div>
    </aside>
  );
};
