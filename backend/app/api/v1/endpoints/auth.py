from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.auth import LoginRequest, Token, UserResponse, UserCreate
from app.api.deps import get_current_user, get_current_active_admin

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    login_identifier = request.email.strip()
    
    # Check if login_identifier is an email
    user = db.query(User).filter(User.email.ilike(login_identifier)).first()
    
    # If not found by email, check if it matches a student registration / roll number
    matched_student = None
    if not user:
        matched_student = db.query(Student).filter(Student.reg_no.ilike(login_identifier)).first()
        if matched_student:
            user = db.query(User).filter(User.email.ilike(matched_student.email)).first()
    else:
        matched_student = db.query(Student).filter(Student.email.ilike(user.email)).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials. Please verify your email / roll number and password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive. Contact the administration.",
        )
    
    access_token = create_access_token(subject=user.email, role=user.role.value)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "full_name": user.full_name,
        "email": user.email,
        "student_id": matched_student.id if matched_student else None,
        "reg_no": matched_student.reg_no if matched_student else None,
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
