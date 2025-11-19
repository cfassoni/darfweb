import ollama

from darfweb.core.llm.base import ILlmParser
from darfweb.core.models import BrokerageStatement

OLLAMA_MODELS = [
    "llama3:latest",
    "gemma3:latest",
]
OLLAMA_RULES = """
        - Output ONLY valid JSON. No markdown blocks (```json), no intro text.
        - If a field is missing or unclear, use null (or None).
        - Convert all dates to ISO 8601 (YYYY-MM-DD).
        - Convert numeric strings to numbers (e.g., "1.234,56" -> 1234.56).
        - If a number ends with " D", it means it's negative (e.g. "1.234,56 D" -> -1234.56).
        - The broker code and client code are normally found together and expressed like this: 123-4 567890-1 (where 123-4 is the broker code and 567890-1 is the client code).
        """


class OllamaParser(ILlmParser):
    """Parser for extracting brokerage statement data using Ollama LLM."""

    def __init__(
        self,
        model: str = None,
        rules: str = OLLAMA_RULES,
        host: str = "http://localhost:11434",
        timeout: int = 60,
    ):
        """Initialize the Ollama parser with model and rules."""
        super().__init__()

        try:
            self.client = ollama.Client(host=host, timeout=timeout)
        except Exception as e:
            raise e

        models = self.list_models()
        if model is None:
            model = models[0]
        else:
            if model not in models:
                raise ValueError(f"Invalid model '{model}'. Must be one of: {models}")
        self._model = model
        self.rules = rules

    def get_llm_name(self) -> str:
        """Return the name of the LLM model being used."""
        return f"Ollama model: {self._model}"

    def list_models(self) -> list[str]:
        """Returns a list of available Ollama models."""
        models_list = self.client.list()
        models = [m.model for m in models_list.models]
        return models

    def get_parsed_data(self, pdf_text: str) -> BrokerageStatement:
        """Extract structured data from PDF text using Ollama LLM."""
        prompt = f"""
        You are an expert financial data extractor specialized in Brazilian "Nota de Corretagem" (SINACOR).
        Your task is to extract data from the provided brokerage statement text and output it as strictly valid JSON.
        ### RULES
        {self.rules}
        ### INPUT TEXT
        {pdf_text}
        """
        response = self.client.chat(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            format=BrokerageStatement.model_json_schema(),
            options={"temperature": 0},
        )
        raw_json = response["message"]["content"]

        try:
            return BrokerageStatement.model_validate_json(raw_json)
        # finally:
        #     return raw_json
        except Exception as e:
            raise e
