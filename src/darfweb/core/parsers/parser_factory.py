# parser_factory.py
from .base import IBrokerStatementParser
from .xp_parser import XpParser
from .btg_parser import BtgParser
import pdfplumber

PARSERS = [XpParser(), BtgParser()]


def get_parser(pdf_path: str) -> IBrokerStatementParser:
    with pdfplumber.open(pdf_path) as pdf:
        first_page_text = pdf.pages[0].extract_text().lower()

        if "xp investimentos" in first_page_text:
            return XpParser()
        if "btg pactual" in first_page_text:
            return BtgParser()

    raise ValueError("Could not identify broker for the provided PDF.")
