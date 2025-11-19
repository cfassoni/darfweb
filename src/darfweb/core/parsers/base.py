# parsers/base.py
from abc import ABC, abstractmethod
from darfweb.core.models import BrokerageStatement
import pdfplumber


class IBrokerStatementParser(ABC):
    @abstractmethod
    def get_broker_name(self) -> str:
        """Returns the parser's broker name."""
        pass

    @abstractmethod
    def parse(self, pdf: pdfplumber.PDF) -> BrokerageStatement:
        """
        Takes a loaded pdfplumber object and returns
        the structured StatementData.
        """
        pass
