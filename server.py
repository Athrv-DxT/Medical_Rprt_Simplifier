import os
import pandas as pd
import pdfplumber
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Define the upload folder and output folder
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Helper function to extract tables and text from the PDF
def extract_pdf_content(pdf_path):
    """Extract tables and text content from a PDF file."""
    tables = []
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables
            tables_on_page = page.extract_tables()
            for table in tables_on_page:
                table_df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(table_df)
            # Extract text
            text_content += page.extract_text()
    return tables, text_content


# Helper function to extract hemoglobin value from text
def extract_hemoglobin_value(text_content):
    """Extract the hemoglobin value from the text content."""
    # Example regex pattern for matching a hemoglobin value (e.g., 'Hemoglobin: 13.5 g/dL')
    pattern = r"hemoglobin.*?(\d+(\.\d+)?)\s*(g/dL|g/L)"
    match = re.search(pattern, text_content, re.IGNORECASE)
    
    if match:
        # Extracted value (first group in the regex match)
        return float(match.group(1))
    else:
        return None

# Updated diagnosis function to include hemoglobin level validation
def diagnose_data(tables, text_content):
    """Diagnose data based on the extracted tables and text content."""
    diagnosis = []
    
    # Check for hemoglobin value and compare it to normal range
    hemoglobin_value = extract_hemoglobin_value(text_content)
    if hemoglobin_value is not None:
        if 12 <= hemoglobin_value <= 15:  # Example range for women
            diagnosis.append(f"Hemoglobin levels are normal: {hemoglobin_value} g/dL.")
        elif 13 <= hemoglobin_value <= 17:  # Example range for men
            diagnosis.append(f"Hemoglobin levels are normal: {hemoglobin_value} g/dL.")
        else:
            diagnosis.append(f"Hemoglobin levels are abnormal: {hemoglobin_value} g/dL.")
    else:
        diagnosis.append("Hemoglobin data not found or abnormal.")
    
    # Additional diagnosis logic for other tests (RBC, ESR, etc.)...
    
    return diagnosis

# Flask route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload PDF file and diagnose the results."""
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Extract content from the PDF
        tables, text_content = extract_pdf_content(file_path)

        # Diagnose data from the extracted content
        diagnosis_results = diagnose_data(tables, text_content)

        # Save output files
        table_output_path = os.path.join(OUTPUT_FOLDER, 'tables_output.csv')
        text_output_path = os.path.join(OUTPUT_FOLDER, 'text_output.txt')

        # Save the tables as CSV with utf-8 encoding
        with open(table_output_path, 'w', newline='', encoding='utf-8') as f:
            for table in tables:
                table.to_csv(f, index=False)

        # Save the extracted text with utf-8 encoding
        with open(text_output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # Return a success message with the paths to the generated files
        return jsonify({
            "status": "success",
            "message": "File processed successfully",
            "diagnosis": diagnosis_results,
            "table_file_path": table_output_path,
            "text_file_path": text_output_path
        }), 200
    else:
        return jsonify({"message": "Invalid file type. Only PDF files are allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True)
