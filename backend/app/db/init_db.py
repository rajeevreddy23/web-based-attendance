"""
Database Initializer and Seed Script.
Populates standard academic timetable (Mon-Sat), class sections, periods, subjects,
faculty, admin user, and sample students.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.class_section import ClassSection
from app.models.subject import Subject
from app.models.faculty import Faculty
from app.models.period import Period
from app.models.student import Student
from app.models.timetable import Timetable


def init_db(db: Session) -> None:
    # 1. Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

    # 2. Seed Default Admin User
    admin = db.query(User).filter(User.email == "admin@college.edu").first()
    if not admin:
        admin = User(
            email="admin@college.edu",
            hashed_password=get_password_hash("Admin@123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("[+] Admin user created: admin@college.edu / Admin@123")

    # 3. Seed Class Sections
    sections_data = [
        {"name": "CSE-6A", "department": "Computer Science & Engineering", "academic_year": "2026-2027", "semester": 6},
        {"name": "CSE-6B", "department": "Computer Science & Engineering", "academic_year": "2026-2027", "semester": 6},
    ]
    created_sections = {}
    for s_data in sections_data:
        sec = db.query(ClassSection).filter(ClassSection.name == s_data["name"]).first()
        if not sec:
            sec = ClassSection(**s_data)
            db.add(sec)
            db.commit()
            db.refresh(sec)
        created_sections[s_data["name"]] = sec
    print(f"[+] Class Sections initialized: {list(created_sections.keys())}")

    # 4. Seed Subjects
    subjects_data = [
        {"code": "CS601", "name": "Machine Learning", "department": "CSE", "credits": 4},
        {"code": "CS602", "name": "Cloud Computing", "department": "CSE", "credits": 3},
        {"code": "CS603", "name": "Computer Networks", "department": "CSE", "credits": 4},
        {"code": "CS604", "name": "Database Management Systems", "department": "CSE", "credits": 4},
        {"code": "CS605", "name": "Software Engineering", "department": "CSE", "credits": 3},
        {"code": "CS606", "name": "Web Technologies", "department": "CSE", "credits": 3},
    ]
    created_subjects = {}
    for sub in subjects_data:
        s = db.query(Subject).filter(Subject.code == sub["code"]).first()
        if not s:
            s = Subject(**sub)
            db.add(s)
            db.commit()
            db.refresh(s)
        created_subjects[sub["code"]] = s
    print(f"[+] Subjects initialized: {len(created_subjects)} subjects")

    # 5. Seed Faculty Users & Profiles
    faculty_list = [
        ("dr.sharma@college.edu", "Dr. Rajesh Sharma", "FAC001", "CSE", "Professor"),
        ("prof.anita@college.edu", "Prof. Anita Desai", "FAC002", "CSE", "Associate Professor"),
        ("dr.vikram@college.edu", "Dr. Vikram Seth", "FAC003", "CSE", "Assistant Professor"),
        ("prof.priya@college.edu", "Prof. Priya Nair", "FAC004", "CSE", "Assistant Professor"),
    ]
    created_faculty = []
    for email, name, emp_id, dept, desig in faculty_list:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash("Faculty@123"),
                full_name=name,
                role=UserRole.FACULTY,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        fac = db.query(Faculty).filter(Faculty.employee_id == emp_id).first()
        if not fac:
            fac = Faculty(
                user_id=user.id,
                employee_id=emp_id,
                department=dept,
                designation=desig,
            )
            db.add(fac)
            db.commit()
            db.refresh(fac)
        created_faculty.append(fac)
    print(f"[+] Faculty initialized: {len(created_faculty)} members")

    # 6. Seed Periods (Standard College Schedule)
    periods_data = [
        {"period_number": 1, "name": "Period 1", "start_time": time(9, 0), "end_time": time(9, 50), "is_break": False},
        {"period_number": 2, "name": "Period 2", "start_time": time(9, 50), "end_time": time(10, 40), "is_break": False},
        {"period_number": 3, "name": "Period 3", "start_time": time(10, 55), "end_time": time(11, 45), "is_break": False},
        {"period_number": 4, "name": "Period 4", "start_time": time(11, 45), "end_time": time(12, 35), "is_break": False},
        {"period_number": 5, "name": "Lunch Break", "start_time": time(12, 35), "end_time": time(13, 25), "is_break": True},
        {"period_number": 6, "name": "Period 5", "start_time": time(13, 25), "end_time": time(14, 15), "is_break": False},
        {"period_number": 7, "name": "Period 6", "start_time": time(14, 15), "end_time": time(15, 5), "is_break": False},
    ]
    created_periods = {}
    for p in periods_data:
        period = db.query(Period).filter(Period.period_number == p["period_number"]).first()
        if not period:
            period = Period(**p)
            db.add(period)
            db.commit()
            db.refresh(period)
        created_periods[p["period_number"]] = period
    print(f"[+] Periods initialized: {len(created_periods)} slots (including Lunch Break)")

    # 7. Seed Full-Week Timetable for CSE-6A (Monday=0 to Saturday=5)
    # Timetable pattern:
    # Day 0 (Mon): P1: CS601 (Sharma), P2: CS602 (Anita), P3: CS603 (Vikram), P4: CS604 (Priya), P6: CS605 (Sharma), P7: CS606 (Anita)
    # Day 1 (Tue): P1: CS602, P2: CS603, P3: CS604, P4: CS601, P6: CS606, P7: CS605
    # Day 2 (Wed): P1: CS603, P2: CS601, P3: CS602, P4: CS605, P6: CS604, P7: CS606
    # Day 3 (Thu): P1: CS604, P2: CS605, P3: CS601, P4: CS603, P6: CS602, P7: CS601
    # Day 4 (Fri): P1: CS605, P2: CS606, P3: CS603, P4: CS602, P6: CS601, P7: CS604
    # Day 5 (Sat): P1: CS606, P2: CS604, P3: CS605, P4: CS601, P6: CS603, P7: CS602

    weekly_matrix = {
        0: [("CS601", 1, 0), ("CS602", 2, 1), ("CS603", 3, 2), ("CS604", 4, 3), ("CS605", 6, 0), ("CS606", 7, 1)],
        1: [("CS602", 1, 1), ("CS603", 2, 2), ("CS604", 3, 3), ("CS601", 4, 0), ("CS606", 6, 1), ("CS605", 7, 0)],
        2: [("CS603", 1, 2), ("CS601", 2, 0), ("CS602", 3, 1), ("CS605", 4, 0), ("CS604", 6, 3), ("CS606", 7, 1)],
        3: [("CS604", 1, 3), ("CS605", 2, 0), ("CS601", 3, 0), ("CS603", 4, 2), ("CS602", 6, 1), ("CS601", 7, 0)],
        4: [("CS605", 1, 0), ("CS606", 2, 1), ("CS603", 3, 2), ("CS602", 4, 1), ("CS601", 6, 0), ("CS604", 7, 3)],
        5: [("CS606", 1, 1), ("CS604", 2, 3), ("CS605", 3, 0), ("CS601", 4, 0), ("CS603", 6, 2), ("CS602", 7, 1)],
    }

    sec_a = created_sections["CSE-6A"]
    tt_count = 0
    for day, slots in weekly_matrix.items():
        for sub_code, p_num, fac_idx in slots:
            period_obj = created_periods[p_num]
            sub_obj = created_subjects[sub_code]
            fac_obj = created_faculty[fac_idx]

            existing = db.query(Timetable).filter(
                Timetable.day_of_week == day,
                Timetable.period_id == period_obj.id,
                Timetable.class_section_id == sec_a.id,
            ).first()

            if not existing:
                tt_entry = Timetable(
                    day_of_week=day,
                    period_id=period_obj.id,
                    class_section_id=sec_a.id,
                    subject_id=sub_obj.id,
                    faculty_id=fac_obj.id,
                )
                db.add(tt_entry)
                tt_count += 1
    db.commit()
    print(f"[+] Timetable generated: {tt_count} weekly period slots for CSE-6A")

    # 8. Seed Sample Students for CSE-6A
    students_data = [
        ("21CS001", "Aarav", "Patel", "aarav.p@college.edu"),
        ("21CS002", "Bhavya", "Reddy", "bhavya.r@college.edu"),
        ("21CS003", "Chirag", "Sharma", "chirag.s@college.edu"),
        ("21CS004", "Divya", "Iyer", "divya.i@college.edu"),
        ("21CS005", "Eshaan", "Verma", "eshaan.v@college.edu"),
        ("21CS006", "Fatima", "Khan", "fatima.k@college.edu"),
        ("21CS007", "Gautam", "Menon", "gautam.m@college.edu"),
        ("21CS008", "Harshita", "Gupta", "harshita.g@college.edu"),
        ("21CS009", "Ishaan", "Joshi", "ishaan.j@college.edu"),
        ("21CS010", "Janhavi", "Deshmukh", "janhavi.d@college.edu"),
    ]
    student_count = 0
    for reg, fn, ln, email in students_data:
        st = db.query(Student).filter(Student.reg_no == reg).first()
        if not st:
            st = Student(
                reg_no=reg,
                first_name=fn,
                last_name=ln,
                email=email,
                class_section_id=sec_a.id,
                consent_given=True,
                is_active=True,
            )
            db.add(st)
            student_count += 1
    db.commit()
    print(f"[+] Sample students registered: {student_count} students in CSE-6A")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("[*] Initializing database and loading seed data...")
        init_db(db)
        print("[*] Database successfully seeded.")
    finally:
        db.close()
