"""
CampusSync ERP - Faculty Internal Marks Export Service
======================================================
File: services/export_marks_service.py

Provides Excel (.xlsx) and PDF (.pdf) export generation for HNGU Internal Assessment Marks.
"""

import io
import re
import os
from datetime import datetime
from flask import current_app

# OpenPyXL Imports
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ReportLab Imports
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


def sanitize_filename_component(text):
    """Sanitizes text for safe inclusion in filenames."""
    if not text:
        return ""
    return re.sub(r'[^A-Za-z0-9_\-]', '_', str(text)).strip('_')


def _calc_best_tests(bd):
    """Calculates Best 2 out of 3 Class Tests (/15)."""
    if not bd:
        return None
    tests = [bd.get('test1'), bd.get('test2'), bd.get('test3')]
    valid = [float(v) for v in tests if v is not None]
    if not valid:
        return None
    valid.sort(reverse=True)
    best2 = valid[:2]
    return round(sum(best2) / len(best2), 2)



def _parse_roll_num(val):
    if val is None:
        return 999999
    digits = "".join(c for c in str(val).strip() if c.isdigit())
    return int(digits) if digits else 999999


def generate_internal_marks_excel(data_dict, faculty_name="Faculty"):
    """
    Generates a professionally formatted Excel (.xlsx) workbook for Internal Marks.
    Excludes the internal 'Status' column from the export sheet.
    
    Args:
        data_dict (dict): Dictionary returned by get_faculty_marks_students
        faculty_name (str): Logged-in faculty member's full name
        
    Returns:
        io.BytesIO: Buffer containing generated Excel file
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Internal Marks"
    ws.views.sheetView[0].showGridLines = True

    subject = data_dict.get("subject", {})
    subject_code = subject.get("subject_code", "")
    subject_name = subject.get("subject_name", "")
    subject_type = subject.get("subject_type", "Theory")
    max_internal = subject.get("internal_marks", 50 if subject_type == 'Theory' else 25)
    
    academic_year = data_dict.get("academic_year", "")
    semester = data_dict.get("semester", "")
    division = data_dict.get("division", "")
    students = list(data_dict.get("students", []))
    students.sort(key=lambda s: (_parse_roll_num(s.get("roll_number")), s.get("full_name", "").lower()))

    is_theory = (subject_type == 'Theory')
    from services.subject_service import get_subject_component_config
    comp_cfg = get_subject_component_config(subject)
    maxes = comp_cfg["maxes"] if comp_cfg else {}

    # Color Palette & Styles
    font_title = Font(name="Arial", size=14, bold=True, color="1E3A8A")
    font_subtitle = Font(name="Arial", size=11, bold=True, color="334155")
    font_meta_lbl = Font(name="Arial", size=9, bold=True, color="475569")
    font_meta_val = Font(name="Arial", size=9, bold=False, color="0F172A")
    font_th = Font(name="Arial", size=9, bold=True, color="FFFFFF")
    font_th_calc = Font(name="Arial", size=9, bold=True, color="1E3A8A")
    font_data = Font(name="Arial", size=9, color="0F172A")
    font_total = Font(name="Arial", size=9, bold=True, color="1E40AF")

    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_calc_header = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    fill_total_header = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_total_cell = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    border_all = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")

    num_cols = 14 if is_theory else 8

    college_name = (data_dict.get("college", {}).get("college_name") or "CAMPUSSYNC BCA COLLEGE").upper()
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
    cell_t1 = ws.cell(row=1, column=1, value=college_name)
    cell_t1.font = font_title
    cell_t1.alignment = align_center

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_cols)
    cell_t2 = ws.cell(row=2, column=1, value="INTERNAL ASSESSMENT MARKS REPORT")
    cell_t2.font = font_subtitle
    cell_t2.alignment = align_center

    # Metadata Section (Rows 4-5)
    meta_pairs_r4 = [
        ("Academic Year:", academic_year),
        ("Semester:", f"Semester {semester}"),
        ("Division:", division)
    ]
    meta_pairs_r5 = [
        ("Subject Code:", subject_code),
        ("Subject Name:", f"{subject_name} ({subject_type})"),
        ("Faculty:", faculty_name)
    ]

    col_idx = 1
    for label, val in meta_pairs_r4:
        c_lbl = ws.cell(row=4, column=col_idx, value=label)
        c_lbl.font = font_meta_lbl
        c_lbl.alignment = align_left
        col_idx += 1
        c_val = ws.cell(row=4, column=col_idx, value=val)
        c_val.font = font_meta_val
        c_val.alignment = align_left
        col_idx += 3 if is_theory else 1

    col_idx = 1
    for label, val in meta_pairs_r5:
        c_lbl = ws.cell(row=5, column=col_idx, value=label)
        c_lbl.font = font_meta_lbl
        c_lbl.alignment = align_left
        col_idx += 1
        c_val = ws.cell(row=5, column=col_idx, value=val)
        c_val.font = font_meta_val
        c_val.alignment = align_left
        col_idx += 3 if is_theory else 1

    # Table Header Row (Row 7)
    header_row = 7
    if is_theory:
        t1_m = maxes.get("test1", 20)
        t2_m = maxes.get("test2", 20)
        t3_m = maxes.get("test3", 20)
        b2_m = maxes.get("best2", 20)
        ie_m = maxes.get("internal_exam", 50)
        al_m = maxes.get("active_learning", 5)
        ca_m = maxes.get("class_assignment", 5)
        ha_m = maxes.get("home_assignment", 5)
        att_m = maxes.get("attendance", 5)
        headers = [
            "Roll No", "Enrollment No", "Student Name",
            f"Test 1\n(/{t1_m:g})", f"Test 2\n(/{t2_m:g})", f"Test 3\n(/{t3_m:g})", f"Best 2\n(/{b2_m:g})",
            f"Internal Exam\n(/{ie_m:g})",
            f"Active Lrn\n(/{al_m:g})", f"Class Assign\n(/{ca_m:g})", f"Home Assign\n(/{ha_m:g})",
            "Attendance\n(%)", f"Attend.\n(/{att_m:g})",
            f"Internal Total\n(/{max_internal})"
        ]
    else:
        ie_m = maxes.get("internal_exam", 10)
        pe_m = maxes.get("practical_eval", 10)
        vi_m = maxes.get("viva", 0)
        jo_m = maxes.get("journal", 5)
        headers = [
            "Roll No", "Enrollment No", "Student Name",
            f"Viva / Interview\n(/{ie_m:g})", f"Coding / Practical\n(/{pe_m:g})", f"Journal\n(/{jo_m:g})",
            f"Internal Total\n(/{max_internal})"
        ]

    for c_i, h_text in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=c_i, value=h_text)
        cell.font = font_th
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_all
        
        # Highlighting calculated columns
        if is_theory and c_i in [7, 13]:
            cell.fill = fill_calc_header
            cell.font = font_th_calc
        elif (is_theory and c_i == 14) or (not is_theory and c_i == 7):
            cell.fill = fill_total_header
            cell.font = font_th_calc

    ws.row_dimensions[header_row].height = 28

    # Populate Data Rows
    current_row = header_row + 1
    for st_idx, st in enumerate(students):
        bd = st.get("breakdown") or {}

        if is_theory:
            best_2 = _calc_best_tests(bd)
            
            att_val = bd.get("attendance")
            if att_val is not None:
                att_pct_str = f"{round((float(att_val) / maxes.get('attendance', 5.0)) * 100, 1)}%"
                att_num = float(att_val)
            else:
                att_pct_str = "N/A"
                att_num = "N/A"

            total_obtained = st.get("marks_obtained")

            row_data = [
                st.get("roll_number", ""),
                st.get("enrollment_no", ""),
                st.get("full_name", ""),
                bd.get("test1") if bd.get("test1") is not None else "",
                bd.get("test2") if bd.get("test2") is not None else "",
                bd.get("test3") if bd.get("test3") is not None else "",
                best_2 if best_2 is not None else "",
                bd.get("internal_exam") if bd.get("internal_exam") is not None else "",
                bd.get("active_learning") if bd.get("active_learning") is not None else "",
                bd.get("class_assignment") if bd.get("class_assignment") is not None else "",
                bd.get("home_assignment") if bd.get("home_assignment") is not None else "",
                att_pct_str,
                att_num,
                total_obtained if total_obtained is not None else ""
            ]
        else:
            total_obtained = st.get("marks_obtained")
            row_data = [
                st.get("roll_number", ""),
                st.get("enrollment_no", ""),
                st.get("full_name", ""),
                bd.get("internal_exam") if bd.get("internal_exam") is not None else "",
                bd.get("practical_eval") if bd.get("practical_eval") is not None else "",
                bd.get("journal") if bd.get("journal") is not None else "",
                total_obtained if total_obtained is not None else ""
            ]

        is_even = (st_idx % 2 == 1)
        row_fill = fill_zebra if is_even else None

        for c_i, val in enumerate(row_data, start=1):
            cell = ws.cell(row=current_row, column=c_i, value=val)
            cell.font = font_data
            cell.border = border_all
            if row_fill:
                cell.fill = row_fill

            # Alignment & Cell Specific Styling
            if c_i == 1:
                cell.alignment = align_center
            elif c_i == 2:
                cell.alignment = align_center
            elif c_i == 3:
                cell.alignment = align_left
            else:
                cell.alignment = align_center

            # Total column styling
            if (is_theory and c_i == 14) or (not is_theory and c_i == 7):
                cell.font = font_total
                cell.fill = fill_total_cell

        ws.row_dimensions[current_row].height = 20
        current_row += 1

    # Freezepanes
    ws.freeze_panes = "D8"

    # Column Auto-Widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            lines = val_str.split('\n')
            for l in lines:
                if len(l) > max_len:
                    max_len = len(l)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

    # Specific Width Overrides
    ws.column_dimensions['A'].width = 10  # Roll No
    ws.column_dimensions['B'].width = 16  # Enrollment
    ws.column_dimensions['C'].width = 28  # Name

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


class NumberedCanvas(canvas.Canvas):
    """Custom ReportLab canvas for dynamic multi-page 'Page X of Y' numbering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        page_w, page_h = self._pagesize
        
        # Footer text & line
        gen_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        footer_left = f"CampusSync ERP · Official Internal Assessment Report · {gen_time}"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(20, 22, page_w - 20, 22)
        
        self.drawString(20, 12, footer_left)
        self.drawRightString(page_w - 20, 12, footer_right)
        self.restoreState()


def generate_internal_marks_pdf(data_dict, faculty_name="Faculty"):
    """
    Generates a high-quality ReportLab PDF document for Internal Marks.
    Excludes the internal 'Status' column from the generated table.
    
    Args:
        data_dict (dict): Dictionary returned by get_faculty_marks_students
        faculty_name (str): Logged-in faculty member's full name
        
    Returns:
        io.BytesIO: Buffer containing generated PDF file
    """
    subject = data_dict.get("subject", {})
    subject_code = subject.get("subject_code", "")
    subject_name = subject.get("subject_name", "")
    subject_type = subject.get("subject_type", "Theory")
    max_internal = subject.get("internal_marks", 50 if subject_type == 'Theory' else 25)
    
    academic_year = data_dict.get("academic_year", "")
    semester = data_dict.get("semester", "")
    division = data_dict.get("division", "")
    students = list(data_dict.get("students", []))
    students.sort(key=lambda s: (_parse_roll_num(s.get("roll_number")), s.get("full_name", "").lower()))

    is_theory = (subject_type == 'Theory')
    pagesize = landscape(A4) if is_theory else portrait(A4)

    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=pagesize,
        leftMargin=15 if is_theory else 25,
        rightMargin=15 if is_theory else 25,
        topMargin=20,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=8
    )

    meta_lbl_style = ParagraphStyle(
        'MetaLabel',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569')
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    th_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7 if is_theory else 8.5,
        leading=8.5 if is_theory else 10.5,
        textColor=colors.white,
        alignment=1
    )

    td_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7 if is_theory else 8.5,
        leading=8.5 if is_theory else 10.5,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )

    td_name_style = ParagraphStyle(
        'TableNameCell',
        fontName='Helvetica-Bold',
        fontSize=7 if is_theory else 8.5,
        leading=8.5 if is_theory else 10.5,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("BCA COLLEGE PALANPUR", title_style))
    story.append(Paragraph(f"INTERNAL ASSESSMENT MARKS SHEET ({subject_type.upper()})", subtitle_style))

    # Metadata Table Block
    meta_data = [
        [
            Paragraph("<b>Academic Year:</b>", meta_lbl_style), Paragraph(str(academic_year), meta_val_style),
            Paragraph("<b>Semester:</b>", meta_lbl_style), Paragraph(f"Semester {semester}", meta_val_style),
            Paragraph("<b>Division:</b>", meta_lbl_style), Paragraph(str(division), meta_val_style)
        ],
        [
            Paragraph("<b>Subject Code:</b>", meta_lbl_style), Paragraph(str(subject_code), meta_val_style),
            Paragraph("<b>Subject Name:</b>", meta_lbl_style), Paragraph(str(subject_name), meta_val_style),
            Paragraph("<b>Faculty:</b>", meta_lbl_style), Paragraph(str(faculty_name), meta_val_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[65, 95, 50, 160, 45, 160] if is_theory else [75, 90, 55, 130, 45, 120])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Table Header & Data Rows (14 columns for Theory, 7 for Practical)
    from services.subject_service import get_subject_component_config
    comp_cfg = get_subject_component_config(subject)
    maxes = comp_cfg["maxes"] if comp_cfg else {}

    if is_theory:
        att_m = maxes.get("attendance", 5.0)
        headers = [
            "Roll", "Enrollment", "Student Name",
            "T1", "T2", "T3", "Best 2",
            "Int Exam",
            "Act", "Class", "Home",
            "Att%", f"Att/{att_m:g}",
            f"Total /{max_internal}"
        ]
        # Landscape A4 usable width = 842 - 30 = 812pt
        col_widths = [32, 85, 170, 32, 32, 32, 42, 55, 36, 40, 40, 44, 44, 58]
    else:
        ie_m = maxes.get("internal_exam", 10.0)
        pe_m = maxes.get("practical_eval", 10.0)
        jo_m = maxes.get("journal", 5.0)
        headers = [
            "Roll", "Enrollment No", "Student Name",
            f"Viva / Interview /{ie_m:g}", f"Coding / Practical /{pe_m:g}", f"Journal /{jo_m:g}",
            f"Internal /{max_internal}"
        ]
        # Portrait A4 usable width = 595 - 50 = 545pt
        col_widths = [35, 95, 145, 80, 80, 50, 60]

    table_data = [[Paragraph(h, th_style) for h in headers]]

    for st in students:
        bd = st.get("breakdown") or {}

        if is_theory:
            best_2 = _calc_best_tests(bd)
            
            att_val = bd.get("attendance")
            att_max_val = maxes.get("attendance", 5.0)
            if att_val is not None:
                att_pct_str = f"{round((float(att_val) / att_max_val) * 100, 0):.0f}%"
                att_num_str = f"{float(att_val):g}"
            else:
                att_pct_str = "-"
                att_num_str = "-"

            tot_val = st.get("marks_obtained")
            tot_str = f"<b>{float(tot_val):g}</b>" if tot_val is not None else "-"

            row_cells = [
                str(st.get("roll_number", "")),
                str(st.get("enrollment_no", "")),
                Paragraph(str(st.get("full_name", "")), td_name_style),
                str(bd.get("test1")) if bd.get("test1") is not None else "-",
                str(bd.get("test2")) if bd.get("test2") is not None else "-",
                str(bd.get("test3")) if bd.get("test3") is not None else "-",
                str(best_2) if best_2 is not None else "-",
                str(bd.get("internal_exam")) if bd.get("internal_exam") is not None else "-",
                str(bd.get("active_learning")) if bd.get("active_learning") is not None else "-",
                str(bd.get("class_assignment")) if bd.get("class_assignment") is not None else "-",
                str(bd.get("home_assignment")) if bd.get("home_assignment") is not None else "-",
                att_pct_str,
                att_num_str,
                Paragraph(tot_str, td_style)
            ]
        else:
            tot_val = st.get("marks_obtained")
            tot_str = f"<b>{float(tot_val):g}</b>" if tot_val is not None else "-"

            row_cells = [
                str(st.get("roll_number", "")),
                str(st.get("enrollment_no", "")),
                Paragraph(str(st.get("full_name", "")), td_name_style),
                str(bd.get("internal_exam")) if bd.get("internal_exam") is not None else "-",
                str(bd.get("practical_eval")) if bd.get("practical_eval") is not None else "-",
                str(bd.get("journal")) if bd.get("journal") is not None else "-",
                Paragraph(tot_str, td_style)
            ]

        table_data.append([
            c if isinstance(c, Paragraph) else Paragraph(str(c), td_style)
            for c in row_cells
        ])

    marks_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Base Table Style
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
    ]

    # Zebra striping for table data rows
    for r_i in range(1, len(table_data)):
        if r_i % 2 == 0:
            t_style.append(('BACKGROUND', (0, r_i), (-1, r_i), colors.HexColor('#F8FAFC')))

    # Total column background highlight (14th col for Theory = index 13; 7th col for Practical = index 6)
    tot_col_idx = 13 if is_theory else 6
    t_style.append(('BACKGROUND', (tot_col_idx, 1), (tot_col_idx, -1), colors.HexColor('#EFF6FF')))
    t_style.append(('TEXTCOLOR', (tot_col_idx, 1), (tot_col_idx, -1), colors.HexColor('#1E40AF')))

    marks_table.setStyle(TableStyle(t_style))
    story.append(marks_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    output.seek(0)
    return output


def generate_student_result_pdf(data_dict):
    """
    Generates an official single-student Internal Assessment Result PDF document using ReportLab.
    Matches the official BCA College Palanpur design:
    - College Logo + College Name + Title
    - Student Profile Info Box (2 columns)
    - Clean 5-column Subject-wise Internal Result Table
    - Result Summary with Highlighted Percentage Box
    - Official Verification Footer (College Stamp + Principal Signature)
    """
    college = data_dict.get("college", {})
    student = data_dict.get("student", {})
    results = data_dict.get("results", [])
    sem = data_dict.get("semester", student.get("semester", 1))
    ay = data_dict.get("academic_year", "2026-27")

    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=portrait(A4),
        leftMargin=30,
        rightMargin=30,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    # Typography styles
    c_name = ParagraphStyle(
        'ColName',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=19,
        textColor=colors.HexColor('#0F3460'),
        alignment=1,
        spaceAfter=3
    )
    c_sub = ParagraphStyle(
        'ColSub',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1,
        spaceAfter=6
    )
    section_title = ParagraphStyle(
        'SecTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0F2B5C'),
        spaceBefore=10,
        spaceAfter=6
    )
    info_lbl = ParagraphStyle('InfoLbl', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#334155'))
    info_val = ParagraphStyle('InfoVal', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#0F172A'))

    th_center = ParagraphStyle('THC', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#1E293B'), alignment=1)
    th_left = ParagraphStyle('THL', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#1E293B'), alignment=0)
    td_center = ParagraphStyle('TDC', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#334155'), alignment=1)
    td_bold_center = ParagraphStyle('TDBC', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#0F172A'), alignment=1)
    td_left = ParagraphStyle('TDL', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#334155'), alignment=0)

    perc_lbl = ParagraphStyle('PercLbl', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=colors.HexColor('#0284C7'), alignment=1)
    perc_val = ParagraphStyle('PercVal', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0284C7'), alignment=1)

    sig_lbl = ParagraphStyle('SigLbl', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'), alignment=1)
    sig_name = ParagraphStyle('SigName', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0F172A'), alignment=1)
    sig_sub = ParagraphStyle('SigSub', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#64748B'), alignment=1)

    story = []

    # Uploads directory path
    base_dir = current_app.root_path if current_app else os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    upload_college_dir = os.path.join(base_dir, 'uploads', 'college')

    # 1. Header with Logo & Title
    logo_filename = college.get("logo")
    logo_flowable = None
    if logo_filename:
        logo_path = os.path.join(upload_college_dir, logo_filename)
        if os.path.isfile(logo_path):
            try:
                logo_flowable = RLImage(logo_path, width=54, height=54)
            except Exception:
                logo_flowable = None

    college_title_text = (college.get("college_name") or "BCA COLLEGE PALANPUR").upper()
    header_title_cells = [
        Paragraph(college_title_text, c_name),
        Paragraph("INTERNAL ASSESSMENT RESULT", c_sub)
    ]

    if logo_flowable:
        header_table = Table([[logo_flowable, header_title_cells]], colWidths=[65, 470])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph(college_title_text, c_name))
        story.append(Paragraph("INTERNAL ASSESSMENT RESULT", c_sub))

    story.append(Spacer(1, 8))

    # 2. Student Info Box (2 columns matching HTML layout)
    # Total width = 535
    info_data = [
        [
            Paragraph("Student Name", info_lbl), Paragraph(f":  {student.get('full_name', '-')}", info_val),
            Paragraph("Semester", info_lbl), Paragraph(f":  {sem}", info_val)
        ],
        [
            Paragraph("Enrollment No", info_lbl), Paragraph(f":  {student.get('enrollment_no', '-')}", info_val),
            Paragraph("Division", info_lbl), Paragraph(f":  {student.get('division', 'A')}", info_val)
        ],
        [
            Paragraph("Roll No", info_lbl), Paragraph(f":  {student.get('roll_number', '-')}", info_val),
            Paragraph("Academic Year", info_lbl), Paragraph(f":  {ay}", info_val)
        ],
        [
            Paragraph("Course", info_lbl), Paragraph(f":  {student.get('course', 'BCA')}", info_val),
            Paragraph("", info_lbl), Paragraph("", info_val)
        ]
    ]
    info_table = Table(info_data, colWidths=[100, 185, 90, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#DBEAFE')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Subject-wise Internal Result Table (Clean 5 columns)
    story.append(Paragraph("Subject-wise Internal Result", section_title))
    headers = [
        Paragraph("Sr.", th_center),
        Paragraph("Subject Code", th_left),
        Paragraph("Subject Name", th_left),
        Paragraph("Internal Marks", th_center),
        Paragraph("Max Marks", th_center)
    ]
    table_rows = [headers]

    for idx, r in enumerate(results, start=1):
        m_obt = r.get('marks_obtained')
        if m_obt is not None:
            m_obt_str = str(int(m_obt)) if float(m_obt).is_integer() else str(m_obt)
        else:
            m_obt_str = "-"

        m_max = r.get('max_marks', 50)
        m_max_str = str(int(m_max)) if float(m_max).is_integer() else str(m_max)

        row_cells = [
            Paragraph(str(idx), td_center),
            Paragraph(str(r.get("subject_code", "-")), td_left),
            Paragraph(str(r.get("subject_name", "-")), td_left),
            Paragraph(m_obt_str, td_bold_center),
            Paragraph(m_max_str, td_center)
        ]
        table_rows.append(row_cells)

    # 35 + 95 + 235 + 85 + 85 = 535
    sub_table = Table(table_rows, colWidths=[35, 95, 235, 85, 85])
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
    ]
    for r_i in range(1, len(table_rows)):
        if r_i % 2 == 0:
            t_style.append(('BACKGROUND', (0, r_i), (-1, r_i), colors.HexColor('#F8FAFC')))
    sub_table.setStyle(TableStyle(t_style))
    story.append(sub_table)
    story.append(Spacer(1, 10))

    # 4. Result Summary (Left metrics + Right Percentage Card)
    story.append(Paragraph("Result Summary", section_title))
    tot_sub = len(results)
    tot_obt = data_dict.get('total_obtained', 0)
    tot_obt_str = str(int(tot_obt)) if float(tot_obt).is_integer() else str(tot_obt)
    tot_max = data_dict.get('total_max', 0)
    tot_max_str = str(int(tot_max)) if float(tot_max).is_integer() else str(tot_max)
    perc = data_dict.get('overall_percentage', 0.0)

    summary_left_data = [
        [Paragraph("Total Subjects", info_lbl), Paragraph(f":  {tot_sub}", info_val)],
        [Paragraph("Total Internal Marks", info_lbl), Paragraph(f":  {tot_obt_str}", info_val)],
        [Paragraph("Total Max Marks", info_lbl), Paragraph(f":  {tot_max_str}", info_val)],
    ]
    summary_left_table = Table(summary_left_data, colWidths=[130, 180])
    summary_left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Percentage Card Table
    perc_table_data = [
        [Paragraph("Percentage", perc_lbl)],
        [Paragraph(f"{perc:.2f}%", perc_val)]
    ]
    perc_table = Table(perc_table_data, colWidths=[175])
    perc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#BAE6FD')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    summary_wrapper = Table([[summary_left_table, perc_table]], colWidths=[340, 195])
    summary_wrapper.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(summary_wrapper)
    story.append(Spacer(1, 16))

    # 5. Official Verification Footer (Stamp on left, Signature on right)
    stamp_filename = college.get("college_stamp") or "default-stamp.png"
    stamp_path = os.path.join(upload_college_dir, stamp_filename)
    stamp_flowable = None
    if os.path.isfile(stamp_path):
        try:
            stamp_flowable = RLImage(stamp_path, width=72, height=72)
        except Exception:
            stamp_flowable = None

    sig_filename = college.get("principal_signature") or "default-signature.png"
    sig_path = os.path.join(upload_college_dir, sig_filename)
    sig_flowable = None
    if os.path.isfile(sig_path):
        try:
            sig_flowable = RLImage(sig_path, width=105, height=42)
        except Exception:
            sig_flowable = None

    principal_name_str = college.get("principal_name") or "Dr. Principal"
    today_str = datetime.utcnow().strftime('%d/%m/%Y')

    # Left cell: Stamp
    left_cell_items = []
    if stamp_flowable:
        left_cell_items.append(stamp_flowable)
        left_cell_items.append(Spacer(1, 2))
    left_cell_items.append(Paragraph("College Official Seal", sig_lbl))

    # Center cell: Issue Notice
    center_cell_items = [
        Spacer(1, 20),
        Paragraph("Verified & System Generated", sig_sub),
        Paragraph(f"Date: {today_str}", sig_sub)
    ]

    # Right cell: Signature
    right_cell_items = []
    if sig_flowable:
        right_cell_items.append(sig_flowable)
        right_cell_items.append(Spacer(1, 2))
    else:
        right_cell_items.append(Spacer(1, 35))
    right_cell_items.append(Paragraph("Principal Signature", sig_lbl))
    right_cell_items.append(Paragraph(principal_name_str, sig_name))

    footer_table = Table([[left_cell_items, center_cell_items, right_cell_items]], colWidths=[185, 165, 185])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(KeepTogether([footer_table]))

    doc.build(story)
    output.seek(0)
    return output

