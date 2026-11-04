"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import { Calendar, Clock, BookOpen, User, RefreshCw } from "lucide-react";

interface TimetableSlot {
  id: number;
  day_of_week: number;
  period: {
    id: number;
    period_number: number;
    name: string;
    start_time: string;
    end_time: string;
    is_break: boolean;
  };
  class_section: {
    id: number;
    name: string;
  };
  subject: {
    id: number;
    code: string;
    name: string;
  };
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export default function TimetablePage() {
  const [slots, setSlots] = useState<TimetableSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState(new Date().getDay() === 0 ? 0 : new Date().getDay() - 1);

  const fetchTimetable = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<TimetableSlot[]>("/timetable/");
      setSlots(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimetable();
  }, []);

  const daySlots = slots
    .filter((s) => s.day_of_week === activeDay)
    .sort((a, b) => a.period.period_number - b.period.period_number);

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Class Timetable & Schedule</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automatic period-wise subject identification and active class session verification
          </p>
        </div>

        <button
          onClick={fetchTimetable}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-sm transition-all self-start md:self-auto"
        >
          <RefreshCw className="w-4 h-4 text-slate-500" />
          <span>Refresh Schedule</span>
        </button>
      </div>

      {/* Day Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {DAYS.map((dayName, idx) => (
          <button
            key={dayName}
            onClick={() => setActiveDay(idx)}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              activeDay === idx
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            }`}
          >
            {dayName}
          </button>
        ))}
      </div>

      {/* Period Slots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400">
            Loading scheduled periods...
          </div>
        ) : daySlots.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-400">
            No class periods scheduled for {DAYS[activeDay]}.
          </div>
        ) : (
          daySlots.map((slot) => (
            <div
              key={slot.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 font-bold text-xs rounded-lg">
                    {slot.period.name}
                  </span>
                  <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-medium">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>
                      {slot.period.start_time} - {slot.period.end_time}
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {slot.subject.code}
                  </span>
                  <h3 className="font-bold text-base text-slate-800 leading-snug">
                    {slot.subject.name}
                  </h3>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="font-semibold text-slate-700">
                  Section: {slot.class_section.name}
                </span>
                <span className="text-[11px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded">
                  Attendance Active
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
