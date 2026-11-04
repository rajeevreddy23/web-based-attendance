import os
import math
import pickle
import logging
import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from app.core.config import settings

logger = logging.getLogger(__name__)


class SalpSwarmOptimizer:
    """
    Salp Swarm Algorithm (SSA) for optimizing SVM hyperparameters (C and gamma).
    Mirjalili et al. (2017) formulation with exploration decay c1 = 2 * exp(-(4t/T)^2).
    """

    def __init__(
        self,
        n_salps: int = 15,
        max_iter: int = 20,
        lb: np.ndarray = np.array([-1.0, -4.0]),  # log10(C) in [-1, 2], log10(gamma) in [-4, 0]
        ub: np.ndarray = np.array([2.0, 0.0]),
        n_splits: int = 3,
        random_state: int = 42,
    ):
        self.n_salps = n_salps
        self.max_iter = max_iter
        self.lb = lb
        self.ub = ub
        self.dim = len(lb)
        self.n_splits = n_splits
        self.random_state = random_state
        np.random.seed(random_state)

    def _fitness(self, position: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
        C = 10.0 ** position[0]
        gamma = 10.0 ** position[1]

        clf = SVC(C=C, gamma=gamma, kernel="rbf", probability=True)
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        try:
            scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
            return float(np.mean(scores))
        except Exception:
            return 0.0

    def optimize(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
        """
        Runs SSA optimization.
        Returns: (best_C, best_gamma, best_fitness)
        """
        # Initialize salp positions uniformly between [lb, ub]
        positions = np.zeros((self.n_salps, self.dim))
        for i in range(self.dim):
            positions[:, i] = np.random.uniform(self.lb[i], self.ub[i], self.n_salps)

        # Initialize food source (global best)
        food_pos = np.copy(positions[0])
        food_fitness = -1.0

        for i in range(self.n_salps):
            fit = self._fitness(positions[i], X, y)
            if fit > food_fitness:
                food_fitness = fit
                food_pos = np.copy(positions[i])

        # Main SSA loop
        for t in range(self.max_iter):
            # Exploration/exploitation decay parameter
            c1 = 2.0 * math.exp(-((4.0 * t / self.max_iter) ** 2))

            for i in range(self.n_salps):
                if i < self.n_salps // 2:
                    # Leader salps
                    for j in range(self.dim):
                        c2 = np.random.rand()
                        c3 = np.random.rand()
                        if c3 >= 0.5:
                            positions[i, j] = food_pos[j] + c1 * ((self.ub[j] - self.lb[j]) * c2 + self.lb[j])
                        else:
                            positions[i, j] = food_pos[j] - c1 * ((self.ub[j] - self.lb[j]) * c2 + self.lb[j])
                else:
                    # Follower salps
                    positions[i] = 0.5 * (positions[i] + positions[i - 1])

                # Boundary clamping
                positions[i] = np.clip(positions[i], self.lb, self.ub)

                # Fitness evaluation
                fit = self._fitness(positions[i], X, y)
                if fit > food_fitness:
                    food_fitness = fit
                    food_pos = np.copy(positions[i])

        best_C = float(10.0 ** food_pos[0])
        best_gamma = float(10.0 ** food_pos[1])
        logger.info(f"SSA Tuning Complete -> Best C: {best_C:.4f}, Best gamma: {best_gamma:.6f}, CV Accuracy: {food_fitness:.4f}")
        return best_C, best_gamma, food_fitness


def train_ssa_svm(
    embeddings: np.ndarray,
    labels: np.ndarray,
    save_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full training pipeline:
    1. Label encodes student IDs
    2. Runs SSA to find optimal C and gamma
    3. Trains SVM with optimal hyperparameters
    4. Evaluates precision, recall, f1, and confusion matrix
    5. Computes class centroids for cosine-distance rejection gating
    6. Saves model bundle to disk
    """
    if save_path is None:
        save_path = os.path.join(settings.MODELS_DIR, "ssa_svm_model.pkl")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    le = LabelEncoder()
    y_encoded = le.fit_transform(labels)
    n_classes = len(le.classes_)

    if n_classes < 2:
        raise ValueError("At least 2 distinct students are required to train the classifier.")

    # Determine CV splits based on minimum class count
    unique, counts = np.unique(y_encoded, return_counts=True)
    min_count = min(counts)
    n_splits = max(2, min(min_count, 3))

    # SSA Optimization
    ssa = SalpSwarmOptimizer(n_salps=12, max_iter=15, n_splits=n_splits)
    best_C, best_gamma, cv_score = ssa.optimize(embeddings, y_encoded)

    # Train-test split for final metric reporting
    if min_count >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings, y_encoded, test_size=0.25, stratify=y_encoded, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test = embeddings, embeddings, y_encoded, y_encoded

    clf = SVC(C=best_C, gamma=best_gamma, kernel="rbf", probability=True)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Compute class prototypes (centroids) for cosine distance gating
    centroids = {}
    for class_idx, class_name in enumerate(le.classes_):
        class_embs = embeddings[y_encoded == class_idx]
        mean_vector = np.mean(class_embs, axis=0)
        norm_mean = mean_vector / (np.linalg.norm(mean_vector) + 1e-12)
        centroids[int(class_idx)] = norm_mean

    # Fit final classifier on 100% of available data
    final_clf = SVC(C=best_C, gamma=best_gamma, kernel="rbf", probability=True)
    final_clf.fit(embeddings, y_encoded)

    model_bundle = {
        "classifier": final_clf,
        "label_encoder": le,
        "centroids": centroids,
        "best_C": best_C,
        "best_gamma": best_gamma,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "cv_score": round(float(cv_score), 4),
            "confusion_matrix": cm,
            "classes": [str(c) for c in le.classes_],
        },
    }

    with open(save_path, "wb") as f:
        pickle.dump(model_bundle, f)

    logger.info(f"Model saved to {save_path} with Test Accuracy={acc:.4f}, F1={f1:.4f}")
    return model_bundle["metrics"]
