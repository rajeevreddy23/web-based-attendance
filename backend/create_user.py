"""
Interactive CLI utility to register new Admins and Professors / Faculty.
Usage:
    python create_user.py
    or
    python create_user.py --email prof.smith@college.edu --name "Dr. John Smith" --role faculty --password MySecret123 --emp-id FAC005 --dept CSE
"""

import sys
import argparse
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.faculty import Faculty


def add_user(email: str, name: str, password: str, role: str, emp_id: str = None, dept: str = "CSE", designation: str = "Assistant Professor"):
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email.strip().lower()).first()
        if existing:
            print(f"[!] Error: A user with email '{email}' already exists.")
            return False

        user_role = UserRole.ADMIN if role.strip().lower() == "admin" else UserRole.FACULTY
        user = User(
            email=email.strip().lower(),
            hashed_password=get_password_hash(password),
            full_name=name.strip(),
            role=user_role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if user_role == UserRole.FACULTY:
            # Auto-generate employee id if omitted
            if not emp_id:
                count = db.query(Faculty).count() + 1
                emp_id = f"FAC{count:03d}"

            fac = Faculty(
                user_id=user.id,
                employee_id=emp_id.strip(),
                department=dept.strip(),
                designation=designation.strip(),
            )
            db.add(fac)
            db.commit()
            print(f"[+] Faculty profile linked: Employee ID: {emp_id}, Dept: {dept}, Designation: {designation}")

        print(f"[SUCCESS] User created successfully!")
        print(f"   Name:     {user.full_name}")
        print(f"   Email:    {user.email}")
        print(f"   Role:     {user.role.value}")
        print(f"   Password: [Hidden]")
        return True
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Create a new Admin or Professor account.")
    parser.add_argument("--email", type=str, help="Institutional email address")
    parser.add_argument("--name", type=str, help="Full Name")
    parser.add_argument("--password", type=str, help="Login Password")
    parser.add_argument("--role", type=str, choices=["admin", "faculty"], default="faculty", help="Role (admin or faculty)")
    parser.add_argument("--emp-id", type=str, help="Employee ID (faculty only, e.g. FAC005)")
    parser.add_argument("--dept", type=str, default="CSE", help="Department (default: CSE)")
    parser.add_argument("--desig", type=str, default="Assistant Professor", help="Designation")

    args = parser.parse_args()

    if args.email and args.name and args.password:
        add_user(
            email=args.email,
            name=args.name,
            password=args.password,
            role=args.role,
            emp_id=args.emp_id,
            dept=args.dept,
            designation=args.desig,
        )
    else:
        print("=" * 65)
        print("  SmartAttend - User & Professor Registration Utility")
        print("=" * 65)
        role = input("Enter Role [faculty/admin] (default: faculty): ").strip().lower() or "faculty"
        name = input("Enter Full Name (e.g. Dr. Rajesh Sharma): ").strip()
        while not name:
            name = input("Name cannot be empty. Enter Full Name: ").strip()

        email = input("Enter Email (e.g. prof.name@college.edu): ").strip()
        while not email:
            email = input("Email cannot be empty. Enter Email: ").strip()

        password = input("Enter Password (e.g. Faculty@123): ").strip()
        while not password:
            password = input("Password cannot be empty. Enter Password: ").strip()

        emp_id = None
        dept = "CSE"
        desig = "Assistant Professor"

        if role == "faculty":
            dept = input("Enter Department (default: CSE): ").strip() or "CSE"
            desig = input("Enter Designation (default: Assistant Professor): ").strip() or "Assistant Professor"
            emp_id = input("Enter Employee ID (optional, press Enter to auto-generate): ").strip() or None

        add_user(
            email=email,
            name=name,
            password=password,
            role=role,
            emp_id=emp_id,
            dept=dept,
            designation=desig,
        )


if __name__ == "__main__":
    main()
