# Web-Based Period-Wise Student Attendance Management Using Real-Time Facial Recognition

**Dr. K. Hari Krishna**, M.Tech, Ph.D.  
*Associate Professor, Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Sree Sainath Nagar, A. Rangampet, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: harikrishna.k@mbu.asia*  

**Sali Manaswini** (23102A040066)  
*Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: 23102a040066@mbu.asia*  

**Polisetty Sri Sambhava Krishna** (23102A040021)  
*Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: 23102a040021@mbu.asia*  

**Konka Lohith Kumar** (23102A040044)  
*Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: 23102a040044@mbu.asia*  

**Yerrapathu Gnanendra** (23102A040051)  
*Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: 23102a040051@mbu.asia*  

**Iragadindla Veerendra Sehwag** (23102A040070)  
*Department of Computer Science and Engineering, School of Computing*  
*Mohan Babu University, Tirupati – 517 102, Andhra Pradesh, India*  
*Email: 23102a040070@mbu.asia*  

*Capstone Project Batch No: A1-8 (Academic Year 2026–2027)*

---

### Abstract
Manual student attendance tracking across higher educational institutions is inherently labor-intensive, time-consuming, and highly susceptible to proxy marking and human errors. Conventional automated or biometric installations typically capture student presence only once per day at main campus access gates, completely failing to reflect physical attendance across distinct academic periods, lectures, and laboratory sessions. To resolve these challenges, this paper presents **Web-Based Period-Wise Student Attendance Management Using Real-Time Facial Recognition**, an end-to-end, full-stack, cloud-native architecture. The system integrates real-time optical video stream capture from classroom cameras with lightweight deep feature extraction using **MobileNet V2** and hyperparameter-optimized classification using **Salp/Sparrow Swarm Algorithm-tuned Support Vector Machines (SSA-SVM)**. 

Crucially, the system binds biometric facial recognitions directly with the institutional academic timetable, class sections, and period schedules. Before an attendance entry is committed, the backend verifies period boundaries, maps the recognized student identity to the enrolled subject section, applies Cosine Distance threshold gating ($\tau \le 0.45$) to reject unknown intruders, and enforces relational database unique constraints to strictly prevent duplicate entries within the same period. Students who remain unverified at period termination are automatically categorized as absent through background scheduler daemons. The implementation couples a high-performance **FastAPI** backend with a responsive **Next.js 14** web dashboard featuring real-time WebSockets and automated multi-sheet Excel reporting. Experimental evaluations under varied classroom illumination ($250\text{ lux}$ to $650\text{ lux}$), posture orientations, and multi-face density yield an identity classification accuracy of **97.10%**, an end-to-end inference latency of **188.1 ms**, and a **100% duplicate prevention rate**, eliminating manual paperwork while guaranteeing tamper-proof academic attendance records.

**Keywords**— *Period-Wise Attendance, Real-Time Facial Recognition, MobileNet V2, Swarm Intelligence, SSA-SVM, Academic Timetable Synchronization, Duplicate Prevention, Full-Stack Web Architecture, Automated Absentee Reconciliation.*

---

## I. INTRODUCTION

Accurate student attendance recording is an essential academic prerequisite across colleges and universities worldwide. Maintaining rigorous attendance logs directly influences institutional accreditation, regulatory compliance, student engagement analytics, and academic retention. Despite pervasive digital transformations across educational infrastructure, the primary method for taking attendance remains manual verbal roll calls or circulating paper sign-in sheets. These manual methods impose substantial operational bottlenecks:

1. **Instructional Time Wastage**: In standard engineering lecture halls accommodating 60 to 120 students, conducting roll calls consumes 10% to 15% of total class duration (5 to 10 minutes per period), directly reducing valuable teaching time.
2. **Vulnerability to Proxy Marking**: Paper-based attendance sheets and verbal roll calls are notoriously vulnerable to peer buddy-punching, forged signatures, and inadvertent faculty transcription oversights.
3. **One-Time Daily Record Inadequacy**: Legacy biometric access solutions—such as entrance-gate RFID card swiping or hallway fingerprint scanners—record student arrival only once per day. They fail to determine whether a student is physically present in individual class periods, elective lectures, or designated laboratory slots. Students frequently sign in at the gate but skip intermediate periods.
4. **Administrative Maintenance Burden**: Consolidating paper registers at the conclusion of each semester into university Enterprise Resource Planning (ERP) databases is labor-intensive, repetitive, and prone to data entry inconsistencies.

Biometric facial recognition provides an automated, non-intrusive, and hygienic solution to these limitations. However, deploying optical computer vision inside active academic classrooms presents several domain-specific engineering challenges: varying ambient illumination from windows and artificial lights, head pose rotations (pitch, yaw, roll), partial facial occlusions, and real-time processing constraints. Furthermore, isolated face recognition is administratively incomplete without deep integration into the academic timetable framework: attendance must be synchronized dynamically with real-time class periods, academic sections, course codes, duplicate protection barriers, and automated absent reconciliation.

To bridge this critical gap, this paper introduces an intelligent, web-based, period-wise attendance management platform. The primary contributions of this project are:
- **Lightweight Deep Feature Extraction**: Deploying **MobileNet V2** utilizing depthwise separable convolutions to produce discriminative 128-dimensional facial embeddings with minimal computational footprint.
- **Swarm-Optimized Classification**: Implementing the **Salp/Sparrow Swarm Algorithm (SSA)** to automatically optimize Support Vector Machine (SVM) hyperparameters ($C$ and $\gamma$), achieving high classification accuracy while mitigating overfitting.
- **Cosine Distance Gating**: Formulating an adaptive Cosine Distance rejection metric ($\tau \le 0.45$) to distinguish enrolled students from unauthorized or unregistered visitors.
- **Dynamic Timetable Synchronization**: An automated period-matching engine that validates class section boundaries (e.g., CSE-6A, CSE-6B) and marks students as `PRESENT` or `LATE` based on institutional grace intervals.
- **Strict Database Idempotency**: Enforcing relational composite unique constraints `(student_id, period_id, date)` to achieve a 100% duplicate prevention rate under continuous video streaming.
- **Automated Period-End Reconciliation**: Employing background cron schedulers to automatically identify unrecorded students and log them as `ABSENT` upon period conclusion.
- **Enterprise Full-Stack Web Portal**: Constructing a real-time web portal (Next.js 14, Tailwind CSS, FastAPI, PostgreSQL/SQLite, WebSockets) with interactive camera overlays, live event streams, faculty audit correction trails, and automated multi-sheet Excel export engines.

The remainder of this paper is organized as follows: Section II reviews related literature and formulates the research gap. Section III details the methodology, system architecture, and mathematical models. Section IV outlines the experimental setup. Section V presents empirical results, throughput benchmarks, and comparative discussions. Section VI concludes the paper and delineates future research directions.

---

## II. LITERATURE SURVEY & RESEARCH GAP

### A. Classical Visual Descriptors and Feature Handcrafting
Early automated attendance systems relied heavily on traditional statistical visual feature extractors. Turk and Pentland [1] pioneered facial recognition utilizing Principal Component Analysis (PCA), termed Eigenfaces, which projects pixel intensity matrices into lower-dimensional orthogonal subspaces. Belhumeur et al. extended this via Fisher’s Linear Discriminant Analysis (Fisherfaces) to maximize between-class variance while minimizing within-class variance. Ahonen et al. introduced Local Binary Patterns Histograms (LBPH), which segment facial regions into micro-texture histograms. While computationally lightweight and executable on microcontroller units, these classical approaches suffer catastrophic accuracy degradation when subjected to illumination fluctuations, partial facial occlusions, and off-axis head poses frequently encountered in live classroom environments.

### B. Deep Convolutional Neural Networks and Biometric Embeddings
The emergence of Deep Convolutional Neural Networks (CNNs) drastically elevated facial recognition benchmarks. Schroff et al. [3] introduced **FaceNet**, which employed deep inception backbones trained with triplet loss to map faces directly into a unified Euclidean space where squared Euclidean distances correspond directly to facial identity similarity. Parkhi et al. demonstrated deep representations using VGG-Face. Although deep CNNs achieve verification accuracies exceeding 99% on curated benchmarks (such as Labeled Faces in the Wild), their extreme computational complexity (over 25 million parameters and billions of FLOPs) demands high-end GPU clusters, rendering them cost-prohibitive for ubiquitous classroom deployment and real-time edge processing.

To address computational bottlenecks, Howard et al. [2] introduced **MobileNets**, which factorize standard convolutional operations into spatial depthwise convolutions followed by channel-wise $1 \times 1$ pointwise convolutions. This structural factorization slashes computational overhead by over 88% while preserving feature extraction fidelity.

### C. Swarm Intelligence and Hyperparameter-Tuned Classifiers
Support Vector Machines (SVM) formulated by Cortes and Vapnik [5] remain among the most robust classifiers for high-dimensional feature spaces. However, the generalization accuracy of SVMs equipped with Radial Basis Function (RBF) kernels is strictly governed by the regularization penalty parameter $C$ and the kernel bandwidth parameter $\gamma$. Conventional grid-search and random-search techniques are either computationally exhaustive or prone to sub-optimal local minima. Swarm intelligence algorithms—such as Particle Swarm Optimization (PSO) and the Sparrow Search Algorithm (SSA) proposed by Xue and Shen [4]—have proven superior in discovering global optima across non-linear continuous hyperparameter surfaces.

### D. Base Study and Research Gap Formulation
Recently, Fan [1] established a real-time classroom face recognition system coupling MobileNet feature extraction with SSA-SVM classification. While Fan's work validated the raw accuracy of SSA-SVM for student identification, it treated attendance purely as a computer vision classification exercise, exposing significant operational gaps:
1. **Absence of Timetable and Period Integration**: Prior implementations log recognitions as disjoint timestamped events without cross-referencing institutional period schedules, course codes, or registered class sections.
2. **Uncontrolled Duplicate Accumulation**: In continuous video streams (30 FPS), a student remaining in camera view triggers repetitive positive classifications, generating hundreds of redundant attendance rows within minutes.
3. **Absence of Autonomous Absentee Marking**: Existing frameworks identify who is in front of the lens, but fail to deduce who is missing from the scheduled roster, requiring manual post-lecture administrative data entry.
4. **Lack of Role-Based Cloud Portals and Compliance Reporting**: Educational institutions require decoupled web interfaces for department heads, faculty audit correction logs with reason tracking, and automated multi-sheet Excel reports formatted for university compliance.

The proposed system directly closes these operational gaps by encapsulating the MobileNet + SSA-SVM vision pipeline inside an intelligent academic scheduling engine.

---

## III. PROPOSED SYSTEM METHODOLOGY & ARCHITECTURE

The architectural framework of the proposed system operates through four decoupled layers, as depicted in the architectural workflow diagram (Fig. 1):
1. **Classroom Optical Sensing Tier**: Continuous video capture from standard webcams or RTSP classroom IP cameras.
2. **Computer Vision & ML Pipeline Tier**: Face detection, alignment, depthwise feature extraction, and SSA-SVM classification with Cosine Distance threshold rejection.
3. **Period-Wise Attendance Engine Tier**: Real-time timetable evaluation, section matching, grace-period thresholding, duplicate rejection, and scheduled absentee reconciliation.
4. **Cloud-Native Web Application Tier**: FastAPI REST & WebSocket server, PostgreSQL database, and Next.js responsive user interface.

```
+-----------------------------------------------------------------------------------+
|                           CLASSROOM OPTICAL SENSING                               |
|        Live HD Optical Camera Feed (30 FPS / Subsampling: N=3, FoV = 90°)         |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     DEEP COMPUTER VISION & INFERENCE PIPELINE                     |
|  1. OpenCV Haar-Cascade Face Localization: Bbox = (x, y, w, h)                   |
|  2. Canonical Alignment & Radiometric Normalization (160 x 160 x 3, [0, 1])       |
|  3. MobileNet V2 Depthwise Separable Feature Extraction: x ∈ R^128                |
|  4. Cosine Distance Gating: D_cos(x, c_k) <= 0.45                                  |
|  5. SSA-Optimized RBF SVM Classification: Predict Student ID                      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      PERIOD-WISE ATTENDANCE DECISION ENGINE                       |
|  1. Query Institutional Academic Timetable for Active Period: T ∈ [T_start, T_end]|
|  2. Verify Class Section Enrollment (e.g. CSE-6A, CSE-6B)                         |
|  3. Grace Period Check: t_rec <= T_start + Δt_grace ? "PRESENT" : "LATE"          |
|  4. Enforce Database Idempotency: Unique(student_id, date, period_id)              |
|  5. APScheduler Background Daemon: Auto-Mark "ABSENT" at Period End (T_end)       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          +--------------------+
                                          |                    |
                                          v                    v
+--------------------------------------------+  +-----------------------------------+
|       MANAGED POSTGRESQL / SQLITE DB       |  |      NEXT.JS 14 WEB DASHBOARD     |
|  - Students, Faculty, Sections & Timetable |  |  - Live Optical HUD Video Feed    |
|  - 128-D Biometric Embeddings Store        |  |  - Real-time WebSockets (wss://)  |
|  - Immutable Audit & Attendance Records    |  |  - Class-wise Filter & Excel Export|
+--------------------------------------------+  +-----------------------------------+
```
*Fig. 1. End-to-end system architecture of the period-wise attendance platform.*

### A. Face Detection and Canonical Input Preprocessing
Video frames $F_t$ captured at 30 FPS are subsampled to process every $N$-th frame ($N=3$) to prevent GPU/CPU saturation. Face regions are localized using boosted Haar Cascade classifiers:

$$\text{Bbox}_i = (x_i, y_i, w_i, h_i)$$

To prevent facial boundary clipping, a 15% bounding margin is applied:

$$x_1 = \max(0, x - 0.15w), \quad y_1 = \max(0, y - 0.15h)$$
$$x_2 = \min(W, x + 1.15w), \quad y_2 = \min(H, y + 1.15h)$$

The isolated face patch $I_{\text{crop}} = F_t[y_1:y_2, x_1:x_2]$ is radiometrically equalized via histogram equalization and resized to a canonical tensor $\hat{I} \in \mathbb{R}^{160 \times 160 \times 3}$. Pixel values are normalized into the floating-point range $[0, 1]$:

$$\hat{I}(u, v) = \frac{I_{\text{crop}}(u, v)}{255.0}$$

### B. MobileNet V2 Feature Representation
The canonical tensor $\hat{I}$ is fed into the MobileNet V2 backbone [2]. Standard convolutions simultaneously filter spatial features and combine channel features, consuming high computational complexity:

$$\mathcal{C}_{\text{standard}} = D_K \cdot D_K \cdot M \cdot N \cdot D_F \cdot D_F$$

where $D_K$ is the kernel spatial dimension, $M$ is the number of input channels, $N$ is the number of output channels, and $D_F$ is the feature map resolution. MobileNet decomposes this into:
1. **Depthwise Convolution**: Applies a single spatial filter per input channel ($D_K \times D_K \times 1$).
2. **Pointwise Convolution**: Applies a $1 \times 1$ linear combination across all channels ($1 \times 1 \times M \times N$).

The total computational expenditure of depthwise separable convolution is:

$$\mathcal{C}_{\text{separable}} = D_K \cdot D_K \cdot M \cdot D_F \cdot D_F + M \cdot N \cdot D_F \cdot D_F$$

The theoretical computational reduction ratio is expressed as:

$$\frac{\mathcal{C}_{\text{separable}}}{\mathcal{C}_{\text{standard}}} = \frac{D_K^2 \cdot M \cdot D_F^2 + M \cdot N \cdot D_F^2}{D_K^2 \cdot M \cdot N \cdot D_F^2} = \frac{1}{N} + \frac{1}{D_K^2}$$

For standard $3 \times 3$ convolutional kernels ($D_K = 3$), this achieves an approximate **88.8% reduction** in arithmetic operations. Following adaptive average pooling and dense projection, the network outputs an invariant 128-dimensional embedding vector $\mathbf{x} \in \mathbb{R}^{128}$, which is $L_2$-normalized:

$$\hat{\mathbf{x}} = \frac{\mathbf{x}}{\|\mathbf{x}\|_2 + \epsilon}, \quad \|\hat{\mathbf{x}}\|_2 = 1.0$$

### C. SSA-Optimized Multi-Class SVM Classification
To classify the high-dimensional feature vector $\hat{\mathbf{x}}$ into student identities, a multi-class Support Vector Machine with a Radial Basis Function (RBF) kernel is deployed:

$$K(\hat{\mathbf{x}}_i, \hat{\mathbf{x}}_j) = \exp\left(-\gamma \|\hat{\mathbf{x}}_i - \hat{\mathbf{x}}_j\|^2\right), \quad \gamma > 0$$

The SVM dual optimization problem solves:

$$\max_{\boldsymbol{\alpha}} \sum_{i=1}^m \alpha_i - \frac{1}{2}\sum_{i=1}^m \sum_{j=1}^m \alpha_i \alpha_j y_i y_j K(\hat{\mathbf{x}}_i, \hat{\mathbf{x}}_j)$$
$$\text{subject to } 0 \le \alpha_i \le C \quad \forall i, \quad \sum_{i=1}^m \alpha_i y_i = 0$$

The classification performance is critically governed by the penalty parameter $C$ and kernel bandwidth $\gamma$. We formulate the **Salp/Sparrow Swarm Algorithm (SSA)** to autonomously find the optimal pair $(C^*, \gamma^*)$. The search agents update positions across continuous logarithmic bounds $\log_{10}(C) \in [-1, 2]$ and $\log_{10}(\gamma) \in [-4, 0]$. The objective fitness function minimizes $K$-fold stratified cross-validation error:

$$f_{\text{fitness}}(C, \gamma) = 1 - \frac{1}{K}\sum_{k=1}^K \text{Accuracy}_k(C, \gamma)$$

The exploration decay parameter $c_1$ balances global exploration and local exploitation across $T$ maximum iterations:

$$c_1 = 2 \cdot \exp\left(-\left(\frac{4t}{T}\right)^2\right)$$

Leader agents update their position toward the best-known food source $\mathbf{x}_{\text{food}}$:

$$x_{i, j}^{t+1} = \begin{cases} x_{\text{food}, j}^t + c_1 \left((ub_j - lb_j)c_2 + lb_j\right), & c_3 \ge 0.5 \\ x_{\text{food}, j}^t - c_1 \left((ub_j - lb_j)c_2 + lb_j\right), & c_3 < 0.5 \end{cases}$$

Follower agents adjust positions based on Newtonian physical convergence:

$$x_{i, j}^{t+1} = \frac{1}{2}\left(x_{i, j}^t + x_{i-1, j}^t\right)$$

### D. Cosine Distance Gating for Unknown Face Rejection
Closed-set SVM classifiers force any input vector to be classified into one of the registered classes. In a live classroom, unregistered visitors, guest lecturers, or unrecognized faces must not be misclassified as enrolled students. To prevent false positives, we compute the class centroid $\mathbf{c}_k$ for each registered student $k$:

$$\mathbf{c}_k = \frac{1}{|E_k|}\sum_{\mathbf{e} \in E_k} \mathbf{e}$$

The Cosine Distance between query embedding $\hat{\mathbf{x}}$ and predicted centroid $\mathbf{c}_{\hat{y}}$ is evaluated:

$$D_{\cos}(\hat{\mathbf{x}}, \mathbf{c}_{\hat{y}}) = 1 - \frac{\hat{\mathbf{x}} \cdot \mathbf{c}_{\hat{y}}}{\|\hat{\mathbf{x}}\|_2 \|\mathbf{c}_{\hat{y}}\|_2}$$

The recognition is accepted if and only if:

$$D_{\cos}(\hat{\mathbf{x}}, \mathbf{c}_{\hat{y}}) \le \tau_{\text{threshold}} \quad \text{and} \quad P(\hat{y} \mid \hat{\mathbf{x}}) \ge 0.50$$

where empirical evaluations establish $\tau_{\text{threshold}} = 0.45$. If $D_{\cos} > 0.45$, the identity is safely rejected as `Unknown Face`.

### E. Mathematical Model for Period-Wise Attendance Verification
Let $S = \{s_1, s_2, \dots, s_n\}$ represent enrolled students in class section $C_{\text{sec}}$, and $P = \{p_1, p_2, \dots, p_m\}$ denote daily academic periods. Each period $p_j$ is bounded by calendar times $[T_{\text{start}}^{p_j}, T_{\text{end}}^{p_j}]$ and mapped to scheduled subject $Sub_k$.

The attendance decision state function $\mathcal{A}(s_i, p_j, D)$ for student $s_i$ on date $D$ is formally defined as:

$$\mathcal{A}(s_i, p_j, D) = \begin{cases} 
\text{PRESENT}, & \text{if } D_{\cos} \le \tau \wedge t_{\text{rec}} \in [T_{\text{start}}^{p_j}, T_{\text{start}}^{p_j} + \Delta t_{\text{grace}}] \wedge \mathcal{U}(s_i, p_j, D) = 1 \\
\text{LATE},    & \text{if } D_{\cos} \le \tau \wedge t_{\text{rec}} \in (T_{\text{start}}^{p_j} + \Delta t_{\text{grace}}, T_{\text{end}}^{p_j}] \wedge \mathcal{U}(s_i, p_j, D) = 1 \\
\text{REJECTED},& \text{if } \mathcal{U}(s_i, p_j, D) = 0 \quad (\text{Duplicate within period}) \\
\text{ABSENT},  & \text{if } t > T_{\text{end}}^{p_j} \wedge s_i \notin S_{\text{present}}^{p_j}
\end{cases}$$

where $\Delta t_{\text{grace}} = 15.0\text{ minutes}$, and $\mathcal{U}(s_i, p_j, D)$ represents the relational database idempotency operator:

$$\mathcal{U}(s_i, p_j, D) = \begin{cases}
1, & \text{if } \nexists \, \text{Record in DB with } (\text{student\_id}=s_i, \, \text{period\_id}=p_j, \, \text{date}=D) \\
0, & \text{if Record already exists in DB}
\end{cases}$$

### F. Scheduled Autonomous Absentee Marking
At the expiration of each period ($t = T_{\text{end}}^{p_j} + \delta$), an asynchronous background daemon scheduled via APScheduler triggers an automated set-difference sweep:

$$S_{\text{absent}}^{p_j} = S_{\text{enrolled}}^{C_{\text{sec}}} \setminus S_{\text{present}}^{p_j}$$

For each missing student $s_k \in S_{\text{absent}}^{p_j}$, an attendance record is committed with status `ABSENT`, `confidence = NULL`, and `verification_method = "AUTOMATED_PERIOD_END"`.

---

## IV. EXPERIMENTAL SETUP

### A. Experimental Environment & System Specifications
The production deployment and testing environment were instantiated using containerized microservices. Table I specifies the hardware, operating system, frameworks, and deployment stack.

**TABLE I. EXPERIMENTAL ENVIRONMENT & SYSTEM CONFIGURATION**
| Component | Specification / Configuration |
| :--- | :--- |
| **System Name** | SmartAttend: Web-Based Period-Wise Attendance Platform |
| **Institution** | Mohan Babu University, Tirupati, India |
| **Academic Batch** | Capstone Batch No: A1-8 (2026–2027) |
| **Operating System** | Windows 11 Enterprise (Host) / Linux Ubuntu 22.04 LTS (Docker Container) |
| **Backend Framework** | FastAPI 0.110 (ASGI Async Pipeline, Python 3.11/3.13) |
| **Frontend Framework** | Next.js 14.2 (React 18, TypeScript, Tailwind CSS) |
| **Database Engine** | SQLite 3 (Local Edge) / PostgreSQL 16 (Render Managed Cloud) |
| **Computer Vision** | OpenCV 4.9.0 (Haar Cascade & Image Processing) |
| **Deep Learning Stack**| PyTorch 2.2, torchvision (MobileNet V2 Backbone) |
| **Machine Learning** | scikit-learn 1.4 (SSA-SVM, RBF Kernel, Metrics) |
| **WebSocket Engine** | Native ASGI WebSockets (`/ws/live` Real-Time Broadcast) |
| **Reporting Engine** | OpenPyXL & pandas (Automated Multi-Sheet Excel Generation) |
| **Camera Hardware** | 1080p Full HD Optical Webcam (30 FPS, $90^\circ$ Wide Angle FoV) |
| **Compute Hardware** | Intel Core i7-13700H @ 2.40 GHz (16 vCPUs), 16 GB DDR5 RAM |

### B. Student Dataset Collection Protocol
Biometric facial datasets were constructed using registered students from Batch A1-8 enrolled in Computer Science and Engineering at Mohan Babu University. Face capture was conducted via the integrated student registration module:
- **Sample Burst**: 20 to 25 canonical facial frames captured per student subject.
- **Head Pose Variations**: Yaw range $[-30^\circ, +30^\circ]$, Pitch range $[-15^\circ, +15^\circ]$, and Roll range $[-10^\circ, +10^\circ]$.
- **Distance Range**: Captures taken between $1.0\text{ m}$ and $3.5\text{ m}$ from the optical camera.
- **Illumination Matrix**: Natural daylight ($500 - 650\text{ lux}$), standard fluorescent indoor classroom lighting ($350 - 450\text{ lux}$), and low ambient evening lighting ($250 - 300\text{ lux}$).

The dataset was partitioned into 70% for training the SSA-SVM decision boundaries and 30% for independent cross-validation. Hyperparameters converged to $C^* = 14.28$ and $\gamma^* = 0.0028$.

### C. Experimental Evaluation Scenarios
Four operational scenarios were formulated to test the end-to-end capabilities of the system:
- **Scenario 1: Live Optical Recognition & Database Insertion**: Student faces the camera. The system must detect the face, extract 128-d MobileNet vectors, identify the student, verify the class section, insert a `PRESENT` row into `attendances`, draw a green HUD box with confidence, and broadcast over WebSockets.
- **Scenario 2: Duplicate Prevention under Continuous Feed**: A student verified as `PRESENT` remains standing in front of the lens for 5 minutes (over 300 processed frames). The system must detect existing attendance and reject duplicate DB inserts.
- **Scenario 3: Class-Wise & Timetable Transition**: Testing period handoffs between Period 1 (CS601) and Period 2 (CS602) across separate sections (CSE-6A vs CSE-6B). Identical students must receive independent period logs without cross-contamination.
- **Scenario 4: Automated Absentee Reconciliation**: At period termination, the background daemon marks all students who were not optically verified as `ABSENT`.

### D. Performance Metrics
System evaluation is governed by standard quantitative metrics:
1. **Classification Accuracy**:
   $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} \times 100$$
2. **Precision & Recall**:
   $$\text{Precision} = \frac{TP}{TP + FP} \times 100, \quad \text{Recall} = \frac{TP}{TP + FN} \times 100$$
3. **F1-Score**:
   $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
4. **Average Latency**:
   $$T_{\text{avg}} = \frac{1}{M}\sum_{i=1}^M T_i \quad (\text{ms})$$
5. **Duplicate Prevention Rate**:
   $$R_{\text{dup}} = \left(1 - \frac{N_{\text{duplicate committed}}}{N_{\text{duplicate attempts}}}\right) \times 100$$
6. **Recovery / Attendance Success Rate**:
   $$R_{\text{success}} = \frac{N_{\text{verified}}}{N_{\text{total sessions}}} \times 100$$

---

## V. RESULTS AND DISCUSSION

### A. Biometric Classification Benchmarks
The classification accuracy of the proposed MobileNet + SSA-SVM pipeline was benchmarked against classical and alternative machine learning classifiers on identical 128-d normalized embeddings. The results are summarized in Table II.

**TABLE II. CLASSIFICATION PERFORMANCE COMPARISON ACROSS MODELS**
| Model Architecture | Precision (%) | Recall (%) | F1-Score (%) | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: |
| K-Nearest Neighbors ($k=3$) | 88.50 | 87.10 | 87.79 | 87.60 |
| Random Forest (100 Trees) | 90.80 | 89.60 | 90.19 | 90.20 |
| Standard Grid-Search SVM | 94.20 | 93.40 | 93.80 | 93.75 |
| **Proposed MobileNet + SSA-SVM** | **97.35** | **96.85** | **97.10** | **97.10** |

As demonstrated in Table II, the proposed SSA-SVM pipeline achieved the highest precision (97.35%) and accuracy (97.10%). The Salp/Sparrow Swarm Algorithm efficiently escaped local minima, achieving convergence within 16 iterations and establishing optimal hyperparameter margins that prevent misclassifying registered classmates.

### B. End-to-End Latency and Computational Budget
To evaluate real-time viability on standard classroom computers without dedicated discrete GPUs, latency was measured across 500 frame transactions. Table III details the execution duration for each sub-component.

**TABLE III. SUB-COMPONENT INFERENCE LATENCY BREAKDOWN**
| Sub-Component / Pipeline Stage | Mean Latency (ms) | Peak Latency (ms) |
| :--- | :---: | :---: |
| Optical Frame Capture & Preprocessing | 16.4 | 22.8 |
| Haar-Cascade Face Localization & Cropping | 38.2 | 52.4 |
| MobileNet V2 128-D Embedding Extraction | 62.5 | 78.1 |
| SSA-SVM Inference & Cosine Distance Gating | 11.8 | 18.2 |
| Timetable Schedule & Section Validation | 14.5 | 21.0 |
| Relational Database Transaction Commit | 28.7 | 44.5 |
| WebSocket Live Broadcast to Dashboard | 16.0 | 24.7 |
| **Total End-to-End Transaction Time** | **188.1 ms** | **261.7 ms** |

With an average end-to-end latency of **188.1 ms**, the platform comfortably sustains real-time throughput (>5 FPS on subsampled input streams). A student entering the lecture hall or looking towards the instructor's desk is recognized, verified against the class timetable, and committed to the database in under a quarter of a second.

### C. Timetable Verification, Class-Wise Partitioning, and Duplicate Integrity
Empirical results from the operational scenario evaluations are presented in Table IV.

**TABLE IV. OPERATIONAL SCENARIO EVALUATION RESULTS**
| Operational Metric / Scenario | Total Evaluated | Successful Outcomes | Accuracy / Success Rate |
| :--- | :---: | :---: | :---: |
| Optical Facial Attendance Verification | 200 Trials | 194 Recognized | 97.00% |
| Duplicate Entry Attempts in Active Period | 450 Attempts | 0 Duplicates Committed | **100.00%** |
| Period-to-Period Transition Handoff | 50 Handoffs | 50 Successful | **100.00%** |
| Section Isolation (CSE-6A vs CSE-6B) | 80 Cross-Checks| 80 Correctly Isolated | **100.00%** |
| Automated Period-End Absentee Marking | 60 Periods | 60 Perfect Reconciliations | **100.00%** |
| Excel Compliance Report Exports | 30 Reports | 30 Valid Workbooks | **100.00%** |

1. **Duplicate Prevention**: In continuous streaming tests where verified students remained in front of the lens, the database unique constraint `(student_id, period_id, date)` completely suppressed duplicate insertions. Zero duplicate rows were logged across 450 trigger attempts (**100% duplicate prevention rate**).
2. **Class-Wise Separation**: When tested across separate sections (CSE-6A vs CSE-6B), students belonging to Section A were not marked into Section B's timetable slot, correctly validating academic course isolation.
3. **Automated Absentee Logging**: The scheduled cron daemon executed reliably at period termination ($T_{\text{end}}$), correctly calculating set differences and inserting `ABSENT` records for all missing students.
4. **Faculty Audit Trail**: Manual status overrides performed by instructors logged full audit trails, capturing the old status, new status, timestamp, faculty email, and mandatory justification reason.
5. **Excel Compliance Generation**: The reporting module compiled multi-sheet workbooks with color-coded status badges, overall attendance percentages, and period-wise audit details, providing immediate compliance documentation for academic deans.

---

## VI. CONCLUSION AND FUTURE WORK

In this paper, an intelligent, web-based, period-wise student attendance management system powered by real-time facial recognition was designed, implemented, and empirically validated. By combining lightweight **MobileNet V2** depthwise separable feature extractors with **SSA-optimized Support Vector Machines** and Cosine Distance gating ($\tau \le 0.45$), the system achieves a high identification accuracy of **97.10%** and an end-to-end inference latency of **188.1 ms** on commodity hardware. 

Unlike conventional facial recognition systems that record presence only once per day or generate unconstrained duplicate logs, the proposed architecture dynamically synchronizes optical recognitions with the active academic timetable. It strictly enforces class-section boundaries, prevents duplicate entries via database unique constraints, and automatically reconciles absentees upon period termination. The decoupled full-stack architecture—combining a FastAPI backend with a responsive Next.js 14 dashboard—delivers real-time WebSocket monitoring, student enrollment, faculty audit controls, and automated Excel reporting.

Future work will focus on:
1. **Infrared & 3D Liveness Detection**: Integrating multi-spectral liveness detection to eliminate potential spoofing attacks from digital screens and photographic printouts.
2. **Edge Hardware Acceleration**: Embedding optimized TensorRT / ONNX models directly onto edge devices (e.g., NVIDIA Jetson Orin Nano or Raspberry Pi 5 with Hailo NPU) for local camera inference without cloud bandwidth dependencies.
3. **Automated Parent Notification Gateways**: Integrating automated SMS and WhatsApp notification webhooks to alert parents and academic mentors immediately upon consecutive unexcused period absences.

---

## REFERENCES

[1] K. Fan, "Classroom facial recognition using MobileNet and SSA-SVM," *Scientific Reports*, vol. 16, no. 1, art. no. 265, 2026. DOI: [10.1038/s41598-025-29327-1](https://doi.org/10.1038/s41598-025-29327-1).  
[2] A. G. Howard, M. Zhu, B. Chen, D. Kalenichenko, W. Wang, T. Weyand, M. Andreetto, and H. Adam, "MobileNets: Efficient convolutional neural networks for mobile vision applications," *arXiv preprint arXiv:1704.04861*, 2017. DOI: [10.48550/arXiv.1704.04861](https://arxiv.org/abs/1704.04861).  
[3] F. Schroff, D. Kalenichenko, and J. Philbin, "FaceNet: A unified embedding for face recognition and clustering," in *Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)*, Boston, MA, USA, 2015, pp. 815–823. DOI: [10.1109/CVPR.2015.7298682](https://doi.org/10.1109/CVPR.2015.7298682).  
[4] J. Xue and B. Shen, "A novel swarm intelligence optimization approach: Sparrow search algorithm," *Systems Science & Control Engineering*, vol. 8, no. 1, pp. 22–34, 2020. DOI: [10.1080/21642583.2019.1708830](https://doi.org/10.1080/21642583.2019.1708830).  
[5] C. Cortes and V. Vapnik, "Support-vector networks," *Machine Learning*, vol. 20, no. 3, pp. 273–297, 1995. DOI: [10.1007/BF00994018](https://doi.org/10.1007/BF00994018).  
[6] P. Viola and M. Jones, "Rapid object detection using a boosted cascade of simple features," in *Proc. IEEE Computer Society Conf. Computer Vision and Pattern Recognition (CVPR)*, Kauai, HI, USA, 2001, pp. 511–518. DOI: [10.1109/CVPR.2001.990517](https://doi.org/10.1109/CVPR.2001.990517).  
[7] M. Turk and A. Pentland, "Eigenfaces for recognition," *Journal of Cognitive Neuroscience*, vol. 3, no. 1, pp. 71–86, 1991. DOI: [10.1162/jocn.1991.3.1.71](https://doi.org/10.1162/jocn.1991.3.1.71).  
[8] OpenCV Open Source Computer Vision Library, "VideoCapture — Real-time classroom camera frames," *OpenCV 4.x Reference Documentation*, 2024. [Online]. Available: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html.  
[9] PostgreSQL Global Development Group, "Unique constraints and transaction isolation," *PostgreSQL 16 Reference Manual*, 2024. [Online]. Available: https://www.postgresql.org/docs/current/ddl-constraints.html.  
[10] The pandas Development Team, "pandas.DataFrame.to_excel — Multi-sheet tabular report generation," *pandas Documentation*, 2024. [Online]. Available: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html.  
[11] S. Ramírez-Quintana, J. R. Chacon-Murguia, and D. A. Torres-Salazar, "Deep learning architectures for face recognition: A comprehensive review of performance across constrained environments," *IEEE Access*, vol. 11, pp. 45120–45145, 2023. DOI: [10.1109/ACCESS.2023.3273185](https://doi.org/10.1109/ACCESS.2023.3273185).  
[12] Capstone Project Abstract and Presentation, *Batch No: A1-8*, Department of Computer Science and Engineering, School of Computing, Mohan Babu University, Sree Sainath Nagar, A. Rangampet, Tirupati – 517 102, Academic Year 2026–2027.
