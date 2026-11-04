from app.schemas.auth import (
    LoginRequest,
    Token,
    TokenPayload,
    UserCreate,
    UserResponse,
)
from app.schemas.class_section import (
    ClassSectionCreate,
    ClassSectionResponse,
)
from app.schemas.subject import (
    SubjectCreate,
    SubjectResponse,
)
from app.schemas.period import (
    PeriodCreate,
    PeriodResponse,
)
from app.schemas.timetable import (
    TimetableCreate,
    TimetableResponse,
    ActivePeriodResponse,
)
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    FaceRegistrationRequest,
)
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    ManualCorrectionRequest,
    LiveRecognitionEvent,
)
from app.schemas.report import (
    ReportFilterRequest,
    ReportDownloadResponse,
)
