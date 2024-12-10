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

# Define the normal ranges for various parameters
parameter_ranges = {
    "hemoglobin": (12, 17),  # Example range (g/dL)
    "RBC": (3.8, 4.8),  # Example range (x10^12/L)
    "PCV": (36, 46),    # Example range (%)
    "MCV": (83, 101),   # Example range (fL)
    "TLC": (4, 10),      # Example range (x10^9/L)
    "Neutrophils": (40, 80),  # Example range (%)
    "Lymphocytes": (20, 40),  # Example range (%)
    "Platelet Count": (150, 410),  # Example range (x10^9/L)
    "MPV": (9.3, 12.1)  # Example range (fL)
}

# Helper function to extract numerical values for a specific parameter from text
def extract_value_from_text(parameter, text_content):
    """Extract a numerical value for a specific parameter from text content."""
    # This the regex pattern for matching a parameter value (e.g., 'RBC: 4.5 x10^12/L')
    pattern = rf"{parameter}.*?(\d+(\.\d+)?)\s*(x10\^12/L|g/dL|fL|x10\^9/L|%)"
    match = re.search(pattern, text_content, re.IGNORECASE)
    
    if match:
        # Extracted value (first group in the regex match)
        return float(match.group(1))
    else:
        return None

# Helper function to diagnose individual parameters
def diagnose_parameter(parameter, value):
    """Diagnose the value based on its normal range."""
    min_value, max_value = parameter_ranges.get(parameter, (None, None))
    
    if min_value is None or max_value is None:
        return f"No reference range available for {parameter}."
    
    if value is None:
        return f"{parameter} data not found."
    
    if min_value <= value <= max_value:
        return f"{parameter} is within the normal range: {value}."
    else:
        return f"{parameter} is abnormal: {value}."

# Updated diagnose function to include hemoglobin and other parameters
def diagnose_data(tables, text_content):
    """Diagnose data based on the extracted tables and text content."""
    diagnosis = []
    
    # Check for hemoglobin value and compare it to normal range
    hemoglobin_value = extract_value_from_text("hemoglobin", text_content)
    if hemoglobin_value is not None:
        if 12 <= hemoglobin_value <= 15:  # Example range for women
            diagnosis.append(f"Hemoglobin levels are normal: {hemoglobin_value} g/dL.")
        elif 13 <= hemoglobin_value <= 17:  # Example range for men
            diagnosis.append(f"Hemoglobin levels are normal: {hemoglobin_value} g/dL.")
        else:
            diagnosis.append(f"Hemoglobin levels are abnormal: {hemoglobin_value} g/dL.")
            if hemoglobin_value < 12:  # Specific message if hemoglobin is low
                diagnosis.append("""
                **If your hemoglobin levels are low**, it’s often because your body isn’t getting enough of the nutrients it needs to make healthy red blood cells. Here are some simple remedies and lifestyle tips to improve hemoglobin levels:

                ### 1. *Eat Iron-Rich Foods*
                Iron is the main building block for hemoglobin. Include foods like:
                   - Spinach, kale, and other leafy greens 🥬
                   - Lentils and beans (like chickpeas and kidney beans) 🌱
                   - Red meat, chicken, and fish 🍖🐟
                   - Tofu and soy products
                   - Fortified cereals and bread
                   - Pumpkin seeds and nuts (like almonds and cashews)

                ### 2. *Vitamin C Helps Absorb Iron*
                Pair iron-rich foods with vitamin C to help your body absorb the iron better. Add these to your meals:
                   - Oranges, strawberries, and kiwis 🍊🍓
                   - Tomatoes and bell peppers 🍅
                   - Broccoli and cauliflower

                ### 3. *Boost Folate Intake*
                Folate (vitamin B9) helps your body make red blood cells. Eat:
                   - Leafy greens (again!) 🥗
                   - Avocados 🥑
                   - Bananas 🍌
                   - Eggs 🥚

                ### 4. *Get Enough Vitamin B12*
                Vitamin B12 is another key player for healthy hemoglobin levels. Find it in:
                   - Meat, fish, and dairy 🥩🧀
                   - Eggs 🍳
                   - Fortified cereals or supplements (especially for vegetarians/vegans)

                ### 5. *Avoid Iron Blockers*
                Some foods and drinks can block iron absorption if consumed in excess, such as:
                   - Tea and coffee ☕
                   - Foods high in calcium (like milk and cheese) during iron-rich meals 🥛

                ### 6. *Stay Hydrated*
                Proper hydration ensures good blood flow, helping red blood cells do their job. Drink enough water every day! 💧

                ### 7. *Consider Supplements*
                If food alone isn’t enough, talk to a doctor about taking iron or multivitamin supplements. But don’t self-medicate—too much iron can be harmful.

                ### 8. *Check for Underlying Issues*
                Sometimes low hemoglobin is caused by something like anemia, chronic disease, or a vitamin deficiency. If your levels stay low despite eating well, see a doctor for advice.

                Good food + proper care = healthy blood and a stronger you! 💪
                """)
    else:
        diagnosis.append("Hemoglobin data not found or abnormal.")
    
    # Check and diagnose other parameters (RBC, PCV, MCV, etc.)
    for parameter in parameter_ranges.keys():
        value = extract_value_from_text(parameter, text_content)
        diagnosis.append(diagnose_parameter(parameter, value))
 
    return diagnosis


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
