from pypdf import PdfReader
import docx2txt

def extract_text_from_file(path: str) -> str:
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        return " ".join(page.extract_text() or "" for page in reader.pages)

    if path.endswith(".docx"):
        return docx2txt.process(path)

    raise ValueError("Unsupported file format")
