import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import mysql.connector
from datetime import datetime

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
        if grade == "U":
            continue  # Skip grades that are "U" (arrears)
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
    footer_title2 = "HOD"
    footer_sign2 = ""
    footer_sign1 = "Class Advisor"

    # Get current date and format it
    current_date = datetime.now().strftime("Date : %d/%m/%Y")

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

        # Space below the logo
        space_below_logo = 20  # Adjust this value for more/less space
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(width / 2, height - 110 - space_below_logo, college_name)

        c.setFont('Helvetica', 12)
        c.drawCentredString(width / 2, height - 130 - space_below_logo, sub_heading)
        c.drawCentredString(width / 2, height - 150 - space_below_logo, department_name)

        # Add "End Semester Grade" in bold below the department name
        c.setFont('Helvetica-Bold', 14)  # Set font to bold for this text
        c.drawCentredString(width / 2, height - 175 - space_below_logo, "End Semester Grade")

        # Reset to regular font for subsequent text
        c.setFont('Helvetica', 12)

        # Student Info Section
        dear_parents_x = 40
        dear_parents_y = height - 220
        date_x = dear_parents_x + 400

        c.drawString(dear_parents_x, dear_parents_y, "Dear Parents,")
        c.drawString(date_x, dear_parents_y, current_date)

        info_text = (
            f"\nThe daughter/son of yours {student_name} is studying B.E CSE in II Year / IV Sem & A/B Section. "
            "\nThe End Semester Grade and the details of courses are given below."
        )
        text_object = c.beginText(40, dear_parents_y - 30)
        text_object.textLines(info_text)
        c.drawText(text_object)

        # Grades Table
        table_data = [['S.No', 'Course Code', 'Course Name', 'Grade']]
        grades = []
        credits = []
        arrear_count = 0

        for i, (index, row) in enumerate(group.iterrows(), start=1):
            course_name = get_course_name(row['CourseCode'])
            course_credit = get_credit(row['CourseCode'])
            grades.append(row['Grade'])
            credits.append(course_credit)

            if row['Grade'] == "U":
                arrear_count += 1

            table_data.append([str(i), row['CourseCode'], course_name, row['Grade']])

        # Calculate SGPA
        sgpa = calculate_sgpa(grades, credits)

        # Insert SGPA row as the 9th row, spanning 3 columns
        if len(table_data) < 9:
            # Fill in with empty rows until we reach the 9th row
            while len(table_data) < 9:
                table_data.append(['', '', '', ''])


        # Insert SGPA into the 9th row (position 8 as Python is zero-indexed)
        table_data[8] = ['SGPA', '', '', f"{sgpa:.2f}"]

        # Add the Distinction/First Class/Second Class row spanning all columns
        distinction_text = "Distinction: >= 8.5 & no history of arrears, First Class: >= 7, Second Class: < 7"
        table_data.append([distinction_text, '', '', ''])

        # Adjust the column widths
        table = Table(table_data, colWidths=[50, 100, 200, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, -2), (2, -2)),  # Span for SGPA across 3 columns
            ('SPAN', (0, -1), (-1, -1)),  # Span the entire row for Distinction line
        ]))

        table_width = sum([50, 100, 200, 100])
        table_x = ((width - table_width) / 2) - 5
        table_padding_top = 40
        table_y = height - 450 - table_padding_top

        table.wrapOn(c, width, height)
        table.drawOn(c, table_x, table_y)

        # Grade classification lines moved here
        c.setFont('Helvetica', 10)  # Set smaller font size for grade info
        grade_info_line1 = "91-100 Grade 'O'; 81-90 Grade 'A+'; 71-80 Grade 'A'; 61-70 Grade 'B+'; 51-60 Grade 'B'"
        grade_info_line2 = "50-59 Grade 'C'; 0-49 Grade 'U'; AB - Absent; WH - Withheld"

        # Calculate the Y position for the grade info lines
        grade_info_y_position = table_y - 30  # Adjust this value to control the spacing above the footer
        c.drawCentredString(width / 2, grade_info_y_position, grade_info_line1)  # Adjust Y position as needed
        c.drawCentredString(width / 2, grade_info_y_position - 20, grade_info_line2)  # Adjust Y position as needed

        # Footer Section
        arrear_text = "None" if arrear_count == 0 else str(arrear_count)
        footer_text = (
            f"Total Number of Arrears: {arrear_text}\n"
            f"Attendance Percentage of your ward as on : {current_date.split(': ')[-1]}"
            "______________\n"
           
        )

        c.setFont('Helvetica', 10)
        Contact = "Contact Number: Class Advisors - A:9591604228 , 9894999098, B:9345215112 , 9994049209"
        Contact_position = table_y - 30
        c.drawCentredString(width / 2, Contact_position - 140, Contact)





        c.setFont('Helvetica', 10)
        text_object_footer = c.beginText(40, table_y - 100)  # This position should match the footer text
        text_object_footer.textLines(footer_text)
        c.drawText(text_object_footer)

        # Signature Section
        c.setFont('Helvetica', 12)
        c.drawString(100, 50, f"{footer_sign1}")
        c.drawString(430, 50, f"{footer_title2}  {footer_sign2}")

        c.save()
        
        # Append only the filename, not the full path
        pdf_links.append(f"{student_name}.pdf")

    return pdf_links




@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Serve the PDF file for download."""
    return send_from_directory(app.config['PDF_DIR'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 
