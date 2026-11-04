import os
import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np
from typing import List, Union, Optional


class MobileNetFeatureExtractor:
    """
    MobileNet Feature Extractor for Facial Embeddings.
    Extracts L2-normalized 128-dimensional deep feature representations.
    """

    def __init__(self, embedding_dim: int = 128, device: Optional[str] = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Standard MobileNetV2 backbone
        try:
            weights = models.MobileNet_V2_Weights.DEFAULT
            base_model = models.mobilenet_v2(weights=weights)
        except Exception:
            # Offline initialization without remote weight fetch
            base_model = models.mobilenet_v2(weights=None)

        # Extract features up to pooling layer (1280 dimensions)
        self.features = base_model.features
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        # Projection head to embedding_dim with L2 normalization
        self.projection = nn.Sequential(
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Linear(512, embedding_dim),
        )

        self.model = nn.Sequential(
            self.features,
            self.pool,
        )

        # Move to device and evaluation mode
        self.features.to(self.device).eval()
        self.projection.to(self.device).eval()

        # ImageNet normalization constants
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1, 3, 1, 1)

    def extract_embedding(self, face_rgb_norm: np.ndarray) -> np.ndarray:
        """
        Extracts L2-normalized 1D feature embedding from a single normalized face (160x160x3).
        """
        embeddings = self.extract_batch([face_rgb_norm])
        return embeddings[0]

    def extract_batch(self, faces_list: List[np.ndarray]) -> np.ndarray:
        """
        Extracts embeddings for a batch of normalized face arrays (H, W, 3).
        Returns shape: (N, 128), L2 normalized.
        """
        if not faces_list:
            return np.empty((0, 128), dtype=np.float32)

        # Convert to Tensor (N, C, H, W)
        tensor_batch = torch.from_numpy(np.stack(faces_list)).permute(0, 3, 1, 2).to(self.device)
        tensor_batch = (tensor_batch - self.mean) / self.std

        with torch.no_grad():
            feat = self.features(tensor_batch)
            pooled = self.pool(feat)
            flattened = torch.flatten(pooled, 1)
            projected = self.projection(flattened)
            
            # L2 Normalize
            norm = torch.norm(projected, p=2, dim=1, keepdim=True).clamp(min=1e-12)
            normalized_embeddings = (projected / norm).cpu().numpy()

        return normalized_embeddings
