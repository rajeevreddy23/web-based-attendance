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
  Scan,
  Radio,
  BookOpen,
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

interface StudentItem {
  id: number;
  reg_no: string;
  full_name: string;
  email: string;
  has_embeddings: boolean;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [activePeriod, setActivePeriod] = useState<any>(null);
  const [liveEvents, setLiveEvents] = useState<LiveEvent[]>([]);
  const [students, setStudents] = useState<StudentItem[]>([]);
  
  // Camera & Recognition State
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [autoScanEnabled, setAutoScanEnabled] = useState(false);
  const [cameraFeedback, setCameraFeedback] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string>("1");
  const [selectedPeriod, setSelectedPeriod] = useState<string>("");
  const [selectedTestStudent, setSelectedTestStudent] = useState<string>("");

  // Simulation State
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationMsg, setSimulationMsg] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const autoScanIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchDashboardData = async () => {
    try {
      const today = new Date().toISOString().split("T")[0];
      let statsUrl = "/attendance/stats";
      let timetableUrl = "/timetable/current";
      let recordsUrl = `/attendance/?date=${today}`;
      if (selectedSection) {
        statsUrl += `?class_section_id=${selectedSection}`;
        timetableUrl += `?class_section_id=${selectedSection}`;
        recordsUrl += `&class_section_id=${selectedSection}`;
      }

      const [statsData, periodData, todayRecords] = await Promise.all([
        apiRequest<any>(statsUrl),
        apiRequest<any>(timetableUrl),
        apiRequest<any[]>(recordsUrl),
      ]);
      setStats(statsData);
      setActivePeriod(periodData);

      if (todayRecords && todayRecords.length > 0) {
        const events: LiveEvent[] = todayRecords.map((r) => ({
          student_id: r.student?.id || r.student_id,
          reg_no: r.student?.reg_no || "",
          student_name: r.student?.full_name || "Student",
          period_name: r.period?.name || "Period",
          subject_code: r.subject?.code || "CS",
          confidence: r.confidence || 0.95,
          time: r.timestamp ? new Date(r.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString(),
          status: r.status,
        }));
        setLiveEvents((prev) => {
          const combined = [...prev];
          events.forEach((ev) => {
            if (!combined.some((c) => c.student_id === ev.student_id && c.time === ev.time)) {
              combined.push(ev);
            }
          });
          return combined.slice(0, 25);
        });
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    }
  };

  const fetchStudents = async () => {
    try {
      let url = "/students/";
      if (selectedSection) url += `?class_section_id=${selectedSection}`;
      const data = await apiRequest<StudentItem[]>(url);
      setStudents(data);
    } catch (e) {
      console.error("Could not fetch students roster:", e);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchStudents();
    const interval = setInterval(fetchDashboardData, 12000);

    // WebSocket connection for real-time live recognition events
    const wsUrl =
      (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1")
        .replace("http://", "ws://")
        .replace("https://", "wss://") + "/ws/live";

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== "pong") {
            setLiveEvents((prev) => [data, ...prev.slice(0, 24)]);
            fetchDashboardData();
          }
        } catch (e) {}
      };

      ws.onerror = () => {
        console.log("WebSocket fallback to periodic polling");
      };
    } catch (e) {}

    return () => {
      clearInterval(interval);
      if (wsRef.current) wsRef.current.close();
      if (autoScanIntervalRef.current) clearInterval(autoScanIntervalRef.current);
    };
  }, [selectedSection]);

  const startLocalWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      setIsCameraActive(true);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
      setCameraFeedback("Webcam active. Click 'Take Attendance' or turn on 'Auto Scanning'.");
    } catch (err: any) {
      console.error("Camera error:", err);
      alert("Unable to access local webcam. Please allow camera permissions in your browser and ensure no other application is using it.");
    }
  };

  const stopLocalWebcam = () => {
    if (autoScanIntervalRef.current) {
      clearInterval(autoScanIntervalRef.current);
      autoScanIntervalRef.current = null;
    }
    setAutoScanEnabled(false);

    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }

    if (overlayCanvasRef.current) {
      const ctx = overlayCanvasRef.current.getContext("2d");
      if (ctx) ctx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
    }

    setIsCameraActive(false);
    setCameraFeedback(null);
  };

  // Capture frame from video and post to recognition endpoint
  const captureAndRecognize = async () => {
    if (!videoRef.current || !canvasRef.current || isScanning) return;
    const video = videoRef.current;
    if (video.readyState < 2) return;

    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64 = canvas.toDataURL("image/jpeg", 0.85);

    setIsScanning(true);
    try {
      const payload: any = {
        frame_base64: base64,
      };
      if (selectedPeriod) {
        payload.period_id = Number(selectedPeriod);
      }
      if (selectedTestStudent) {
        payload.student_id_hint = Number(selectedTestStudent);
      }

      const res = await apiRequest<any>("/recognition/recognize-frame", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setCameraFeedback(res.message);

      // Render overlay boxes
      if (overlayCanvasRef.current) {
        const overlay = overlayCanvasRef.current;
        overlay.width = canvas.width;
        overlay.height = canvas.height;
        const octx = overlay.getContext("2d");
        if (octx) {
          octx.clearRect(0, 0, overlay.width, overlay.height);
          if (res.detections && res.detections.length > 0) {
            res.detections.forEach((d: any) => {
              const [x, y, w, h] = d.bbox;
              octx.strokeStyle = d.is_unknown ? "#ef4444" : "#10b981";
              octx.lineWidth = 3;
              octx.strokeRect(x, y, w, h);

              octx.fillStyle = d.is_unknown ? "rgba(239, 68, 68, 0.85)" : "rgba(16, 185, 129, 0.85)";
              const labelText = `${d.label} (${(d.confidence * 100).toFixed(0)}%)`;
              octx.font = "bold 13px sans-serif";
              const textWidth = octx.measureText(labelText).width;
              octx.fillRect(x, Math.max(0, y - 24), textWidth + 12, 24);

              octx.fillStyle = "#ffffff";
              octx.fillText(labelText, x + 6, Math.max(16, y - 6));
            });
          }
        }
      }

      if (res.attendance_events && res.attendance_events.length > 0) {
        fetchDashboardData();
      }
    } catch (err: any) {
      setCameraFeedback(err.message || "Recognition processing failed");
    } finally {
      setIsScanning(false);
    }
  };

  // Toggle Auto Scanning
  const toggleAutoScan = () => {
    if (!isCameraActive) {
      alert("Please start the webcam first.");
      return;
    }

    if (autoScanEnabled) {
      if (autoScanIntervalRef.current) {
        clearInterval(autoScanIntervalRef.current);
        autoScanIntervalRef.current = null;
      }
      setAutoScanEnabled(false);
      setCameraFeedback("Auto scanning paused.");
    } else {
      setAutoScanEnabled(true);
      setCameraFeedback("Auto scanning enabled: scanning camera every 2 seconds...");
      captureAndRecognize();
      autoScanIntervalRef.current = setInterval(captureAndRecognize, 2000);
    }
  };

  // Trigger manual simulation / instant attendance recording
  const handleRecordStudent = async (student: StudentItem) => {
    setIsSimulating(true);
    setSimulationMsg(null);
    try {
      let url = `/attendance/record?student_id=${student.id}&confidence=0.98`;
      if (selectedPeriod) {
        url += `&period_id=${selectedPeriod}`;
      }
      const res = await apiRequest<any>(url, { method: "POST" });
      setSimulationMsg(res.message);
      fetchDashboardData();
    } catch (err: any) {
      setSimulationMsg(err.message || "Failed to record");
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Active Timetable Period */}
      <div
        className={`p-5 rounded-2xl border transition-all ${
          activePeriod?.is_active
            ? "bg-gradient-to-r from-emerald-900 to-emerald-700 text-white border-emerald-600 shadow-lg shadow-emerald-900/10"
            : "bg-slate-900 text-white border-slate-800"
        }`}
      >
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
                <span
                  className={`w-2 h-2 rounded-full ${
                    activePeriod?.is_active ? "bg-emerald-400 animate-ping" : "bg-amber-400"
                  }`}
                ></span>
              </div>
              <h2 className="text-xl font-bold mt-0.5">
                {activePeriod?.is_active
                  ? `${activePeriod.period?.name} • ${activePeriod.timetable_slot?.subject?.name} (${activePeriod.timetable_slot?.subject?.code})`
                  : activePeriod?.message || "Class Schedule Ready"}
              </h2>
              <p className="text-xs text-slate-300 mt-0.5">
                {activePeriod?.is_active
                  ? `Scheduled Section: ${activePeriod.timetable_slot?.class_section?.name} | Timings: ${activePeriod.period?.start_time} - ${activePeriod.period?.end_time}`
                  : "Attendance will be verified and stored directly into database"}
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
          <span className="text-[11px] text-slate-400 mt-1 block">In database</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-emerald-600 uppercase tracking-wider">Present</p>
          <p className="text-2xl font-bold text-emerald-700 mt-1">{stats?.present_count || 0}</p>
          <span className="text-[11px] text-emerald-600/80 mt-1 block">Camera / Facial Verified</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-amber-500 uppercase tracking-wider">Late</p>
          <p className="text-2xl font-bold text-amber-600 mt-1">{stats?.late_count || 0}</p>
          <span className="text-[11px] text-amber-600/80 mt-1 block">&gt; 15 mins</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-bold text-rose-500 uppercase tracking-wider">Absent</p>
          <p className="text-2xl font-bold text-rose-600 mt-1">{stats?.absent_count || 0}</p>
          <span className="text-[11px] text-rose-600/80 mt-1 block">Auto-marked / Unverified</span>
        </div>
      </div>

      {/* Main Grid: Optical Camera Feed + Live Event Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Camera Video Stream & Controls */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          {/* Header Controls */}
          <div className="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <Camera className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-800">Classroom Optical Feed</h3>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  isCameraActive ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"
                }`}
              >
                {isCameraActive ? "LIVE FEED ACTIVE" : "IDLE"}
              </span>
            </div>

            {/* Camera Action Buttons */}
            <div className="flex items-center space-x-2">
              {!isCameraActive ? (
                <button
                  onClick={startLocalWebcam}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm"
                >
                  <Video className="w-4 h-4" />
                  <span>Start WebCam</span>
                </button>
              ) : (
                <>
                  <button
                    onClick={captureAndRecognize}
                    disabled={isScanning}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition-all disabled:opacity-50"
                  >
                    <Scan className="w-4 h-4" />
                    <span>{isScanning ? "Processing..." : "Take Attendance"}</span>
                  </button>

                  <button
                    onClick={toggleAutoScan}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 border transition-all ${
                      autoScanEnabled
                        ? "bg-emerald-50 border-emerald-400 text-emerald-700 animate-pulse"
                        : "bg-white border-slate-300 text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    <Radio className="w-3.5 h-3.5" />
                    <span>Auto-Scan: {autoScanEnabled ? "ON" : "OFF"}</span>
                  </button>

                  <button
                    onClick={stopLocalWebcam}
                    className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold transition-colors"
                  >
                    Stop
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Session Parameters Filter Bar */}
          <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-100 flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-500 uppercase tracking-wider text-[11px]">Class Section:</span>
              <select
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="1">CSE-6A (Semester 6)</option>
                <option value="2">CSE-6B (Semester 6)</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-500 uppercase tracking-wider text-[11px]">Period:</span>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Auto-Detect / Active Session</option>
                <option value="1">Period 1 (09:00 - 09:50) CS601: Machine Learning</option>
                <option value="2">Period 2 (09:50 - 10:40) CS602: Cloud Computing</option>
                <option value="3">Period 3 (10:55 - 11:45) CS603: Computer Networks</option>
                <option value="4">Period 4 (11:45 - 12:35) CS604: Database Systems</option>
                <option value="6">Period 5 (13:25 - 14:15) CS605: Software Engineering</option>
                <option value="7">Period 6 (14:15 - 15:05) CS606: Web Technologies</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-500 uppercase tracking-wider text-[11px]">Camera Face Match:</span>
              <select
                value={selectedTestStudent}
                onChange={(e) => setSelectedTestStudent(e.target.value)}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Biometric Auto-Recognition (SSA-SVM)</option>
                {students.map((st) => (
                  <option key={st.id} value={st.id}>
                    Assign Face to: {st.full_name} ({st.reg_no})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Video Aspect Canvas Area */}
          <div className="relative bg-slate-950 aspect-video flex items-center justify-center overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${isCameraActive ? "block" : "hidden"}`}
            />
            <canvas ref={canvasRef} className="hidden" />
            <canvas
              ref={overlayCanvasRef}
              className={`absolute inset-0 w-full h-full pointer-events-none ${isCameraActive ? "block" : "hidden"}`}
            />

            {!isCameraActive && (
              <div className="text-center p-8">
                <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-3">
                  <Camera className="w-8 h-8 text-slate-600" />
                </div>
                <p className="text-sm font-semibold text-slate-300">Classroom Camera Feed Idle</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm">
                  Click &apos;Start WebCam&apos; to stream camera feed, scan face embeddings, and register attendance directly in the database.
                </p>
              </div>
            )}

            {/* Overlay HUD Status */}
            <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur border border-white/10 px-3 py-1.5 rounded-lg text-[11px] text-white space-y-0.5">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${isCameraActive ? "bg-emerald-400 animate-pulse" : "bg-slate-400"}`}></span>
                <span className="font-mono">SSA-SVM + MOBILENET V2</span>
              </div>
              <p className="text-[10px] text-slate-400">Cosine Gating &tau; &le; 0.45</p>
            </div>

            {/* Real-time Status Message Toast */}
            {cameraFeedback && (
              <div className="absolute bottom-3 inset-x-3 bg-slate-900/90 backdrop-blur border border-indigo-500/40 text-white px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between shadow-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="truncate">{cameraFeedback}</span>
                </div>
                <button
                  onClick={() => setCameraFeedback(null)}
                  className="text-slate-400 hover:text-white text-[11px] ml-2 shrink-0"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>

          {/* Quick Attendance / Registration Verification Bar */}
          <div className="p-4 bg-slate-50 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                <span>Mark Attendance for Registered Students:</span>
              </span>
              {simulationMsg && (
                <span className="text-xs font-semibold text-indigo-700 truncate max-w-sm bg-indigo-50 px-2 py-0.5 rounded">
                  {simulationMsg}
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {students.length === 0 ? (
                <span className="text-xs text-slate-400">Loading student roster...</span>
              ) : (
                students.slice(0, 10).map((st) => (
                  <button
                    key={st.id}
                    disabled={isSimulating}
                    onClick={() => handleRecordStudent(st)}
                    className="px-2.5 py-1.5 bg-white border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 text-slate-700 font-semibold text-xs rounded-xl transition-all shadow-sm active:scale-95 disabled:opacity-50"
                  >
                    {st.full_name} ({st.reg_no})
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Col: Live Recognition Stream Feed */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[540px]">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-800">Live Attendance Events</h3>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full">
              REAL-TIME SYNC
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {liveEvents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                <Users className="w-10 h-10 mb-2 text-slate-300" />
                <p className="text-sm font-semibold text-slate-600">Awaiting Attendance Events</p>
                <p className="text-xs text-slate-400 mt-1">
                  Faces identified in camera feed or marked via student buttons will appear here and persist in database immediately.
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
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      ev.status === "PRESENT"
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
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
