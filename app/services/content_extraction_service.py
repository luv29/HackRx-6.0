# app/services/text_extraction_service.py

import fitz
import docx
import email
import os
from typing import Optional
from docling.document_converter import DocumentConverter
import time

class TextExtractionService:

    @staticmethod
    def sanitize_text(text: str) -> str:
        return text.replace("\x00", "").strip()

    @classmethod
    def docling_extractor(cls, file_path:str) -> str:
        try:
            convertor = DocumentConverter()
            result = convertor.convert(file_path)
            return cls.sanitize_text(result.document.export_to_markdown())
        except Exception as e:
            raise RuntimeError(f"Error extracting file: {file_path} :: {e}")

    @classmethod
    def extract_from_email(cls, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                msg = email.message_from_file(f)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode(errors="ignore")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors="ignore")
                return cls.sanitize_text(body)
        except Exception as e:
            raise RuntimeError(f"Email extraction failed: {e}")

    @classmethod
    def extract_fallback(cls, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return cls.sanitize_text(f.read())
        except Exception:
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    return cls.sanitize_text(content.decode("utf-8", errors="ignore"))
            except Exception as e:
                raise RuntimeError(f"Fallback extraction failed: {e}")

    @classmethod
    def extract_markdown(cls, file_path: str, mime_type: Optional[str] = None) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf" or mime_type == "application/pdf":
                return cls.docling_extractor(file_path)
            elif ext == ".docx" or mime_type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ]:
                return cls.docling_extractor(file_path)
            elif ext in [".eml", ".msg"] or mime_type == "message/rfc822":
                return cls.extract_from_email(file_path)
            else:
                return cls.extract_fallback(file_path)
        except Exception as e:
            return f"Error extracting text: {str(e)}"

if __name__ == '__main__':
    source = 'D:\Hackathon\HackRx 6\HackRx-6.0\data\policy.pdf'
    source = 'D:\Hackathon\HackRx 6\HackRx-6.0\data\Super_Splendor_(Feb_2023).pdf'
    start_time = time.monotonic()
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(TextExtractionService.extract_markdown(source))
    end_time = time.monotonic()
    print(f'\n\n\n\n{end_time-start_time}')