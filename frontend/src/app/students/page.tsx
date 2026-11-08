"use client";

import React, { useEffect, useState, useRef } from "react";
import { apiRequest } from "@/lib/api";
import {
  Users,
  UserPlus,
  Camera,
  Cpu,
  CheckCircle,
  AlertCircle,
  Trash2,
  RefreshCw,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

interface Student {
  id: number;
  reg_no: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  class_section_id: number;
  has_embeddings: boolean;
  consent_given: boolean;
}

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSection, setFilterSection] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // New Student Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [regNo, setRegNo] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [sectionId, setSectionId] = useState(1);
  const [consentGiven, setConsentGiven] = useState(true);
  const [creating, setCreating] = useState(false);

  // Face Capture Modal
  const [captureStudent, setCaptureStudent] = useState<Student | null>(null);
  const [capturedImages, setCapturedImages] = useState<string[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [uploadingFaces, setUploadingFaces] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Model Retraining State
  const [training, setTraining] = useState(false);
  const [trainingMetrics, setTrainingMetrics] = useState<any>(null);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<Student[]>("/students/");
      setStudents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await apiRequest("/students/", {
        method: "POST",
        body: JSON.stringify({
          reg_no: regNo,
          first_name: firstName,
          last_name: lastName,
          email: email,
          class_section_id: Number(sectionId),
          consent_given: consentGiven,
        }),
      });
      setShowAddModal(false);
      setRegNo("");
      setFirstName("");
      setLastName("");
      setEmail("");
      fetchStudents();
    } catch (err: any) {
      alert(err.message || "Failed to create student");
    } finally {
      setCreating(false);
    }
  };

  const handleStartCapture = async (student: Student) => {
    setCaptureStudent(student);
    setCapturedImages([]);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 480, height: 480 },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCapturing(true);
      }
    } catch (err) {
      alert("Could not access webcam for biometric face capture.");
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth || 480;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
      setCapturedImages((prev) => [...prev, dataUrl]);
    }
  };

  const handleUploadEmbeddings = async () => {
    if (!captureStudent || capturedImages.length < 5) {
      alert("Please capture at least 5 face frames.");
      return;
    }
    setUploadingFaces(true);
    try {
      await apiRequest("/recognition/register-faces", {
        method: "POST",
        body: JSON.stringify({
          student_id: captureStudent.id,
          images_base64: capturedImages,
        }),
      });
      alert(`Face vectors successfully extracted and stored for ${captureStudent.full_name}. Retraining model to activate new facial profile...`);
      closeCaptureModal();
      await fetchStudents();
      // Auto train model so new embeddings are active
      try {
        const trainRes = await apiRequest<any>("/recognition/train", { method: "POST" });
        setTrainingMetrics(trainRes.metrics);
      } catch (te) {}
    } catch (err: any) {
      alert(err.message || "Failed to save embeddings");
    } finally {
      setUploadingFaces(false);
    }
  };

  const closeCaptureModal = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }
    setCaptureStudent(null);
    setCapturedImages([]);
    setIsCapturing(false);
  };

  const handleTrainModel = async () => {
    setTraining(true);
    setTrainingMetrics(null);
    try {
      const res = await apiRequest<any>("/recognition/train", {
        method: "POST",
      });
      setTrainingMetrics(res.metrics);
    } catch (err: any) {
      alert(err.message || "Training failed");
    } finally {
      setTraining(false);
    }
  };

  const handleDeleteStudent = async (student: Student) => {
    if (!confirm(`Are you sure you want to delete ${student.full_name} (${student.reg_no}) from the database?`)) {
      return;
    }
    try {
      await apiRequest(`/students/${student.id}`, { method: "DELETE" });
      fetchStudents();
    } catch (err: any) {
      alert(err.message || "Failed to delete student");
    }
  };

  return (
    <div className="space-y-6">
      {/* Title Bar & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Student Directory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage student registrations, capture biometric facial profiles, and train SSA-SVM
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleTrainModel}
            disabled={training}
            className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
          >
            <Cpu className="w-4 h-4" />
            <span>{training ? "Tuning with SSA..." : "Train SSA-SVM Model"}</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add Student</span>
          </button>
        </div>
      </div>

      {/* Metrics Banner (if just trained) */}
      {trainingMetrics && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-900 shadow-sm flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-6 h-6 text-emerald-600" />
            <div>
              <p className="text-sm font-bold">SSA-SVM Retrained Successfully!</p>
              <div className="flex flex-wrap gap-4 text-xs mt-1 text-emerald-800 font-medium">
                <span>Accuracy: {(trainingMetrics.accuracy * 100).toFixed(1)}%</span>
                <span>Precision: {(trainingMetrics.precision * 100).toFixed(1)}%</span>
                <span>Recall: {(trainingMetrics.recall * 100).toFixed(1)}%</span>
                <span>F1-Score: {(trainingMetrics.f1_score * 100).toFixed(1)}%</span>
                <span>CV Score: {(trainingMetrics.cv_score * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setTrainingMetrics(null)}
            className="text-xs text-emerald-600 font-bold hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Class-wise Filter & Search Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap">
            Filter Class Section:
          </label>
          <select
            value={filterSection}
            onChange={(e) => setFilterSection(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Class Sections</option>
            <option value="1">CSE-6A (Semester 6)</option>
            <option value="2">CSE-6B (Semester 6)</option>
          </select>
        </div>

        <div className="w-full md:w-72">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by student name or reg no..."
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Students List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Reg No</th>
                <th className="py-3 px-4">Full Name</th>
                <th className="py-3 px-4">Institutional Email</th>
                <th className="py-3 px-4">Class Section</th>
                <th className="py-3 px-4">Biometric Embeddings</th>
                <th className="py-3 px-4">Ethical Consent</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    Loading student directory...
                  </td>
                </tr>
              ) : students.filter((st) => {
                  const matchSection = !filterSection || String(st.class_section_id) === filterSection;
                  const matchSearch = !searchQuery || 
                    st.full_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                    st.reg_no.toLowerCase().includes(searchQuery.toLowerCase());
                  return matchSection && matchSearch;
                }).length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No students found matching current class section and search filters.
                  </td>
                </tr>
              ) : (
                students
                  .filter((st) => {
                    const matchSection = !filterSection || String(st.class_section_id) === filterSection;
                    const matchSearch = !searchQuery || 
                      st.full_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                      st.reg_no.toLowerCase().includes(searchQuery.toLowerCase());
                    return matchSection && matchSearch;
                  })
                  .map((st) => (
                  <tr key={st.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-700">
                      {st.reg_no}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-800">
                      {st.full_name}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{st.email}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-semibold font-mono text-[11px]">
                        {st.class_section_id === 2 ? "CSE-6B" : "CSE-6A"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {st.has_embeddings ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold text-[10px]">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          <span>Enrolled (Active)</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold text-[10px]">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          <span>No Embeddings</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center text-emerald-700 font-medium text-[11px]">
                        <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                        <span>Granted</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleStartCapture(st)}
                          className="px-3 py-1.5 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 font-semibold text-xs rounded-lg transition-colors flex items-center space-x-1.5"
                        >
                          <Camera className="w-3.5 h-3.5" />
                          <span>Capture Face</span>
                        </button>
                        <button
                          onClick={() => handleDeleteStudent(st)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                          title="Delete Student"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Student Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-100">
            <h3 className="font-bold text-base text-slate-800 mb-1">Register New Student</h3>
            <p className="text-xs text-slate-500 mb-4">Add profile details to class roster</p>

            <form onSubmit={handleCreateStudent} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                  Registration Number
                </label>
                <input
                  type="text"
                  required
                  value={regNo}
                  onChange={(e) => setRegNo(e.target.value)}
                  placeholder="e.g. 21CS011"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    required
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="John"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    required
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Doe"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="john.doe@college.edu"
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                  Class Section
                </label>
                <select
                  value={sectionId}
                  onChange={(e) => setSectionId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={1}>CSE-6A (Semester 6)</option>
                  <option value={2}>CSE-6B (Semester 6)</option>
                </select>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="consent"
                  checked={consentGiven}
                  onChange={(e) => setConsentGiven(e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="consent" className="text-xs text-slate-600">
                  Student provided biometric facial recognition consent
                </label>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl disabled:opacity-50"
                >
                  {creating ? "Saving..." : "Save Profile"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Face Capture Modal */}
      {captureStudent && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 border border-slate-100">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-bold text-base text-slate-800">
                  Face Capture: {captureStudent.full_name}
                </h3>
                <p className="text-xs text-slate-500 font-mono">Reg: {captureStudent.reg_no}</p>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg">
                {capturedImages.length} Frames Captured
              </span>
            </div>

            <div className="relative aspect-square bg-slate-950 rounded-2xl overflow-hidden mb-4 border border-slate-800 flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />

              {/* Face Guide Oval */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-56 h-72 border-2 border-dashed border-emerald-400 rounded-[50%] opacity-70"></div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={captureFrame}
                className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl flex items-center space-x-2 shadow"
              >
                <Camera className="w-4 h-4" />
                <span>Snap Face Frame ({capturedImages.length}/20)</span>
              </button>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={closeCaptureModal}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={capturedImages.length < 5 || uploadingFaces}
                  onClick={handleUploadEmbeddings}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl disabled:opacity-40 transition-all shadow"
                >
                  {uploadingFaces ? "Extracting Embeddings..." : "Save Embeddings"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
