import copy
import hashlib
import os
import pdfplumber

from abc import ABC, abstractmethod
from datetime import datetime

from darfweb.core.models import BrokerageStatement, Negocio, Pagina
from .skeleton import create_skeleton


class IBrokerParser(ABC):
    def __init__(self):
        """Initialize the parser."""
        self.state = "IDLE"

        # --- DYNAMIC INITIALIZATION ---
        # 1. Create the root skeleton
        self.data = create_skeleton(BrokerageStatement)
        self._page_template = create_skeleton(Pagina)
        self._trade_template = create_skeleton(Negocio)

        self.start_new_page()

        # 2. Manually initialize the first page
        # Because lists start empty [], we need to add the first object structure
        # new_page_data = copy.deepcopy(self._page_template)
        # self.data["paginas"].append(new_page_data)

        # 3. Create pointers for easier access
        # This keeps your code clean. Instead of typing the full path, use self.nota
        # self.current_page = self.data["paginas"][0]
        # self.current_nota = self.current_page["nota"]

        # 4. Initialize the first trade and pointer to it
        # self.current_nota["negocios_realizados"].append(self._trade_template)
        # self.current_trade = self.current_nota["negocios_realizados"][0]

        # Optional: Set default values that aren't part of the extraction
        self.data["arquivo"] = "processing.pdf"

    def start_new_page(self):
        """
        Uses the cached template to create a new page
        """
        # CRITICAL: Must use deepcopy, or all pages will be identical!
        new_page_data = copy.deepcopy(self._page_template)
        self.data["paginas"].append(new_page_data)

        # Update pointers
        self.current_page = self.data["paginas"][-1]
        self.current_nota = self.current_page["nota"]

    def add_trade(self):
        """
        Uses the cached template to create a new trade
        """
        # CRITICAL: Must use deepcopy
        new_trade = copy.deepcopy(self._trade_template)

        self.current_nota["negocios_realizados"].append(new_trade)
        # return reference to this specific trade so you can fill it
        return self.current_nota["negocios_realizados"][-1]

    # def add_trade(self):
    #     """Add a new trade to the current nota."""
    #     trade_struct = create_skeleton(Negocio)
    #     self.current_nota["negocios_realizados"].append(trade_struct)

    def get_result(self):
        """Validate and result data in base model"""
        try:
            validate = BrokerageStatement.model_validate(self.data)
        except Exception as e:
            raise RuntimeError(f"Error validating data: {e}") from e
        return validate

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

        self.pages: list[str] = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    self.pages.append(page_text)
                    if page_text:
                        text += f"--- PAGE {i + 1} ---\n{page_text}\n\n"
                self.num_pages = len(pdf.pages)

            self.data["arquivo"] = filename
            self.data["data_extracao"] = extract_date
            self.data["sha1"] = sha1
            self.data["total_de_paginas"] = self.num_pages

        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {e}") from e

        return text

    @abstractmethod
    def get_broker_name(self) -> str:
        """Returns the parser's broker name."""
        pass

    @abstractmethod
    def get_parsed_data(self):
        """
        Takes a loaded pdf text and returns the structured data.
        """
        pass
