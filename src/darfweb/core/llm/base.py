import hashlib
import os
import pdfplumber
from abc import ABC, abstractmethod
from datetime import datetime

from darfweb.core.models import BrokerageStatement


class ILlmParser(ABC):
    """Interface for LLM parsers."""

    @abstractmethod
    def get_llm_name(self) -> str:
        """Returns the LLM's name."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """Returns a list of available models."""
        pass

    @abstractmethod
    def get_parsed_data(self, pdf_text: str) -> BrokerageStatement:
        """
        Takes a loaded pdfplumber object and returns
        the structured StatementData.
        """
        pass

    def __get_pdf_sha1(self, pdf_path: str) -> str:
        """
        Calculates the SHA-1 hash of the PDF file.
        """
        sha1 = hashlib.sha1()
        with open(pdf_path, "rb") as f:
            while True:
                data = f.read(65536)  # Read in 64KB chunks
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from the PDF located at pdf_path.
        """
        filename = os.path.basename(pdf_path)
        extract_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sha1 = self.__get_pdf_sha1(pdf_path)

        text = f"--- FILE: {filename}\n--- EXTRACTED AT: {extract_date}\n--- SHA1: {sha1}\n\n"
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- PAGE {i + 1} ---\n{page_text}\n\n"
        return text
