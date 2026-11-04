"use client";

import React, { useEffect, useState, useRef } from "react";
import { apiRequest } from "@/lib/api";
import {
  Camera,
  Users,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  RefreshCw,
  Video,
  Activity,
} from "lucide-react";

interface LiveEvent {
  student_id: number;
  reg_no: string;
  student_name: string;
  period_name?: string;
  subject_code?: string;
  confidence: number;
  time: string;
  status: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [activePeriod, setActivePeriod] = useState<any>(null);
  const [liveEvents, setLiveEvents] = useState<LiveEvent[]>([]);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationMsg, setSimulationMsg] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const fetchDashboardData = async () => {
    try {
      const [statsData, periodData] = await Promise.all([
        apiRequest<any>("/attendance/stats"),
        apiRequest<any>("/timetable/current"),
      ]);
      setStats(statsData);
      setActivePeriod(periodData);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 15000);

    // WebSocket connection for live recognition events
    const wsUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1")
      .replace("http://", "ws://")
      .replace("https://", "wss://")
      + "/ws/live";

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== "pong") {
            setLiveEvents((prev) => [data, ...prev.slice(0, 19)]);
            fetchDashboardData();
          }
        } catch (e) {}
      };

      ws.onerror = () => {
        console.log("WebSocket fallback to polling");
      };
    } catch (e) {}

    return () => {
      clearInterval(interval);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const startLocalWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      alert("Unable to access local webcam. Please check permissions.");
    }
  };

  const stopLocalWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
    }
  };

  const handleSimulateDetection = async (studentId: number) => {
    setIsSimulating(true);
    setSimulationMsg(null);
    try {
      const res = await apiRequest<any>(`/attendance/record?student_id=${studentId}&confidence=0.98`, {
        method: "POST",
      });
      setSimulationMsg(res.message);
      fetchDashboardData();
      // Add to local live events
      setLiveEvents((prev) => [
        {
          student_id: studentId,
          reg_no: `21CS00${studentId}`,
          student_name: `Student #${studentId}`,
          confidence: 0.98,
          time: new Date().toLocaleTimeString(),
          status: res.success ? "PRESENT" : "ALREADY_RECORDED",
        },
        ...prev.slice(0, 19),
      ]);
    } catch (err: any) {
      setSimulationMsg(err.message || "Failed to record");
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Active Timetable Period */}
      <div className={`p-5 rounded-2xl border transition-all ${
        activePeriod?.is_active
          ? "bg-gradient-to-r from-emerald-900 to-emerald-700 text-white border-emerald-600 shadow-lg shadow-emerald-900/10"
          : "bg-slate-900 text-white border-slate-800"
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-xl ${activePeriod?.is_active ? "bg-emerald-500/20" : "bg-slate-800"}`}>
              <Clock className="w-6 h-6 text-emerald-300" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs uppercase tracking-wider font-bold text-emerald-300">
                  {activePeriod?.is_active ? "Class Session in Progress" : "Timetable Status"}
                </span>
                <span className={`w-2 h-2 rounded-full ${activePeriod?.is_active ? "bg-emerald-400 animate-ping" : "bg-amber-400"}`}></span>
              </div>
              <h2 className="text-xl font-bold mt-0.5">
                {activePeriod?.is_active
                  ? `${activePeriod.period?.name} • ${activePeriod.timetable_slot?.subject?.name} (${activePeriod.timetable_slot?.subject?.code})`
                  : activePeriod?.message || "No Active Class Session"}
              </h2>
              <p className="text-xs text-slate-300 mt-0.5">
                {activePeriod?.is_active
                  ? `Scheduled Section: ${activePeriod.timetable_slot?.class_section?.name} | Timings: ${activePeriod.period?.start_time} - ${activePeriod.period?.end_time}`
                  : "Attendance will be verified against the classroom schedule automatically"}
              </p>
            </div>
          </div>

          <button
            onClick={fetchDashboardData}
            className="flex items-center space-x-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-semibold backdrop-blur transition-all self-start md:self-auto"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Attendance %</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">
            {stats?.overall_percentage || 0}%
          </p>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-3">
            <div
              className="bg-indigo-600 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, stats?.overall_percentage || 0)}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Records</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{stats?.total_records || 0}</p>
          <span className="text-[11px] text-slate-400 mt-1 block">Period-wise sessions</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-emerald-600 uppercase tracking-wider">Present</p>
          <p className="text-2xl font-bold text-emerald-700 mt-1">{stats?.present_count || 0}</p>
          <span className="text-[11px] text-emerald-600/80 mt-1 block">Verified on camera</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-amber-500 uppercase tracking-wider">Late</p>
          <p className="text-2xl font-bold text-amber-600 mt-1">{stats?.late_count || 0}</p>
          <span className="text-[11px] text-amber-600/80 mt-1 block">&gt; 15 mins boundary</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-rose-500 uppercase tracking-wider">Absent</p>
          <p className="text-2xl font-bold text-rose-600 mt-1">{stats?.absent_count || 0}</p>
          <span className="text-[11px] text-rose-600/80 mt-1 block">Auto-marked at end</span>
        </div>
      </div>

      {/* Main Grid: Camera View + Live Event Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Camera Video Stream */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Camera className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-800">Classroom Optical Feed</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                LIVE
              </span>
            </div>

            <div className="flex items-center space-x-2">
              {!isCameraActive ? (
                <button
                  onClick={startLocalWebcam}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                >
                  <Video className="w-3.5 h-3.5" />
                  <span>Start WebCam</span>
                </button>
              ) : (
                <button
                  onClick={stopLocalWebcam}
                  className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold transition-colors"
                >
                  Stop
                </button>
              )}
            </div>
          </div>

          <div className="relative bg-slate-950 aspect-video flex items-center justify-center overflow-hidden">
            {isCameraActive ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-center p-8">
                <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-3">
                  <Camera className="w-8 h-8 text-slate-600" />
                </div>
                <p className="text-sm font-semibold text-slate-300">Classroom Camera Feed Idle</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm">
                  Click &apos;Start WebCam&apos; to stream your camera or use the quick simulation triggers below to simulate facial recognition events.
                </p>
              </div>
            )}

            {/* Overlay HUD */}
            <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur border border-white/10 px-3 py-1.5 rounded-lg text-[11px] text-white space-y-0.5">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="font-mono">BACKEND: 30 FPS / SKIP=3</span>
              </div>
              <p className="text-[10px] text-slate-400">Cosine Threshold &tau; &le; 0.45</p>
            </div>
          </div>

          {/* Quick Simulation Trigger Bar */}
          <div className="p-4 bg-slate-50 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                <span>Simulate Student Face Recognition Event:</span>
              </span>
              {simulationMsg && (
                <span className="text-xs font-semibold text-indigo-600 truncate max-w-xs">
                  {simulationMsg}
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4, 5].map((id) => (
                <button
                  key={id}
                  disabled={isSimulating}
                  onClick={() => handleSimulateDetection(id)}
                  className="px-2.5 py-1.5 bg-white border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 text-slate-700 font-semibold text-xs rounded-lg transition-all shadow-sm"
                >
                  Student #{id} (21CS00{id})
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Live Recognition Stream Feed */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[520px]">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-800">Live Recognition Events</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">Real-Time</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {liveEvents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                <Users className="w-10 h-10 mb-2 text-slate-300" />
                <p className="text-sm font-semibold text-slate-600">Awaiting Recognition Events</p>
                <p className="text-xs text-slate-400 mt-1">
                  Faces identified in camera feed or via simulation will appear here instantly.
                </p>
              </div>
            ) : (
              liveEvents.map((ev, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-slate-100/70 transition-colors flex items-start justify-between"
                >
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-emerald-100 text-emerald-700 rounded-lg mt-0.5">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-800">{ev.student_name}</p>
                      <p className="text-[11px] text-slate-500 font-mono">{ev.reg_no}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                          Confidence: {(ev.confidence * 100).toFixed(0)}%
                        </span>
                        <span className="text-[10px] text-slate-400">{ev.time}</span>
                      </div>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    ev.status === "PRESENT"
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-amber-100 text-amber-700"
                  }`}>
                    {ev.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
