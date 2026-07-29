import io
import email
from pypdf import PdfReader
import docx
from app.core.config import get_settings

async def parse_file(file_bytes: bytes, filename: str) -> str:
    """Parse file based on extension and return text content."""
    settings = get_settings()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValueError(f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_MB} MB).")
        
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    try:
        if ext == "pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return text.strip()
        elif ext == "eml":
            msg = email.message_from_bytes(file_bytes)
            parts = []
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        parts.append(payload.decode(charset, errors='replace'))
            return "\n".join(parts).strip()
        elif ext == "txt":
            try:
                return file_bytes.decode('utf-8').strip()
            except UnicodeDecodeError:
                return file_bytes.decode('latin-1').strip()
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error parsing {ext} file: {str(e)}")
