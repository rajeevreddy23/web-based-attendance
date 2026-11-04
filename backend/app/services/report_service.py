import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date as dt_date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.subject import Subject
from app.models.period import Period
from app.models.class_section import ClassSection
from app.core.config import settings


def generate_attendance_excel(
    db: Session,
    start_date: dt_date,
    end_date: dt_date,
    class_section_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    period_id: Optional[int] = None,
    student_id: Optional[int] = None,
) -> str:
    """
    Generates a professional multi-sheet Excel (.xlsx) attendance report.
    - Sheet 1: Attendance Summary & Metrics
    - Sheet 2: Detailed Period-Wise Records
    """
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_report_{start_date}_to_{end_date}_{timestamp_str}.xlsx"
    filepath = os.path.join(settings.REPORTS_DIR, filename)

    query = db.query(Attendance).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date,
    )
    if class_section_id:
        query = query.filter(Attendance.class_section_id == class_section_id)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    if period_id:
        query = query.filter(Attendance.period_id == period_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    records = query.order_by(Attendance.date.desc(), Attendance.period_id.asc()).all()

    wb = openpyxl.Workbook()
    # Sheet 1: Summary
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True

    # Sheet 2: Details
    ws_detail = wb.create_sheet(title="Period-Wise Details")
    ws_detail.views.sheetView[0].showGridLines = True

    # Styling Palette
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid") # Navy
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="1F497D")
    subtitle_font = Font(name="Calibri", size=11, italic=True, color="595959")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    present_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") # Light Green
    absent_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")  # Light Red
    late_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")    # Light Yellow

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # ==========================
    # POPULATE SUMMARY SHEET
    # ==========================
    ws_summary["A1"] = "Period-Wise Student Attendance Report"
    ws_summary["A1"].font = title_font
    ws_summary["A2"] = f"Report Date Range: {start_date} to {end_date} | Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws_summary["A2"].font = subtitle_font

    total_count = len(records)
    present_count = sum(1 for r in records if r.status in ["PRESENT", "LATE"])
    absent_count = sum(1 for r in records if r.status == "ABSENT")
    late_count = sum(1 for r in records if r.status == "LATE")
    pct = round((present_count / total_count * 100), 2) if total_count > 0 else 0.0

    summary_rows = [
        ("Metric", "Value"),
        ("Total Recorded Sessions", total_count),
        ("Total Present", present_count),
        ("Total Late", late_count),
        ("Total Absent", absent_count),
        ("Overall Attendance Percentage", f"{pct}%"),
    ]

    for row_idx, (k, v) in enumerate(summary_rows, start=4):
        ws_summary.cell(row=row_idx, column=1, value=k)
        ws_summary.cell(row=row_idx, column=2, value=v)
        if row_idx == 4:
            ws_summary.cell(row=row_idx, column=1).fill = header_fill
            ws_summary.cell(row=row_idx, column=1).font = header_font
            ws_summary.cell(row=row_idx, column=2).fill = header_fill
            ws_summary.cell(row=row_idx, column=2).font = header_font
        else:
            ws_summary.cell(row=row_idx, column=1).font = bold_font
            ws_summary.cell(row=row_idx, column=2).font = regular_font
            ws_summary.cell(row=row_idx, column=1).border = thin_border
            ws_summary.cell(row=row_idx, column=2).border = thin_border

    # ==========================
    # POPULATE DETAIL SHEET
    # ==========================
    detail_headers = [
        "Record ID", "Date", "Period Number", "Period Name", "Subject Code",
        "Subject Name", "Registration No", "Student Name", "Class Section",
        "Status", "Time", "Confidence", "Method", "Marked By"
    ]

    for col_idx, h in enumerate(detail_headers, start=1):
        cell = ws_detail.cell(row=1, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_idx, r in enumerate(records, start=2):
        row_data = [
            r.id,
            str(r.date),
            r.period.period_number if r.period else "N/A",
            r.period.name if r.period else "N/A",
            r.subject.code if r.subject else "N/A",
            r.subject.name if r.subject else "N/A",
            r.student.reg_no if r.student else "N/A",
            r.student.full_name if r.student else "N/A",
            r.class_section.name if r.class_section else "N/A",
            r.status,
            r.timestamp.strftime("%H:%M:%S") if r.timestamp else "N/A",
            f"{r.confidence:.2f}" if r.confidence is not None else "N/A",
            r.verification_method,
            r.marked_by,
        ]

        for col_idx, val in enumerate(row_data, start=1):
            cell = ws_detail.cell(row=row_idx, column=col_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            
            # Color status
            if col_idx == 10:  # Status column
                cell.alignment = Alignment(horizontal="center")
                if val == "PRESENT":
                    cell.fill = present_fill
                elif val == "ABSENT":
                    cell.fill = absent_fill
                elif val == "LATE":
                    cell.fill = late_fill

    # Auto-adjust column widths
    for ws in [ws_summary, ws_detail]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(filepath)
    return filepath
