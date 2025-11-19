import os
from google import genai
from google.genai import types

from darfweb.core.llm.base import ILlmParser
from darfweb.core.models import BrokerageStatement

GEMINI_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-pro",
]
GEMINI_RULES = """
        - Output ONLY valid JSON. No markdown blocks (```json), no intro text.
        - If a field is missing or unclear, use null (or None).
        - Convert all dates to ISO 8601 (YYYY-MM-DD).
        - Convert numeric strings to numbers (e.g., "1.234,56" -> 1234.56).
        - If a number ends with " D", it means it's negative (e.g. "1.234,56 D" -> -1234.56).
        - The broker code and client code are normally found together and expressed like this: 123-4 567890-1 (where 123-4 is the broker code and 567890-1 is the client code).
        """


class GeminiParser(ILlmParser):
    """Parser for extracting brokerage statement data using Google Gemini LLM."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "gemini-2.5-flash",
        rules: str = GEMINI_RULES,
    ):
        """Initialize the Gemini parser with API key, model, and rules."""
        super().__init__()

        if model not in GEMINI_MODELS:
            raise ValueError(
                f"Invalid model '{model}'. Must be one of: {GEMINI_MODELS}"
            )
        self._model = model

        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        self.client = genai.Client(api_key=api_key)

        self.rules = rules

    def get_llm_name(self) -> str:
        """Return the name of the LLM model being used."""
        return f"Google Gemini model: {self._model}"

    def list_models(self) -> list[str]:
        """Returns a list of available Gemini models."""
        return GEMINI_MODELS

    def get_parsed_data(self, pdf_text: str) -> BrokerageStatement:
        """Extract structured data from PDF text using Gemini LLM."""
        instruction = 'You are an expert financial data extractor specialized in Brazilian "Nota de Corretagem" (SINACOR).'
        prompt = f"""    
        Your task is to extract data from the provided brokerage statement text and output it as strictly valid JSON.
        
        ### RULES
        {self.rules}

        ### INPUT TEXT
        {pdf_text}
        """
        response = self.client.models.generate_content(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                response_mime_type="application/json",
                response_json_schema=BrokerageStatement.model_json_schema(),
            ),
            contents=prompt,
        )
        try:
            return BrokerageStatement.model_validate_json(response.text)
        except Exception as e:
            raise e
