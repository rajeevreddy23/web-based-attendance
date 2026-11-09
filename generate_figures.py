import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('conference_paper_figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9

# ==============================================================================
# FIGURE 1: Overall System Architecture
# ==============================================================================
fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 65)
ax.axis('off')

# Title banner
title_box = patches.FancyBboxPatch((2, 58), 96, 5.5, boxstyle="round,pad=0.3",
                                  facecolor='#1e293b', edgecolor='#0f172a', lw=1.5)
ax.add_patch(title_box)
ax.text(50, 60.75, "SYSTEM ARCHITECTURE: WEB-BASED PERIOD-WISE ATTENDANCE MANAGEMENT", 
        color='white', weight='bold', fontsize=11, ha='center', va='center')

# Layer 1: Hardware & Ingestion
l1_box = patches.FancyBboxPatch((3, 40), 26, 15, boxstyle="round,pad=0.4",
                                facecolor='#e0f2fe', edgecolor='#0284c7', lw=1.5)
ax.add_patch(l1_box)
ax.text(16, 52.5, "EDGE / CLIENT LAYER", color='#0369a1', weight='bold', fontsize=9, ha='center')
ax.text(16, 48.5, "- Classroom HD Webcam (1080p)\n- Real-Time Video Frame Stream\n- Client-Side Face Alignment HUD\n- Auto-Scan Trigger (2s Interval)",
        color='#0f172a', fontsize=7.5, ha='center', va='center')

# Layer 2: Biometric AI Pipeline
l2_box = patches.FancyBboxPatch((37, 40), 26, 15, boxstyle="round,pad=0.4",
                                facecolor='#ede9fe', edgecolor='#7c3aed', lw=1.5)
ax.add_patch(l2_box)
ax.text(50, 52.5, "BIOMETRIC AI ENGINE", color='#6d28d9', weight='bold', fontsize=9, ha='center')
ax.text(50, 48.5, "- Haar-Cascade Face ROI Detector\n- MobileNet-V2 Feature Extractor\n- 128-d L2-Normalized Vectors\n- SSA-Tuned SVM Classifier (C*, gamma*)\n- Cosine Distance Gating (tau <= 0.45)",
        color='#0f172a', fontsize=7.5, ha='center', va='center')

# Layer 3: Backend & Business Logic
l3_box = patches.FancyBboxPatch((71, 40), 26, 15, boxstyle="round,pad=0.4",
                                facecolor='#ecfdf5', edgecolor='#059669', lw=1.5)
ax.add_patch(l3_box)
ax.text(84, 52.5, "CORE SERVICE LAYER", color='#047857', weight='bold', fontsize=9, ha='center')
ax.text(84, 48.5, "- FastAPI Asynchronous Server\n- Period-Wise Timetable Resolver\n- Strict Duplicate Check Filter\n- WebSocket Real-Time Broadcast\n- JWT Role Authentication",
        color='#0f172a', fontsize=7.5, ha='center', va='center')

# Layer 4: Storage & Presentation
l4_box1 = patches.FancyBboxPatch((15, 12), 32, 20, boxstyle="round,pad=0.4",
                                 facecolor='#fef3c7', edgecolor='#d97706', lw=1.5)
ax.add_patch(l4_box1)
ax.text(31, 29, "CENTRALIZED STORAGE (SQLite/PostgreSQL)", color='#b45309', weight='bold', fontsize=8.5, ha='center')
ax.text(31, 21, "- Students Master Roster (ID, Name, Dept)\n- Biometric Embeddings (128-d Floating Vectors)\n- Timetable Slots (Period 1-6, Section A/B)\n- Attendance Records (student_id, date, period_id)\n- Audit Logs & Manual Correction Trail",
        color='#0f172a', fontsize=7.5, ha='center', va='center')

l4_box2 = patches.FancyBboxPatch((55, 12), 32, 20, boxstyle="round,pad=0.4",
                                 facecolor='#f1f5f9', edgecolor='#475569', lw=1.5)
ax.add_patch(l4_box2)
ax.text(71, 29, "WEB DASHBOARD & REPORTING (Next.js 14)", color='#334155', weight='bold', fontsize=8.5, ha='center')
ax.text(71, 21, "- Real-Time Camera HUD & Face Box Overlay\n- Active Period & Section Roster Display\n- Faculty Manual Attendance Corrections\n- Biometric Student Registration Modal\n- Automated Excel (.xlsx) Report Export",
        color='#0f172a', fontsize=7.5, ha='center', va='center')

# Arrows
ax.annotate('', xy=(37, 47.5), xytext=(29, 47.5),
            arrowprops=dict(facecolor='#0284c7', edgecolor='#0284c7', width=2, headwidth=8))
ax.annotate('', xy=(71, 47.5), xytext=(63, 47.5),
            arrowprops=dict(facecolor='#7c3aed', edgecolor='#7c3aed', width=2, headwidth=8))
ax.annotate('', xy=(31, 32), xytext=(84, 40),
            arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=2, headwidth=8))
ax.annotate('', xy=(55, 22), xytext=(47, 22),
            arrowprops=dict(facecolor='#d97706', edgecolor='#d97706', width=2, headwidth=8))
ax.annotate('', xy=(71, 32), xytext=(84, 40),
            arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=2, headwidth=8))

# Subtitle / caption in diagram
ax.text(50, 4, "Figure 1: High-level architectural schema showing edge capture, ML pipeline, FastAPI services, and web dashboard.",
        fontsize=8.5, style='italic', ha='center', color='#334155')

plt.tight_layout()
fig.savefig('conference_paper_figures/fig1_system_architecture.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 1")

# ==============================================================================
# FIGURE 2: MobileNet-V2 & SSA-SVM Feature Extraction Pipeline
# ==============================================================================
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis('off')

boxes = [
    (2, "Video Frame\n(1920x1080 RGB)", "#e0f2fe", "#0284c7"),
    (18, "Face ROI Detection\n(Haar / Crop)", "#f0fdf4", "#16a34a"),
    (34, "Resize & Normalize\n(160x160 pixels)", "#fef3c7", "#d97706"),
    (50, "MobileNet-V2\nInverted Residuals", "#ede9fe", "#7c3aed"),
    (66, "128-d Vector\nL2 Normalization", "#fce7f3", "#db2777"),
    (82, "SSA-SVM Classifier\nIdentity Match", "#ffedd5", "#ea580c")
]

for x, text, bg, border in boxes:
    p = patches.FancyBboxPatch((x, 18), 14, 18, boxstyle="round,pad=0.3",
                              facecolor=bg, edgecolor=border, lw=1.5)
    ax.add_patch(p)
    ax.text(x + 7, 27, text, ha='center', va='center', fontsize=8, weight='bold', color='#1e293b')

for i in range(len(boxes) - 1):
    x_start = boxes[i][0] + 14
    x_end = boxes[i+1][0]
    ax.annotate('', xy=(x_end, 27), xytext=(x_start, 27),
                arrowprops=dict(facecolor='#475569', edgecolor='#475569', width=1.8, headwidth=6))

# SSA Tuning callout box
callout = patches.FancyBboxPatch((50, 4), 30, 9, boxstyle="round,pad=0.2",
                                facecolor='#f8fafc', edgecolor='#64748b', lw=1, ls='--')
ax.add_patch(callout)
ax.text(65, 8.5, "Sparrow Search Optimization (SSA)\nOptimal Hyperparameters: C* = 10.0, gamma* = 0.01\nCosine Distance Rejection Gate: tau <= 0.45",
        ha='center', va='center', fontsize=7, color='#334155')

ax.annotate('', xy=(89, 18), xytext=(78, 13),
            arrowprops=dict(facecolor='#ea580c', edgecolor='#ea580c', width=1, headwidth=5))

ax.text(50, 46, "FACIAL FEATURE EXTRACTION AND CLASSIFICATION PIPELINE",
        ha='center', va='center', fontsize=10, weight='bold', color='#0f172a')
ax.text(50, 42, "Mathematical workflow from raw video frame ingestion to student identity prediction",
        ha='center', va='center', fontsize=8, color='#475569')

plt.tight_layout()
fig.savefig('conference_paper_figures/fig2_feature_extraction_pipeline.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 2")

# ==============================================================================
# FIGURE 3: Period-Wise Attendance & Duplicate Prevention Flowchart
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Title
ax.text(50, 97, "PERIOD-WISE ATTENDANCE LOGIC & DUPLICATE SUPPRESSION",
        ha='center', va='center', fontsize=10.5, weight='bold', color='#0f172a')

# Step 1: Start
p1 = patches.FancyBboxPatch((35, 87), 30, 6, boxstyle="round,pad=0.5", facecolor='#e2e8f0', edgecolor='#475569', lw=1.5)
ax.add_patch(p1)
ax.text(50, 90, "Start: Web Camera Feed Ingestion", ha='center', va='center', fontsize=8, weight='bold')

# Step 2: Facial Recognition
p2 = patches.FancyBboxPatch((32, 74), 36, 7, boxstyle="round,pad=0.3", facecolor='#e0f2fe', edgecolor='#0284c7', lw=1.5)
ax.add_patch(p2)
ax.text(50, 77.5, "Detect Face & Extract 128-d Embedding\nPredict Student ID via SSA-SVM", ha='center', va='center', fontsize=7.5)

# Step 3: Confidence check Diamond
p3 = patches.Polygon([[50, 68], [68, 62], [50, 56], [32, 62]], facecolor='#fef3c7', edgecolor='#d97706', lw=1.5)
ax.add_patch(p3)
ax.text(50, 62, "Cosine Metric\ntau <= 0.45?", ha='center', va='center', fontsize=7.5, weight='bold')

# Reject branch
p_rej = patches.FancyBboxPatch((76, 59), 21, 6, boxstyle="round,pad=0.3", facecolor='#fee2e2', edgecolor='#dc2626', lw=1.5)
ax.add_patch(p_rej)
ax.text(86.5, 62, "Unknown Face / Ignore\nLog Unregistered Frame", ha='center', va='center', fontsize=6.8, color='#991b1b')

# Step 4: Resolve Active Timetable Period
p4 = patches.FancyBboxPatch((30, 44), 40, 7, boxstyle="round,pad=0.3", facecolor='#ede9fe', edgecolor='#7c3aed', lw=1.5)
ax.add_patch(p4)
ax.text(50, 47.5, "Resolve Timetable Slot\nCurrent Time -> Period P_k, Subject S_j, Section C_m", ha='center', va='center', fontsize=7.5)

# Step 5: Duplicate check Diamond
p5 = patches.Polygon([[50, 39], [70, 32], [50, 25], [30, 32]], facecolor='#fef3c7', edgecolor='#d97706', lw=1.5)
ax.add_patch(p5)
ax.text(50, 32, "Duplicate in DB?\n(stud_id, date, P_k)", ha='center', va='center', fontsize=7.2, weight='bold')

# Duplicate suppressed box
p_dup = patches.FancyBboxPatch((76, 29), 21, 6, boxstyle="round,pad=0.3", facecolor='#fef9c3', edgecolor='#ca8a04', lw=1.5)
ax.add_patch(p_dup)
ax.text(86.5, 32, "Duplicate Suppressed\nWebSocket Event Sent", ha='center', va='center', fontsize=6.8, color='#854d0e')

# Step 6: Mark Attendance
p6 = patches.FancyBboxPatch((28, 12), 44, 8, boxstyle="round,pad=0.3", facecolor='#dcfce7', edgecolor='#16a34a', lw=1.5)
ax.add_patch(p6)
ax.text(50, 16, "INSERT Attendance Record in DB\nStatus='PRESENT', Timestamp, Period ID\nBroadcast 'attendance_recorded' Event to HUD", ha='center', va='center', fontsize=7.2, weight='bold', color='#14532d')

# Step 7: End
p7 = patches.FancyBboxPatch((38, 2), 24, 5, boxstyle="round,pad=0.5", facecolor='#e2e8f0', edgecolor='#475569', lw=1.5)
ax.add_patch(p7)
ax.text(50, 4.5, "End Cycle / Wait 2s", ha='center', va='center', fontsize=7.5, weight='bold')

# Arrows
ax.annotate('', xy=(50, 81), xytext=(50, 87), arrowprops=dict(facecolor='#475569', width=1.5, headwidth=5))
ax.annotate('', xy=(50, 68), xytext=(50, 74), arrowprops=dict(facecolor='#475569', width=1.5, headwidth=5))
ax.annotate('', xy=(50, 51), xytext=(50, 56), arrowprops=dict(facecolor='#16a34a', width=1.5, headwidth=5))
ax.text(52, 53, "YES", fontsize=7, color='#16a34a', weight='bold')
ax.annotate('', xy=(76, 62), xytext=(68, 62), arrowprops=dict(facecolor='#dc2626', width=1.5, headwidth=5))
ax.text(70, 63.5, "NO", fontsize=7, color='#dc2626', weight='bold')
ax.annotate('', xy=(50, 39), xytext=(50, 44), arrowprops=dict(facecolor='#475569', width=1.5, headwidth=5))
ax.annotate('', xy=(50, 20), xytext=(50, 25), arrowprops=dict(facecolor='#16a34a', width=1.5, headwidth=5))
ax.text(52, 22, "NO (New)", fontsize=7, color='#16a34a', weight='bold')
ax.annotate('', xy=(76, 32), xytext=(70, 32), arrowprops=dict(facecolor='#ca8a04', width=1.5, headwidth=5))
ax.text(71, 33.5, "YES (Exists)", fontsize=7, color='#ca8a04', weight='bold')
ax.annotate('', xy=(50, 7), xytext=(50, 12), arrowprops=dict(facecolor='#475569', width=1.5, headwidth=5))

plt.tight_layout()
fig.savefig('conference_paper_figures/fig3_period_attendance_flowchart.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 3")

# ==============================================================================
# FIGURE 4: Web Dashboard Live Camera HUD Mockup
# ==============================================================================
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 70)
ax.axis('off')

# Outer Window
win = patches.FancyBboxPatch((2, 2), 96, 66, boxstyle="round,pad=0.5", facecolor='#0f172a', edgecolor='#334155', lw=2)
ax.add_patch(win)

# Header Bar
head = patches.Rectangle((2, 62), 96, 6, facecolor='#1e293b', edgecolor='none')
ax.add_patch(head)
ax.text(6, 65, "MBU Attendance Portal | Period-Wise Face Recognition HUD", color='white', weight='bold', fontsize=9, va='center')
ax.text(92, 65, "[ Faculty: Dr. K. Hari Krishna ]", color='#94a3b8', fontsize=8, va='center', ha='right')

# Video Viewport (Left)
video_box = patches.Rectangle((6, 12), 52, 46, facecolor='#000000', edgecolor='#38bdf8', lw=1.5)
ax.add_patch(video_box)
ax.text(32, 54, "LIVE OPTICAL CAMERA FEED [1080p @ 30 FPS]", color='#38bdf8', fontsize=8, ha='center', weight='bold')

# Simulated Face Bounding Box
face_bbox = patches.Rectangle((22, 22), 20, 24, facecolor='none', edgecolor='#22c55e', lw=2.5, ls='-')
ax.add_patch(face_bbox)
# Corner marks
for cx, cy in [(22, 22), (42, 22), (22, 46), (42, 46)]:
    cmark = patches.Circle((cx, cy), 1, facecolor='#4ade80', edgecolor='none')
    ax.add_patch(cmark)

# HUD Label above face box
tag = patches.Rectangle((21.5, 46.5), 21, 5, facecolor='#22c55e', edgecolor='none')
ax.add_patch(tag)
ax.text(32, 49, "23102A040066 | S. Manaswini", color='#052e16', fontsize=7, weight='bold', ha='center', va='center')

# Confidence Badge inside video
badge = patches.FancyBboxPatch((8, 14), 22, 4.5, boxstyle="round,pad=0.2", facecolor='#1e293b', edgecolor='#22c55e', lw=1)
ax.add_patch(badge)
ax.text(19, 16.25, "Confidence: 98.4% (tau=0.21)", color='#4ade80', fontsize=6.8, ha='center', va='center', weight='bold')

# Right Panel: Controls & Live Roster
ctrl_box = patches.Rectangle((61, 12), 33, 46, facecolor='#1e293b', edgecolor='#334155', lw=1)
ax.add_patch(ctrl_box)
ax.text(77.5, 54.5, "SESSION CONTROL & ROSTER", color='white', weight='bold', fontsize=8, ha='center')

# Dropdown badges
d1 = patches.FancyBboxPatch((63, 46), 14, 5, boxstyle="round,pad=0.2", facecolor='#334155', edgecolor='none')
ax.add_patch(d1)
ax.text(70, 48.5, "Sec: CSE-6A", color='white', fontsize=7, ha='center', va='center')

d2 = patches.FancyBboxPatch((78, 46), 14, 5, boxstyle="round,pad=0.2", facecolor='#334155', edgecolor='none')
ax.add_patch(d2)
ax.text(85, 48.5, "Period: 1 (09:00)", color='white', fontsize=7, ha='center', va='center')

# Live Roster Items
roster = [
    ("23102A040066", "Sali Manaswini", "PRESENT", "#22c55e"),
    ("23102A040021", "P. Sri Sambhava", "PRESENT", "#22c55e"),
    ("23102A040044", "K. Lohith Kumar", "PENDING", "#eab308"),
    ("23102A040051", "Y. Gnanendra", "PENDING", "#eab308"),
    ("23102A040070", "I. Veerendra Sehwag", "PENDING", "#eab308")
]

y_pos = 38
for rid, rname, rstat, col in roster:
    rbox = patches.FancyBboxPatch((63, y_pos), 29, 5, boxstyle="round,pad=0.2", facecolor='#0f172a', edgecolor='#334155', lw=0.8)
    ax.add_patch(rbox)
    ax.text(65, y_pos + 2.5, f"{rid}\n{rname[:13]}", color='#94a3b8', fontsize=6, va='center')
    sbadge = patches.FancyBboxPatch((84, y_pos + 1), 7.5, 3, boxstyle="round,pad=0.1", facecolor=col, edgecolor='none')
    ax.add_patch(sbadge)
    ax.text(87.75, y_pos + 2.5, rstat, color='white' if col != '#eab308' else '#713f12', fontsize=5.5, weight='bold', ha='center', va='center')
    y_pos -= 6

# Bottom Action Toolbar
btn1 = patches.FancyBboxPatch((6, 5), 18, 5, boxstyle="round,pad=0.2", facecolor='#2563eb', edgecolor='none')
ax.add_patch(btn1)
ax.text(15, 7.5, "[ Take Attendance ]", color='white', weight='bold', fontsize=7, ha='center', va='center')

btn2 = patches.FancyBboxPatch((26, 5), 16, 5, boxstyle="round,pad=0.2", facecolor='#16a34a', edgecolor='none')
ax.add_patch(btn2)
ax.text(34, 7.5, "[ Auto-Scan: ON ]", color='white', weight='bold', fontsize=7, ha='center', va='center')

btn3 = patches.FancyBboxPatch((61, 5), 33, 5, boxstyle="round,pad=0.2", facecolor='#059669', edgecolor='none')
ax.add_patch(btn3)
ax.text(77.5, 7.5, "[ Export Excel Report (.xlsx) ]", color='white', weight='bold', fontsize=7, ha='center', va='center')

plt.tight_layout()
fig.savefig('conference_paper_figures/fig4_web_dashboard_hud.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 4")

# ==============================================================================
# FIGURE 5: Comparative Recognition Performance Chart
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

# Chart 1: Accuracy across angles
angles = ['0 deg (Frontal)', '15 deg (Slight)', '30 deg (Moderate)', '45 deg (Extreme)']
x = np.arange(len(angles))
width = 0.2

ssa_svm = [99.2, 98.4, 96.1, 93.8]
std_svm = [95.0, 93.2, 89.5, 84.1]
knn_acc = [92.1, 89.4, 85.0, 78.6]
cnn_acc = [96.5, 95.1, 92.4, 87.9]

ax1.bar(x - 1.5*width, ssa_svm, width, label='MobileNet+SSA-SVM (Proposed)', color='#2563eb')
ax1.bar(x - 0.5*width, cnn_acc, width, label='Standard CNN Classifier', color='#059669')
ax1.bar(x + 0.5*width, std_svm, width, label='Standard RBF-SVM', color='#d97706')
ax1.bar(x + 1.5*width, knn_acc, width, label='K-Nearest Neighbors (k=5)', color='#dc2626')

ax1.set_ylabel('Recognition Accuracy (%)', weight='bold', fontsize=8.5)
ax1.set_title('(a) Accuracy vs. Camera Viewing Angles', weight='bold', fontsize=9)
ax1.set_xticks(x)
ax1.set_xticklabels(angles, fontsize=7.5, rotation=15)
ax1.set_ylim(70, 102)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
ax1.legend(fontsize=7, loc='lower left')

# Chart 2: Metric Performance Under Variable Lighting & Occlusion
conditions = ['Normal Light', 'Low Light (100 lx)', 'High Glare (800 lx)', 'Mask/Glasses', 'Motion Blur']
f1_ssa = [99.1, 96.5, 95.8, 93.4, 91.8]
f1_svm = [94.5, 89.2, 88.0, 84.1, 81.5]

xc = np.arange(len(conditions))
w2 = 0.35
ax2.bar(xc - w2/2, f1_ssa, w2, label='Proposed SSA-SVM', color='#2563eb')
ax2.bar(xc + w2/2, f1_svm, w2, label='Baseline SVM', color='#94a3b8')

ax2.set_ylabel('F1-Score (%)', weight='bold', fontsize=8.5)
ax2.set_title('(b) Robustness Under Environmental Stress', weight='bold', fontsize=9)
ax2.set_xticks(xc)
ax2.set_xticklabels(conditions, fontsize=7.5, rotation=20)
ax2.set_ylim(75, 102)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.legend(fontsize=7, loc='lower left')

plt.tight_layout()
fig.savefig('conference_paper_figures/fig5_performance_comparison.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 5")

# ==============================================================================
# FIGURE 6: Period-Wise Attendance & Duplicate Suppression Statistics
# ==============================================================================
fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)

periods = ['Period 1\n(09:00-09:50)', 'Period 2\n(09:50-10:40)', 'Period 3\n(10:55-11:45)', 
           'Period 4\n(11:45-12:35)', 'Period 5\n(13:25-14:15)', 'Period 6\n(14:15-15:05)']
x_p = np.arange(len(periods))
w = 0.35

verified_attend = [60, 59, 58, 60, 57, 58] # Total students verified present
dup_prevented = [142, 118, 126, 134, 110, 115] # Repeated scans suppressed by DB check

b1 = ax.bar(x_p - w/2, verified_attend, w, label='Unique Student Attendance Registered', color='#16a34a')
b2 = ax.bar(x_p + w/2, dup_prevented, w, label='Duplicate Camera Scans Blocked', color='#f59e0b')

for rect in b1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 2, f'{int(h)}', ha='center', va='bottom', fontsize=7.5, weight='bold')

for rect in b2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 2, f'{int(h)}', ha='center', va='bottom', fontsize=7.5, weight='bold')

ax.set_ylabel('Transaction Count', weight='bold', fontsize=9)
ax.set_title('Period-Wise Attendance Verification vs. Redundant Scans Blocked (N=60 Students)', weight='bold', fontsize=9.5)
ax.set_xticks(x_p)
ax.set_xticklabels(periods, fontsize=7.5)
ax.set_ylim(0, 170)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend(fontsize=8, loc='upper right')

plt.tight_layout()
fig.savefig('conference_paper_figures/fig6_period_attendance_analytics.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Generated Fig 6")
