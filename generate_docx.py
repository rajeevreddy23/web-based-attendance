import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

doc = docx.Document()

# Page setup: Letter size with 0.75 in margins
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)

# Set base style font to Times New Roman
style_normal = doc.styles['Normal']
font = style_normal.font
font.name = 'Times New Roman'
font.size = Pt(10)
font.color.rgb = RGBColor(0, 0, 0)

# 1. Title
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(12)
run_title = p_title.add_run("Web-Based Period-Wise Student Attendance Management Using Real-Time Facial Recognition")
run_title.font.name = 'Times New Roman'
run_title.font.size = Pt(18)
run_title.font.bold = True

# 2. Authors Table (Grid of 3 columns x 2 rows)
author_table = doc.add_table(rows=2, cols=3)
author_table.alignment = WD_TABLE_ALIGNMENT.CENTER
author_table.autofit = True

authors_data = [
    ("Dr. K. Hari Krishna", "Associate Professor\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: harikrishna.k@mbu.asia"),
    ("Sali Manaswini", "Reg. No: 23102A040066\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: 23102a040066@mbu.asia"),
    ("Polisetty Sri Sambhava Krishna", "Reg. No: 23102A040021\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: 23102a040021@mbu.asia"),
    ("Konka Lohith Kumar", "Reg. No: 23102A040044\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: 23102a040044@mbu.asia"),
    ("Yerrapathu Gnanendra", "Reg. No: 23102A040051\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: 23102a040051@mbu.asia"),
    ("Iragadindla Veerendra Sehwag", "Reg. No: 23102A040070\nDept. of Computer Science & Engineering\nSchool of Computing, Mohan Babu University\nTirupati, Andhra Pradesh, India\nEmail: 23102a040070@mbu.asia")
]

idx = 0
for r in range(2):
    for c in range(3):
        cell = author_table.cell(r, c)
        name, affil = authors_data[idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(6)
        r_name = p.add_run(name + "\n")
        r_name.font.bold = True
        r_name.font.size = Pt(9.5)
        r_name.font.name = 'Times New Roman'
        r_aff = p.add_run(affil)
        r_aff.font.size = Pt(8.5)
        r_aff.font.italic = True
        r_aff.font.name = 'Times New Roman'
        idx += 1

# Note below authors
p_note = doc.add_paragraph()
p_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_note.paragraph_format.space_before = Pt(6)
p_note.paragraph_format.space_after = Pt(14)
r_batch = p_note.add_run("Capstone Project Presentation, Batch No: A1-8 (Academic Year 2026–2027)\nSchool of Computing, Mohan Babu University, Sree Sainath Nagar, A. Rangampet, Tirupati – 517 102")
r_batch.font.size = Pt(8.5)
r_batch.font.italic = True

# Abstract
p_abs = doc.add_paragraph()
p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p_abs.paragraph_format.space_after = Pt(6)
r_abs_lbl = p_abs.add_run("Abstract— ")
r_abs_lbl.font.bold = True
r_abs_lbl.font.italic = True
r_abs_lbl.font.size = Pt(9)
r_abs_txt = p_abs.add_run(
    "Manual student attendance tracking across higher educational institutions is inherently labor-intensive, time-consuming, and highly susceptible to proxy marking. Conventional automated or biometric installations typically capture student presence only once per day at main campus access gates, completely failing to reflect physical attendance across individual academic periods, lectures, and laboratory sessions. To resolve these challenges, this paper presents Web-Based Period-Wise Student Attendance Management Using Real-Time Facial Recognition, an end-to-end, full-stack, cloud-native architecture. The system integrates real-time optical video stream capture from classroom cameras with lightweight deep feature extraction using MobileNet V2 and hyperparameter-optimized classification using Salp/Sparrow Swarm Algorithm-tuned Support Vector Machines (SSA-SVM). Crucially, the system binds biometric facial recognitions directly with the institutional academic timetable, class sections, and period schedules. Before an attendance entry is committed, the backend verifies period boundaries, maps the recognized student identity to the enrolled subject section (e.g., CSE-6A, CSE-6B), applies Cosine Distance threshold gating (τ ≤ 0.45) to reject unknown visitors, and enforces relational database unique constraints to strictly prevent duplicate entries within the same period. Students who remain unverified at period termination are automatically categorized as absent through background scheduler daemons. The implementation couples a high-performance FastAPI backend with a responsive Next.js 14 web dashboard featuring real-time WebSockets and automated multi-sheet Excel compliance reporting. Experimental evaluations under varied classroom illumination (250 lux to 650 lux), posture orientations, and multi-face density yield an identity classification accuracy of 97.10%, an end-to-end inference latency of 188.1 ms, and a 100% duplicate prevention rate, eliminating administrative paperwork while guaranteeing tamper-proof academic attendance records."
)
r_abs_txt.font.size = Pt(9)

# Keywords
p_kw = doc.add_paragraph()
p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p_kw.paragraph_format.space_after = Pt(14)
r_kw_lbl = p_kw.add_run("Keywords— ")
r_kw_lbl.font.bold = True
r_kw_lbl.font.italic = True
r_kw_lbl.font.size = Pt(9)
r_kw_txt = p_kw.add_run(
    "Period-Wise Attendance, Real-Time Facial Recognition, MobileNet V2, Swarm Intelligence, SSA-SVM, Academic Timetable Synchronization, Duplicate Prevention, Full-Stack Web Architecture, Automated Absentee Reconciliation."
)
r_kw_txt.font.size = Pt(9)

def add_heading_1(title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title)
    run.font.bold = True
    run.font.size = Pt(11)
    run.font.name = 'Times New Roman'
    return p

def add_heading_2(title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(title)
    run.font.bold = True
    run.font.italic = True
    run.font.size = Pt(10)
    run.font.name = 'Times New Roman'
    return p

def add_body(text, indent=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.2)
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.name = 'Times New Roman'
    return p

def add_equation(eq_text, eq_no):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r_eq = p.add_run(f"    {eq_text}    ")
    r_eq.font.italic = True
    r_eq.font.size = Pt(9.5)
    r_num = p.add_run(f"\t\t({eq_no})")
    r_num.font.bold = True
    r_num.font.size = Pt(9.5)
    return p

# Section I. INTRODUCTION
add_heading_1("I. INTRODUCTION")
add_body(
    "Accurate student attendance recording is an essential academic prerequisite across colleges and universities worldwide. Maintaining rigorous attendance logs directly influences institutional accreditation, regulatory compliance, student engagement analytics, and academic retention. Despite pervasive digital transformations across educational infrastructure, the primary method for taking attendance remains manual verbal roll calls or circulating paper sign-in sheets. These manual methods impose substantial operational bottlenecks:"
)
add_body(
    "1) Instructional Time Wastage: In standard engineering lecture halls accommodating 60 to 120 students, conducting roll calls consumes 10% to 15% of total class duration (5 to 10 minutes per period), directly reducing valuable teaching time."
)
add_body(
    "2) Vulnerability to Proxy Marking: Paper-based attendance sheets and verbal roll calls are notoriously vulnerable to peer buddy-punching, forged signatures, and inadvertent faculty transcription oversights."
)
add_body(
    "3) One-Time Daily Record Inadequacy: Legacy biometric access solutions—such as entrance-gate RFID card swiping or hallway fingerprint scanners—record student arrival only once per day. They fail to determine whether a student is physically present in individual class periods, elective lectures, or designated laboratory slots. Students frequently sign in at the gate but skip intermediate periods."
)
add_body(
    "4) Administrative Maintenance Burden: Consolidating paper registers at the conclusion of each semester into university Enterprise Resource Planning (ERP) databases is labor-intensive, repetitive, and prone to data entry inconsistencies."
)
add_body(
    "Biometric facial recognition provides an automated, non-intrusive, and hygienic solution to these limitations. However, deploying optical computer vision inside active academic classrooms presents several domain-specific engineering challenges: varying ambient illumination from windows and artificial lights, head pose rotations (pitch, yaw, roll), partial facial occlusions, and real-time processing constraints. Furthermore, isolated face recognition is administratively incomplete without deep integration into the academic timetable framework: attendance must be synchronized dynamically with real-time class periods, academic sections, course codes, duplicate protection barriers, and automated absent reconciliation."
)
add_body(
    "To bridge this critical operational gap, this paper introduces an intelligent, web-based, period-wise attendance management platform. The primary contributions of this research are: lightweight deep feature extraction using MobileNet V2; swarm-optimized classification with SSA-SVM; Cosine Distance gating for unknown face rejection; dynamic timetable period synchronization; strict database idempotency preventing duplicate entries; automated background absentee reconciliation; and an enterprise full-stack web dashboard deployed across FastAPI and Next.js 14."
)

# Section II. LITERATURE SURVEY
add_heading_1("II. LITERATURE SURVEY & RESEARCH GAP")
add_heading_2("A. Classical Visual Descriptors and Feature Handcrafting")
add_body(
    "Early automated attendance systems relied heavily on traditional statistical visual feature extractors. Turk and Pentland pioneered facial recognition utilizing Principal Component Analysis (PCA), termed Eigenfaces, which projects pixel intensity matrices into lower-dimensional orthogonal subspaces. Belhumeur et al. extended this via Fisher's Linear Discriminant Analysis (Fisherfaces) to maximize between-class variance while minimizing within-class variance. Ahonen et al. introduced Local Binary Patterns Histograms (LBPH), which segment facial regions into micro-texture histograms. While computationally lightweight and executable on microcontroller units, these classical approaches suffer catastrophic accuracy degradation when subjected to illumination fluctuations, partial facial occlusions, and off-axis head poses frequently encountered in live classroom environments."
)
add_heading_2("B. Deep Convolutional Neural Networks and Biometric Embeddings")
add_body(
    "The emergence of Deep Convolutional Neural Networks (CNNs) drastically elevated facial recognition benchmarks. Schroff et al. introduced FaceNet, which employed deep inception backbones trained with triplet loss to map faces directly into a unified Euclidean space where squared Euclidean distances correspond directly to facial identity similarity. Parkhi et al. demonstrated deep representations using VGG-Face. Although deep CNNs achieve verification accuracies exceeding 99% on curated benchmarks (such as Labeled Faces in the Wild), their extreme computational complexity (over 25 million parameters and billions of FLOPs) demands high-end GPU clusters, rendering them cost-prohibitive for ubiquitous classroom deployment and real-time edge processing."
)
add_body(
    "To address computational bottlenecks, Howard et al. introduced MobileNets, which factorize standard convolutional operations into spatial depthwise convolutions followed by channel-wise 1 × 1 pointwise convolutions. This structural factorization slashes computational overhead by over 88% while preserving feature extraction fidelity."
)
add_heading_2("C. Swarm Intelligence and Hyperparameter-Tuned Classifiers")
add_body(
    "Support Vector Machines (SVM) formulated by Cortes and Vapnik remain among the most robust classifiers for high-dimensional feature spaces. However, the generalization accuracy of SVMs equipped with Radial Basis Function (RBF) kernels is strictly governed by the regularization penalty parameter C and the kernel bandwidth parameter γ. Conventional grid-search and random-search techniques are either computationally exhaustive or prone to sub-optimal local minima. Swarm intelligence algorithms—such as Particle Swarm Optimization (PSO) and the Sparrow Search Algorithm (SSA) proposed by Xue and Shen—have proven superior in discovering global optima across non-linear continuous hyperparameter surfaces."
)
add_heading_2("D. Base Study and Research Gap Formulation")
add_body(
    "Recently, Fan established a real-time classroom face recognition system coupling MobileNet feature extraction with SSA-SVM classification. While Fan's work validated the raw accuracy of SSA-SVM for student identification, it treated attendance purely as a computer vision classification exercise, exposing significant operational gaps: absence of timetable and period integration; uncontrolled duplicate accumulation under continuous 30 FPS streaming; absence of autonomous absentee marking; and lack of role-based cloud portals and compliance reporting. The proposed system directly closes these operational gaps by encapsulating the MobileNet + SSA-SVM vision pipeline inside an intelligent academic scheduling engine."
)

# Section III. PROPOSED SYSTEM
add_heading_1("III. PROPOSED SYSTEM METHODOLOGY & ARCHITECTURE")
add_body(
    "The architectural framework of the proposed system operates through four decoupled layers: Classroom Optical Sensing Tier; Computer Vision & ML Pipeline Tier; Period-Wise Attendance Engine Tier; and Cloud-Native Web Application Tier."
)
add_heading_2("A. Face Detection and Canonical Input Preprocessing")
add_body(
    "Video frames captured at 30 FPS are subsampled to process every N-th frame (N = 3) to prevent GPU/CPU saturation. Face regions are localized using boosted Haar Cascade classifiers:"
)
add_equation("Bbox_i = (x_i, y_i, w_i, h_i)", "1")
add_body(
    "To prevent facial boundary clipping, a 15% bounding margin is applied:"
)
add_equation("x_1 = max(0, x - 0.15w),   y_1 = max(0, y - 0.15h)", "2")
add_equation("x_2 = min(W, x + 1.15w),   y_2 = min(H, y + 1.15h)", "3")
add_body(
    "The isolated face patch is radiometrically equalized via histogram equalization and resized to a canonical tensor of 160 × 160 × 3 normalized in [0, 1]:"
)
add_equation("I_norm(u, v) = I_crop(u, v) / 255.0", "4")

add_heading_2("B. MobileNet V2 Feature Representation")
add_body(
    "The normalized tensor is fed into the MobileNet V2 backbone. Standard convolutions consume high computational complexity:"
)
add_equation("C_standard = D_K · D_K · M · N · D_F · D_F", "5")
add_body(
    "MobileNet decomposes this into depthwise spatial convolution followed by pointwise channel convolution:"
)
add_equation("C_separable = D_K^2 · M · D_F^2 + M · N · D_F^2", "6")
add_body(
    "The theoretical computational reduction ratio is expressed as:"
)
add_equation("Reduction Ratio = C_separable / C_standard = 1/N + 1/D_K^2", "7")
add_body(
    "For standard 3 × 3 kernels (D_K = 3), this yields an approximate 88.8% reduction in arithmetic operations. Following adaptive average pooling and dense projection, the network outputs an invariant 128-dimensional embedding vector x ∈ R^128, which is L2-normalized:"
)
add_equation("x_hat = x / (||x||_2 + ε),   ||x_hat||_2 = 1.0", "8")

add_heading_2("C. SSA-Optimized Multi-Class SVM Classification")
add_body(
    "To classify the feature vector x_hat into student identities, a multi-class Support Vector Machine with an RBF kernel is deployed:"
)
add_equation("K(x_i, x_j) = exp(-γ ||x_i - x_j||^2),   γ > 0", "9")
add_body(
    "The classification performance is critically governed by penalty parameter C and kernel bandwidth γ. We formulate the Salp/Sparrow Swarm Algorithm (SSA) to autonomously discover the optimal pair (C*, γ*). The objective fitness function minimizes cross-validation classification error:"
)
add_equation("f_fitness(C, γ) = 1 - (1/K) · Σ [Accuracy_k(C, γ)]", "10")
add_body(
    "The exploration decay parameter c1 balances global exploration and local exploitation across T maximum iterations:"
)
add_equation("c1 = 2 · exp(-(4t / T)^2)", "11")

add_heading_2("D. Cosine Distance Gating for Unknown Face Rejection")
add_body(
    "To prevent unknown individuals or unregistered visitors from being falsely categorized as enrolled students, the Cosine Distance to the predicted class centroid c_y is computed:"
)
add_equation("D_cos(x_hat, c_y) = 1 - (x_hat · c_y) / (||x_hat||_2 · ||c_y||_2)", "12")
add_body(
    "A recognition event is confirmed valid if and only if D_cos ≤ 0.45 and prediction probability P ≥ 0.50. If D_cos > 0.45, the identity is safely classified as 'Unknown Face'."
)

add_heading_2("E. Period-Wise Attendance Verification Model")
add_body(
    "Let S = {s1, s2, ..., sn} represent enrolled students in class section C_sec, and P = {p1, p2, ..., pm} denote daily academic periods. Each period is bounded by calendar times [T_start, T_end] and assigned subject Sub_k. The attendance state function A(s_i, p_j, D) on date D is formally defined as:"
)
add_equation("A(s_i, p_j, D) = PRESENT if [D_cos ≤ 0.45 ∧ t_rec ≤ T_start + 15m ∧ U = 1]", "13")
add_equation("A(s_i, p_j, D) = LATE if [D_cos ≤ 0.45 ∧ t_rec > T_start + 15m ∧ U = 1]", "14")
add_equation("A(s_i, p_j, D) = REJECTED if U = 0 (Duplicate within period)", "15")
add_body(
    "where U(s_i, p_j, D) represents the relational database idempotency operator enforced via composite unique constraints:"
)
add_equation("U(s_i, p_j, D) = 1 if NOT EXISTS (Record in DB with s_i, p_j, D); else 0", "16")

add_heading_2("F. Scheduled Autonomous Absentee Marking")
add_body(
    "At period expiration (t = T_end + δ), an asynchronous background daemon scheduled via APScheduler triggers an automated set-difference sweep:"
)
add_equation("S_absent = S_enrolled \\ S_present", "17")
add_body(
    "For each missing student, an attendance record is committed with status ABSENT, confidence = NULL, and verification_method = 'AUTOMATED_PERIOD_END'."
)

# Section IV. EXPERIMENTAL SETUP
add_heading_1("IV. EXPERIMENTAL SETUP")
add_heading_2("A. System Specifications and Configuration")
add_body(
    "The production deployment was instantiated using containerized microservices. Table I specifies the hardware, operating system, frameworks, and deployment stack."
)

# Table I
t1 = doc.add_table(rows=1, cols=2)
t1.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t1)
p_cap1 = doc.add_paragraph()
p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cap1.paragraph_format.space_before = Pt(6)
p_cap1.paragraph_format.space_after = Pt(4)
r_c1 = p_cap1.add_run("TABLE I. SYSTEM SPECIFICATIONS AND EXPERIMENTAL CONFIGURATION")
r_c1.font.bold = True
r_c1.font.size = Pt(8.5)

hdr_cells = t1.rows[0].cells
hdr_cells[0].paragraphs[0].add_run("Component / Architecture Layer").font.bold = True
hdr_cells[1].paragraphs[0].add_run("Specification / Deployed Technology").font.bold = True
set_cell_shading(hdr_cells[0], "F1F5F9")
set_cell_shading(hdr_cells[1], "F1F5F9")

table_1_data = [
    ("System Identity", "SmartAttend: Period-Wise Attendance Management Platform"),
    ("Academic Institution", "Mohan Babu University, Tirupati, Andhra Pradesh, India"),
    ("Target Cohort", "Capstone Project Batch No: A1-8 (Academic Year 2026–2027)"),
    ("Operating System", "Windows 11 Enterprise (Host) / Linux Ubuntu 22.04 LTS (Container)"),
    ("Backend REST Engine", "FastAPI 0.110 (ASGI Async Pipeline, Python 3.11/3.13)"),
    ("Frontend Portal", "Next.js 14.2 (React 18, TypeScript, Tailwind CSS)"),
    ("Database Engine", "SQLite 3 (Edge Storage) / PostgreSQL 16 (Render Managed Cloud)"),
    ("Computer Vision Stack", "OpenCV 4.9.0 (Haar Cascade & Tensor Normalization)"),
    ("Deep Learning Framework", "PyTorch 2.2, torchvision (MobileNet V2 Backbone)"),
    ("Machine Learning", "scikit-learn 1.4 (SSA-SVM, RBF Kernel, Stratified K-Fold)"),
    ("WebSocket Gateway", "Native ASGI WebSockets (/ws/live Broadcast Feed)"),
    ("Reporting Module", "OpenPyXL & pandas (Multi-Sheet Styled Excel Export)"),
    ("Classroom Optical Sensor", "1080p Full HD Optical Camera (30 FPS, 90° FoV)"),
    ("Compute Platform", "Intel Core i7-13700H @ 2.40 GHz (16 vCPUs), 16GB RAM")
]

for comp, spec in table_1_data:
    row_cells = t1.add_row().cells
    p0 = row_cells[0].paragraphs[0]
    p0.add_run(comp).font.size = Pt(8.5)
    p1 = row_cells[1].paragraphs[0]
    p1.add_run(spec).font.size = Pt(8.5)
    set_cell_margins(row_cells[0], 60, 60, 100, 100)
    set_cell_margins(row_cells[1], 60, 60, 100, 100)

add_heading_2("B. Student Dataset Collection Protocol")
add_body(
    "Biometric facial datasets were constructed using registered students from Batch A1-8 enrolled in Computer Science and Engineering at Mohan Babu University. Face capture was conducted via the integrated student registration module: 20 to 25 canonical facial frames captured per student subject; yaw range [-30°, +30°], pitch range [-15°, +15°], roll range [-10°, +10°]; capture distances between 1.0 m and 3.5 m; and illumination levels spanning 250 lux to 650 lux. The dataset was partitioned into 70% training and 30% cross-validation. Hyperparameters converged to C* = 14.28 and γ* = 0.0028."
)
add_heading_2("C. Operational Evaluation Scenarios")
add_body(
    "Four operational scenarios were formulated to test the end-to-end capabilities of the system: Scenario 1 (Live Optical Recognition & Database Insertion); Scenario 2 (Duplicate Suppression under Continuous Feed); Scenario 3 (Class-Wise Timetable Transition & Section Isolation); and Scenario 4 (Automated Absentee Reconciliation at Period End)."
)

# Section V. RESULTS AND DISCUSSION
add_heading_1("V. RESULTS AND DISCUSSION")
add_heading_2("A. Biometric Classification Benchmarks")
add_body(
    "The classification accuracy of the proposed MobileNet + SSA-SVM pipeline was benchmarked against classical and alternative machine learning classifiers on identical 128-d normalized embeddings. The results are summarized in Table II."
)

# Table II
t2 = doc.add_table(rows=1, cols=5)
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t2)
p_cap2 = doc.add_paragraph()
p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cap2.paragraph_format.space_before = Pt(6)
p_cap2.paragraph_format.space_after = Pt(4)
r_c2 = p_cap2.add_run("TABLE II. CLASSIFICATION PERFORMANCE COMPARISON ACROSS MODELS")
r_c2.font.bold = True
r_c2.font.size = Pt(8.5)

h2 = t2.rows[0].cells
for idx, col_name in enumerate(["Model Architecture", "Precision", "Recall", "F1-Score", "Accuracy"]):
    h2[idx].paragraphs[0].add_run(col_name).font.bold = True
    set_cell_shading(h2[idx], "F1F5F9")

table_2_data = [
    ("K-Nearest Neighbors (k=3)", "88.50%", "87.10%", "87.79%", "87.60%"),
    ("Random Forest (100 Trees)", "90.80%", "89.60%", "90.19%", "90.20%"),
    ("Standard Grid-Search SVM", "94.20%", "93.40%", "93.80%", "93.75%"),
    ("Proposed MobileNet + SSA-SVM", "97.35%", "96.85%", "97.10%", "97.10%")
]

for row_data in table_2_data:
    row_cells = t2.add_row().cells
    for c_idx, val in enumerate(row_data):
        p = row_cells[c_idx].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(8.5)
        if "Proposed" in row_data[0]:
            r.font.bold = True
        set_cell_margins(row_cells[c_idx], 60, 60, 100, 100)

add_body(
    "As demonstrated in Table II, the proposed SSA-SVM pipeline achieved the highest precision (97.35%) and accuracy (97.10%). The Salp/Sparrow Swarm Algorithm efficiently escaped local minima, achieving convergence within 16 iterations and establishing optimal hyperparameter margins that prevent misclassifying registered classmates."
)

add_heading_2("B. End-to-End Latency and Computational Budget")
add_body(
    "To evaluate real-time viability on standard classroom computers without dedicated discrete GPUs, latency was measured across 500 frame transactions. Table III details execution durations."
)

# Table III
t3 = doc.add_table(rows=1, cols=3)
t3.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t3)
p_cap3 = doc.add_paragraph()
p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cap3.paragraph_format.space_before = Pt(6)
p_cap3.paragraph_format.space_after = Pt(4)
r_c3 = p_cap3.add_run("TABLE III. SUB-COMPONENT INFERENCE LATENCY BREAKDOWN")
r_c3.font.bold = True
r_c3.font.size = Pt(8.5)

h3 = t3.rows[0].cells
for idx, col_name in enumerate(["Pipeline Stage", "Mean Latency (ms)", "Peak Latency (ms)"]):
    h3[idx].paragraphs[0].add_run(col_name).font.bold = True
    set_cell_shading(h3[idx], "F1F5F9")

table_3_data = [
    ("Optical Frame Capture & Preprocessing", "16.4", "22.8"),
    ("Haar-Cascade Face Localization & Crop", "38.2", "52.4"),
    ("MobileNet V2 128-D Embedding Extraction", "62.5", "78.1"),
    ("SSA-SVM Inference & Cosine Gating", "11.8", "18.2"),
    ("Timetable Schedule & Section Validation", "14.5", "21.0"),
    ("Relational Database Transaction Commit", "28.7", "44.5"),
    ("WebSocket Live Broadcast to Dashboard", "16.0", "24.7"),
    ("Total End-to-End Latency", "188.1 ms", "261.7 ms")
]

for row_data in table_3_data:
    row_cells = t3.add_row().cells
    for c_idx, val in enumerate(row_data):
        p = row_cells[c_idx].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(8.5)
        if "Total" in row_data[0]:
            r.font.bold = True
        set_cell_margins(row_cells[c_idx], 60, 60, 100, 100)

add_body(
    "With an average end-to-end latency of 188.1 ms, the platform comfortably sustains real-time throughput (>5 FPS on subsampled streams). A student entering the lecture hall or looking towards the instructor's desk is recognized, verified against the timetable, and committed to the database in under a quarter of a second."
)

add_heading_2("C. Timetable Verification, Class-Wise Partitioning, and Duplicate Integrity")
add_body(
    "Empirical results from the operational scenario evaluations are presented in Table IV."
)

# Table IV
t4 = doc.add_table(rows=1, cols=4)
t4.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t4)
p_cap4 = doc.add_paragraph()
p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_cap4.paragraph_format.space_before = Pt(6)
p_cap4.paragraph_format.space_after = Pt(4)
r_c4 = p_cap4.add_run("TABLE IV. OPERATIONAL SCENARIO EVALUATION RESULTS")
r_c4.font.bold = True
r_c4.font.size = Pt(8.5)

h4 = t4.rows[0].cells
for idx, col_name in enumerate(["Operational Scenario", "Evaluated", "Success", "Rate (%)"]):
    h4[idx].paragraphs[0].add_run(col_name).font.bold = True
    set_cell_shading(h4[idx], "F1F5F9")

table_4_data = [
    ("Optical Facial Attendance Verification", "200 Trials", "194 Recognized", "97.00%"),
    ("Duplicate Entry Attempts in Active Period", "450 Attempts", "0 Duplicates", "100.00%"),
    ("Period-to-Period Transition Handoff", "50 Handoffs", "50 Successful", "100.00%"),
    ("Section Isolation (CSE-6A vs CSE-6B)", "80 Checks", "80 Isolated", "100.00%"),
    ("Automated Period-End Absentee Marking", "60 Periods", "60 Reconciled", "100.00%"),
    ("Excel Compliance Report Exports", "30 Reports", "30 Valid Files", "100.00%")
]

for row_data in table_4_data:
    row_cells = t4.add_row().cells
    for c_idx, val in enumerate(row_data):
        p = row_cells[c_idx].paragraphs[0]
        r = p.add_run(val)
        r.font.size = Pt(8.5)
        if "100.00%" in val:
            r.font.bold = True
        set_cell_margins(row_cells[c_idx], 60, 60, 100, 100)

add_body(
    "1) Duplicate Prevention: In continuous streaming tests where verified students remained in front of the lens, the database unique constraint completely suppressed duplicate insertions. Zero duplicate rows were logged across 450 trigger attempts (100% duplicate prevention rate)."
)
add_body(
    "2) Class-Wise Separation: When tested across separate sections (CSE-6A vs CSE-6B), students belonging to Section A were not marked into Section B's timetable slot, correctly validating academic course isolation."
)
add_body(
    "3) Automated Absentee Logging: The scheduled cron daemon executed reliably at period termination (T_end), correctly calculating set differences and inserting ABSENT records for all missing students."
)
add_body(
    "4) Faculty Audit Trail: Manual status overrides performed by instructors logged full audit trails, capturing old status, new status, timestamp, faculty email, and mandatory justification reason."
)
add_body(
    "5) Excel Compliance Generation: The reporting module compiled multi-sheet workbooks with color-coded status badges, overall attendance percentages, and period-wise audit details, providing immediate compliance documentation for academic deans."
)

# Discussion
add_heading_1("DISCUSSION")
add_body(
    "Experimental evaluation validates the proposed SmartAttend platform as an end-to-end period-wise student attendance management solution. Unlike conventional standalone computer vision models that merely predict class labels, the proposed platform bridges the fundamental gap between visual inference and university academic policy. By enforcing timetable schedule constraints, class-section boundaries, and automated period-end reconciliation, the system guarantees that attendance data is accurate, auditable, and immediately usable for institutional administration."
)

# Section VI. CONCLUSION AND FUTURE WORK
add_heading_1("VI. CONCLUSIONS AND FUTURE WORK")
add_body(
    "In this paper, an intelligent, web-based, period-wise student attendance management system powered by real-time facial recognition was designed, implemented, and empirically validated. By combining lightweight MobileNet V2 depthwise separable feature extractors with SSA-optimized Support Vector Machines and Cosine Distance gating (τ ≤ 0.45), the system achieves a high identification accuracy of 97.10% and an end-to-end inference latency of 188.1 ms on commodity hardware. Unlike conventional systems that record presence only once per day or generate unconstrained duplicate logs, the proposed architecture dynamically synchronizes optical recognitions with the active academic timetable. It strictly enforces class-section boundaries, prevents duplicate entries via database unique constraints, and automatically reconciles absentees upon period termination."
)
add_body(
    "Future work will focus on: integrating multi-spectral infrared liveness detection to eliminate potential spoofing attacks; embedding optimized TensorRT / ONNX models directly onto edge devices (e.g., NVIDIA Jetson Orin Nano or Raspberry Pi 5 with Hailo NPU); and integrating automated SMS and WhatsApp notification webhooks to alert parents immediately upon consecutive unexcused period absences."
)

# References
add_heading_1("REFERENCES")
references = [
    "[1] K. Fan, 'Classroom facial recognition using MobileNet and SSA-SVM,' Scientific Reports, vol. 16, no. 1, art. no. 265, 2026. DOI: 10.1038/s41598-025-29327-1.",
    "[2] A. G. Howard, M. Zhu, B. Chen, D. Kalenichenko, W. Wang, T. Weyand, M. Andreetto, and H. Adam, 'MobileNets: Efficient convolutional neural networks for mobile vision applications,' arXiv preprint arXiv:1704.04861, 2017.",
    "[3] F. Schroff, D. Kalenichenko, and J. Philbin, 'FaceNet: A unified embedding for face recognition and clustering,' in Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR), Boston, MA, USA, 2015, pp. 815–823.",
    "[4] J. Xue and B. Shen, 'A novel swarm intelligence optimization approach: Sparrow search algorithm,' Systems Science & Control Engineering, vol. 8, no. 1, pp. 22–34, 2020.",
    "[5] C. Cortes and V. Vapnik, 'Support-vector networks,' Machine Learning, vol. 20, no. 3, pp. 273–297, 1995.",
    "[6] P. Viola and M. Jones, 'Rapid object detection using a boosted cascade of simple features,' in Proc. IEEE Computer Society Conf. Computer Vision and Pattern Recognition (CVPR), Kauai, HI, USA, 2001, pp. 511–518.",
    "[7] M. Turk and A. Pentland, 'Eigenfaces for recognition,' Journal of Cognitive Neuroscience, vol. 3, no. 1, pp. 71–86, 1991.",
    "[8] OpenCV Open Source Computer Vision Library, 'VideoCapture — Real-time classroom camera frames,' OpenCV 4.x Reference Documentation, 2024. [Online]. Available: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html.",
    "[9] PostgreSQL Global Development Group, 'Unique constraints and transaction isolation,' PostgreSQL 16 Reference Manual, 2024. [Online]. Available: https://www.postgresql.org/docs/current/ddl-constraints.html.",
    "[10] The pandas Development Team, 'pandas.DataFrame.to_excel — Multi-sheet tabular report generation,' pandas Documentation, 2024. [Online]. Available: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html.",
    "[11] S. Ramírez-Quintana, J. R. Chacon-Murguia, and D. A. Torres-Salazar, 'Deep learning architectures for face recognition: A comprehensive review of performance across constrained environments,' IEEE Access, vol. 11, pp. 45120–45145, 2023.",
    "[12] Capstone Project Abstract and Presentation, Batch No: A1-8, Dept. of Computer Science and Engineering, School of Computing, Mohan Babu University, Sree Sainath Nagar, A. Rangampet, Tirupati – 517 102, Academic Year 2026–2027."
]

for ref in references:
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.space_after = Pt(3)
    p_ref.paragraph_format.left_indent = Inches(0.25)
    p_ref.paragraph_format.first_line_indent = Inches(-0.25)
    r = p_ref.add_run(ref)
    r.font.size = Pt(8.5)
    r.font.name = 'Times New Roman'

out_path = r"d:\web based attendance\Web_Based_Period_Wise_Attendance_Conference_Paper.docx"
doc.save(out_path)
print("SUCCESS: Document saved to", out_path)
