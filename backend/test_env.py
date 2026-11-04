"""
Environment & Hardware Diagnostic Script for Web-Based Period-Wise Student Attendance Management
Run: python test_env.py
"""

import sys
import os

def check_python():
    print(f"[+] Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("  [!] WARNING: Recommended Python version is 3.10 or 3.11.")
    else:
        print("  [*] Python version meets requirements.")

def check_modules():
    print("\n[+] Checking Critical Dependencies:")
    modules = [
        ("FastAPI", "fastapi"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic"),
        ("OpenCV", "cv2"),
        ("PyTorch", "torch"),
        ("Torchvision", "torchvision"),
        ("Scikit-Learn", "sklearn"),
        ("Pandas", "pandas"),
        ("OpenPyXL", "openpyxl"),
        ("APScheduler", "apscheduler"),
    ]
    
    missing = []
    for label, mod_name in modules:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "Installed")
            print(f"  [*] {label:<16}: OK (v{ver})")
        except ImportError:
            print(f"  [X] {label:<16}: MISSING")
            missing.append(label)
    
    if missing:
        print(f"\n[!] Missing modules: {', '.join(missing)}")
        print("    Install them using: pip install -r requirements.txt")
    else:
        print("\n[*] All critical dependencies are installed.")

def check_camera():
    print("\n[+] Testing Classroom Camera / Webcam Access:")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("  [!] Camera index 0 could not be opened.")
            print("      If using an external USB camera, check index 1 or 2 in .env (CAMERA_INDEX).")
        else:
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w, c = frame.shape
                print(f"  [*] Camera index 0 OK! Captured test frame resolution: {w}x{h} ({c} channels)")
            else:
                print("  [!] Camera opened but failed to capture frame.")
            cap.release()
    except Exception as e:
        print(f"  [!] Camera test error: {e}")

def check_pytorch_and_device():
    print("\n[+] Checking PyTorch & Accelerator Device:")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"  [*] CUDA (GPU) Available: {cuda_available}")
        if cuda_available:
            print(f"  [*] GPU Device: {torch.cuda.get_device_name(0)}")
        else:
            print("  [*] Running on CPU (MobileNet is lightweight and optimized for CPU real-time inference).")
    except Exception as e:
        print(f"  [!] PyTorch check error: {e}")

def check_data_directories():
    print("\n[+] Checking Storage Directories:")
    dirs = ["./data/models", "./data/embeddings", "./data/reports"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  [*] Directory ready: {os.path.abspath(d)}")

if __name__ == "__main__":
    print("=" * 70)
    print(" capstone: Face Attendance System - Diagnostic Check")
    print("=" * 70)
    check_python()
    check_modules()
    check_pytorch_and_device()
    check_camera()
    check_data_directories()
    print("=" * 70)
