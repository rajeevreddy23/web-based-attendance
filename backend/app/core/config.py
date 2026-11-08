from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "attendance.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Web-Based Period-Wise Student Attendance Management"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "capstone-super-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # Camera & ML Recognition
    CAMERA_INDEX: int = 0
    PROCESS_EVERY_N_FRAMES: int = 3
    CONSECUTIVE_FRAMES_REQUIRED: int = 3
    COSINE_DISTANCE_THRESHOLD: float = 0.45
    FACE_DETECTION_CONFIDENCE: float = 0.80

    # Paths
    BASE_DIR: str = BASE_DIR
    MODELS_DIR: str = os.path.join(BASE_DIR, "data", "models")
    EMBEDDINGS_DIR: str = os.path.join(BASE_DIR, "data", "embeddings")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "data", "reports")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
