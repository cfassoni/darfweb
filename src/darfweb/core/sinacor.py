import json
import magic
import os

from io import BytesIO
from pathlib import Path
from PyPDF2 import PdfReader

from darfweb.core.exceptions import ParsingError


class SinacorService:
    """Service class for handling Sinacor statements."""

    def __init__(
        self,
        pdf_filepath: str | None = None,
        filename: str | None = None,
        filecontent: bytes | None = None,
        autodetect: bool = True,
    ):
        """Initialize the service with a file path or file content."""

        config_file = (
            Path(__file__).resolve().parent.parent / "core" / "config" / "brokers.json"
        )
        self.__load_config(config_file)

        if pdf_filepath:
            # self.filepath = os.path.abspath(full_filename)
            filename = os.path.basename(pdf_filepath)
            with open(pdf_filepath, "rb") as f:
                filecontent = f.read()
        elif filecontent is None:
            raise ValueError("Either filename or filecontent must be provided.")

        if filename is None:
            filename = "unknown.pdf"

        self.validate_file(filecontent, filename)

        if autodetect:
            self.detected = self.__autodetect()

    def validate_file(self, content: bytes, filename: str | None):
        """Validate uploaded file"""
        try:
            file_size = len(content)  # Get size before converting to DataFrame
            if not file_size:
                raise ValueError("File is empty")

            # Check MIME type
            mime_type = magic.from_buffer(content, mime=True)
            if (not filename.lower().endswith(".pdf")) or (
                mime_type != "application/pdf"
            ):
                raise ValueError("File must be a PDF document")

            pdf_stream = BytesIO(content)
            reader = PdfReader(pdf_stream)
            self.num_pages = len(reader.pages)
            self.pages = reader.pages
            self.detect = {
                "filename": filename,
                "numPages": self.num_pages,
            }
        except Exception as e:
            raise ParsingError(f"Failed to validate {filename}: {e}")

    def __load_config(self, config_file: Path) -> dict:
        """Load JSON configuration file"""

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.__config = json.loads(content)
                return self.__config

        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config file: {e}")

    def __find_models(self, broker, invoice_type):
        brokers_dict = self.__config

        # Find broker and invoice type in config using list comprehension
        broker_config = next(
            (b for b in brokers_dict["brokers"] if b["brokerAlias"] == broker), None
        )

        if not broker_config:
            raise ParsingError(f"Broker '{broker}' not found in configuration")
        invoice_config = next(
            (
                i
                for i in broker_config["invoiceTypes"]
                if i["invoiceType"] == invoice_type
            ),
            None,
        )
        if not invoice_config or "models" not in invoice_config:
            raise ParsingError(
                f"Models not found for broker '{broker}' and invoice type '{invoice_type}'"
            )
        return invoice_config["models"]

    def __find_pattern(self, pattern, text, find_all: bool = False):
        if find_all:
            return all(p in text for p in pattern)
        return any(p in text for p in pattern)

    def __autodetect(self) -> list[dict]:
        result = []
        brokers = self.__config.get("brokers", [])

        for p in range(self.num_pages):
            page = self.pages[p]
            page_extract = page.extract_text()

            # Here we search for each broker pattern
            for broker_config in brokers:
                found_broker = self.__find_pattern(
                    broker_config["searchPattern"],
                    page_extract,
                    broker_config["searchAll"],
                )
                if found_broker:
                    # Then look for invoice types
                    broker = broker_config["brokerAlias"]
                    invoices_json = broker_config["invoiceTypes"]
                    for i in range(len(invoices_json)):
                        invoice_type = invoices_json[i]["invoiceType"]
                        found_type = self.__find_pattern(
                            invoices_json[i]["searchPattern"],
                            page_extract,
                            invoices_json[i]["searchAll"],
                        )
                        if found_type:
                            models = self.__find_models(broker, invoice_type)
                            result.append(
                                {
                                    "page": p + 1,
                                    "brokerId": broker_config["brokerId"],
                                    "brokerAlias": broker,
                                    "invoiceType": invoice_type,
                                    "models": models,
                                }
                            )
                            self.is_detected = True
                            break
                    break
        if not result:
            raise ParsingError("No supported format detected in the document")
        return result
