import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import mysql.connector

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
PDF_DIR = 'generated_pdfs'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_DIR'] = PDF_DIR

# Database configuration
DB_CONFIG = {
    'user': 'root',          # Change to your MySQL username
    'password': '',          # Change to your MySQL password
    'host': '127.0.0.1',    # Change if your MySQL server is on a different host
    'database': 'student_grades'
}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_student_name(register_number):
    """Fetch student name from the database using register number."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM students WHERE register_number = %s", (register_number,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else None

def get_course_name(course_code):
    """Fetch course name from the database using course code."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT course_name FROM courses WHERE course_code = %s", (course_code,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else None

def get_credit(course_code):
    """Fetch course credit from the database using course code."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT credit FROM courses WHERE course_code = %s", (course_code,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else 0

def get_grade_point(grade):
    """Fetch grade point from the database using grade."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT points FROM grade_points WHERE grade = %s", (grade,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else 0

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and PDF generation."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            df = pd.read_excel(filename)
            
            df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
            
            pdf_links = generate_pdfs(df)
            return render_template('download.html', pdf_links=pdf_links)
        else:
            return jsonify({'error': 'Invalid file format. Please upload an Excel (.xlsx) file.'}), 400
    return render_template('upload.html')

def calculate_sgpa(grades, credits):
    total_points = 0
    total_credits = 0

    for grade, credit in zip(grades, credits):
        grade_point = get_grade_point(grade)
        total_points += grade_point * credit
        total_credits += credit

    # To avoid division by zero
    return total_points / total_credits if total_credits > 0 else 0

def generate_pdfs(df):
    """Generate individual PDFs for each student."""
    pdf_links = []
    logo_path = 'logo.png'  # Replace with your logo path
    college_name = "K S RANGASAMY COLLEGE OF TECHNOLOGY, TIRUCHENGODE"
    sub_heading = "(An Autonomous Institution Affiliated to Anna University, Chennai)"
    department_name = "Department of Computer Science and Engineering"
    footer_sign1 = "HOD Sign"
    footer_sign2 = "M.Varshana Devi"
    footer_title2 = "Class Advisor"

    # Group the data by register number
    grouped = df.groupby('register_number')

    for register_number, group in grouped:
        # Fetch the student name for the current register number
        student_name = get_student_name(register_number)

        if not student_name:
            print(f"No student found for register number: {register_number}")
            continue  # Skip this group if the student is not found

        pdf_file = os.path.join(app.config['PDF_DIR'], f"{student_name}.pdf")  # Use student name for the PDF filename

        c = canvas.Canvas(pdf_file, pagesize=letter)
        width, height = letter

        # Header Section
        c.drawImage(logo_path, x=(width - 150) / 2, y=height - 100, width=150, height=60)
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(width / 2, height - 120, college_name)

        c.setFont('Helvetica', 12)
        c.drawCentredString(width / 2, height - 140, sub_heading)
        c.drawCentredString(width / 2, height - 160, department_name)

        # Student Info Section
        c.setFont('Helvetica', 12)
        info_text = (
            f"Dear Parents,\n\nThe daughter/son of yours {student_name} "
            "is studying B.E CSE in II Year / III Sem & A/B Section. "
            "The End Semester Grade and the details of courses are given below."
        )
        text_object = c.beginText(40, height - 220)
        text_object.textLines(info_text)
        c.drawText(text_object)

        # Grades Table
        table_data = [['S.No', 'Course Code', 'Course Name', 'Grade']]
        grades = []
        credits = []
        
        for i, (index, row) in enumerate(group.iterrows(), start=1):
            course_name = get_course_name(row['CourseCode'])
            course_credit = get_credit(row['CourseCode'])
            grades.append(row['Grade'])  # Store the grade for SGPA calculation
            credits.append(course_credit)  # Store the credit for SGPA calculation
            table_data.append([str(i), row['CourseCode'], course_name, row['Grade']])

        # Adjust the column widths, especially for 'Course Name'
        table = Table(table_data, colWidths=[50, 100, 200, 100])  # Increased width for Course Name
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(c, width, height)
        table.drawOn(c, 40, height - 450)

        # Calculate SGPA
        sgpa = calculate_sgpa(grades, credits)

        # Footer Section
        footer_text = (
            "Total Number of Arrears: None\n"
            f"SGPA: {sgpa:.2f}\n"
            "Distinction: >= 8.5 & no history of arrears, First Class: >= 7, Second Class: < 7\n"
            "Attendance Percentage of your ward (as on 03.10.2023): 90.37%\n"
            "Contact Number: Class Advisors - A: 9597604228, B: 9345251112"
        )
        text_object = c.beginText(40, height - 500)
        text_object.textLines(footer_text)
        c.drawText(text_object)

        # Signature Section
        c.setFont('Helvetica', 12)
        c.drawString(100, 120, f"{footer_sign1}")
        c.drawString(400, 120, f"{footer_sign2}")
        c.drawString(400, 100, f"{footer_title2}")

        # Save the PDF
        c.save()
        pdf_links.append(pdf_file)

    return pdf_links


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Serve the PDF file for download."""
    return send_from_directory(app.config['PDF_DIR'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
