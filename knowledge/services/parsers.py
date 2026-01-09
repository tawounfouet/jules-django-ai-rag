import os
import pypdf
from docx import Document
from io import BytesIO

class DocumentParser:
    """
    Service to extract text from physical files.
    """

    @staticmethod
    def extract_text(file_path_or_buffer, file_type: str) -> str:
        """
        Extracts text based on file type.
        """
        if file_type == 'PDF':
            return DocumentParser._parse_pdf(file_path_or_buffer)
        elif file_type == 'DOCX':
            return DocumentParser._parse_docx(file_path_or_buffer)
        elif file_type == 'TEXT' or file_type == 'HTML':
            # Basic text reading, assuming utf-8
            if isinstance(file_path_or_buffer, str):
                with open(file_path_or_buffer, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return file_path_or_buffer.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _parse_pdf(file_path_or_buffer) -> str:
        try:
            reader = pypdf.PdfReader(file_path_or_buffer)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

    @staticmethod
    def _parse_docx(file_path_or_buffer) -> str:
        try:
            doc = Document(file_path_or_buffer)
            text = [para.text for para in doc.paragraphs]
            return "\n".join(text)
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
