from flask import Flask, request, render_template, send_file
import os  
import pdfplumber  # Extract text from PDFs
import docx  # Extract text from DOCX, TXT, HTML
import pandas as pd  # Handle CSV & XLSX
from fpdf import FPDF  # Convert text to PDF
import google.generativeai as genai  # Google AI for MCQ generation
from werkzeug.utils import secure_filename

# Configure API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBXX8mrLlkkPp16x1M3a5N9K_YdqPn2zUE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Flask App Setup
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx', 'html', 'xlsx', 'csv'}

# Ensure Directories Exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# File Type Checker
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Extract Text from Files
def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            return '\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif ext == 'docx':
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif ext == 'xlsx':
        df = pd.read_excel(file_path, engine='openpyxl')
        return df.to_string(index=False)
    elif ext == 'csv':
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    return ""

# Generate MCQs using Gemini API
def generate_mcqs(text, num_questions):
    prompt = f"""
    Generate {num_questions} multiple-choice questions (MCQs) based on the text below:
    
    ""{text}""
    
    Format:
    ## MCQ
    Question: [Question]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    Correct Answer: [Correct Option]
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# Save MCQs to File
def save_to_file(content, filename):
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

# Convert MCQs to PDF
def save_to_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for mcq in content.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)
    pdf_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    pdf.output(pdf_path)
    return pdf_path

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return "Invalid file format", 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    text = extract_text_from_file(file_path)
    if not text:
        return "Failed to extract text", 400
    
    try:
        num_questions = int(request.form['num_questions'])
        if num_questions <= 0:
            raise ValueError
    except (KeyError, ValueError):
        return "Invalid number of questions", 400
    
    mcqs = generate_mcqs(text, num_questions)
    txt_file = f"mcqs_{filename.rsplit('.', 1)[0]}.txt"
    pdf_file = f"mcqs_{filename.rsplit('.', 1)[0]}.pdf"
    save_to_file(mcqs, txt_file)
    save_to_pdf(mcqs, pdf_file)
    
    return render_template('results.html', mcqs=mcqs, txt_filename=txt_file, pdf_filename=pdf_file)

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['RESULTS_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
