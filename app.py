from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory to store the PDFs
PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)  # Read the Excel file
        pdf_links = generate_pdfs(df)
        # Render the download.html template with the links to the PDFs
        return render_template('download.html', pdf_links=pdf_links)
    else:
        return jsonify({'error': 'Invalid file format. Please upload an Excel file.'}), 400



def generate_pdfs(df):
    """ Generate individual PDFs for each student in the DataFrame """
    pdf_links = []
    logo_path = 'logo.png'  # Path to the logo image
    college_name = "KS Rangasamy College of Technology"
    department_name = "Department of Computer Science and Engineering"

    for index, row in df.iterrows():
        student_name = row['Name']
        marks = row['Marks']
        pdf_file = f"{PDF_DIR}/{student_name}.pdf"
        
        # Create PDF
        c = canvas.Canvas(pdf_file, pagesize=letter)

        # Draw the college logo
        c.drawImage(logo_path, 30, 680, width=500, height=100)  # Adjust the position and size as needed
        
        # Draw college name and department in a box
        c.setStrokeColorRGB(0, 0, 0)  # Set border color
        c.rect(30, 620, 400, 50)  # Draw the rectangle
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, 645, college_name)
        c.setFont("Helvetica", 12)
        c.drawString(40, 630, department_name)

        # Add student details
        c.setFont("Helvetica", 12)
        c.drawString(100, 580, f"Student: {student_name}")
        c.drawString(100, 560, f"Marks: {marks}")
        c.save()

        # Add link to the generated PDF
        pdf_links.append(f"http://localhost:5000/download/{student_name}.pdf")
    
    return pdf_links

@app.route('/download/<filename>')
def download_file(filename):
    """ Serve the generated PDF for download """
    return send_file(os.path.join(PDF_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
