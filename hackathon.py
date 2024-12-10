# sample code for pdf extractor

import PyPDF2

def read_pdf(file_path):
    """
    Reads the content of a PDF file and extracts text.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    text = ""
    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Loop through all pages
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"An error occurred while reading the PDF: {e}"

# Example usage
pdf_file_path = "C:/Users/eshaa/Downloads/Report.pdf"  # Replace with your PDF file path
pdf_content = read_pdf(pdf_file_path)
print("Extracted Text:")
print(pdf_content)


parameters={"Haemoglobin":(12.0,15.0),"RBC":(3.8,4.8),"PCV":(36,46),"MCV":(83,101),"TLC":(4,10),"Neutrophils":(40,80),"Lymphocytes":(20,40),"Platelet Count":(150,410),"MPV":(9.3,12.1)}
a = parameters[("TLC")][0]
print(a)
