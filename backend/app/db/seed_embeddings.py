"""
Seeds realistic face embeddings for registered students to enable instant
SSA-SVM model training, cross-validation, and testing without requiring manual camera capture.
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.face_embedding import FaceEmbedding
from app.ml.ssa_svm import train_ssa_svm


def seed_synthetic_student_embeddings(samples_per_student: int = 20):
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        if not students:
            print("[!] No students found. Run init_db.py first.")
            return

        print(f"[*] Generating {samples_per_student} embedding vectors each for {len(students)} students...")
        
        # Fixed seed for reproducibility
        np.random.seed(42)
        total_created = 0

        all_X = []
        all_y = []

        for st in students:
            # Check existing embeddings
            existing_count = db.query(FaceEmbedding).filter(FaceEmbedding.student_id == st.id).count()
            if existing_count >= samples_per_student:
                print(f"  [*] Student {st.reg_no} already has {existing_count} embeddings.")
                continue

            # Generate unique student face centroid in 128-d space
            base_centroid = np.random.randn(128).astype(np.float32)
            base_centroid = base_centroid / np.linalg.norm(base_centroid)

            for i in range(samples_per_student):
                # Add natural intra-class variance (lighting, facial expression, angle noise)
                noise = np.random.normal(0, 0.08, 128).astype(np.float32)
                perturbed = base_centroid + noise
                emb = perturbed / np.linalg.norm(perturbed)

                db_emb = FaceEmbedding(
                    student_id=st.id,
                    embedding_json=json.dumps(emb.tolist()),
                    model_version="mobilenet_v2_128d",
                )
                db.add(db_emb)
                all_X.append(emb)
                all_y.append(st.id)
                total_created += 1

        db.commit()
        print(f"[+] Successfully seeded {total_created} face embeddings.")

        # Train SSA-SVM with the newly generated embeddings
        print("\n[*] Running Salp Swarm Algorithm (SSA) Hyperparameter Optimization on SVM...")
        embs_all = db.query(FaceEmbedding).all()
        X = np.array([json.loads(e.embedding_json) for e in embs_all], dtype=np.float32)
        y = np.array([e.student_id for e in embs_all], dtype=np.int64)

        metrics = train_ssa_svm(X, y)
        print("\n" + "=" * 60)
        print(" SSA-SVM TRAINING RESULTS & METRICS")
        print("=" * 60)
        print(f"  Accuracy        : {metrics['accuracy'] * 100:.2f}%")
        print(f"  Precision       : {metrics['precision'] * 100:.2f}%")
        print(f"  Recall          : {metrics['recall'] * 100:.2f}%")
        print(f"  F1-Score        : {metrics['f1_score'] * 100:.2f}%")
        print(f"  CV Best Score   : {metrics['cv_score'] * 100:.2f}%")
        print(f"  Classes Trained : {len(metrics['classes'])} students")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    seed_synthetic_student_embeddings(20)
