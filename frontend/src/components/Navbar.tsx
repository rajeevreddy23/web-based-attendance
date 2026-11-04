"use client";

import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api";
import { Clock, LogOut, User, ShieldCheck } from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [activePeriod, setActivePeriod] = useState<any>(null);

  useEffect(() => {
    if (pathname === "/") return;
    const fetchActivePeriod = async () => {
      try {
        const data = await apiRequest<any>("/timetable/current");
        setActivePeriod(data);
      } catch (e) {
        // Silently catch if server is warming up
      }
    };
    fetchActivePeriod();
    const interval = setInterval(fetchActivePeriod, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [pathname]);

  if (pathname === "/") return null;

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700">
          <Clock className="w-4 h-4 text-indigo-600" />
          <span className="font-medium">
            {activePeriod?.is_active
              ? `${activePeriod.period?.name}: ${activePeriod.timetable_slot?.subject?.name} (${activePeriod.timetable_slot?.subject?.code})`
              : activePeriod?.message || "Checking timetable..."}
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {user && (
          <div className="flex items-center space-x-3 border-r border-slate-200 pr-4">
            <div className="text-right">
              <p className="text-sm font-semibold text-slate-800 leading-tight">{user.full_name}</p>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700">
                {user.role}
              </span>
            </div>
            <div className="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow">
              {user.full_name?.charAt(0) || "U"}
            </div>
          </div>
        )}

        <button
          onClick={logout}
          title="Sign out"
          className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
