import PyPDF2
import docx
import io

def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_bytes):
    doc = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def get_resume_text(uploaded_file):
    file_bytes = uploaded_file.read()
    if uploaded_file.name.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.name.endswith('.docx') or uploaded_file.name.endswith('.doc'):
        return extract_text_from_docx(file_bytes)
    return ""
