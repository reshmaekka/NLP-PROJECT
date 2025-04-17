# MCQ Generator Web App

This is a Flask web application that allows users to upload various document formats and generate multiple-choice questions (MCQs) from the content using Google's Gemini API.

## Features

- 📄 Supports file uploads: PDF, TXT, DOCX, HTML, XLSX, and CSV.
- 🤖 Uses Google Gemini (Generative AI) to generate MCQs.
- 📝 Outputs the questions in both text and PDF formats.
- 📥 Provides download links for the generated MCQs.

## Technologies Used

- Python
- Flask
- Google Generative AI (`google.generativeai`)
- pdfplumber
- python-docx
- pandas
- fpdf
- openpyxl
- HTML/CSS for frontend

## Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/mcq-generator.git
   cd mcq-generator
