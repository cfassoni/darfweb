from darfweb.core.llm import ILlmParser, GeminiParser, OllamaParser


def get_parser(llm: str, **kwargs) -> ILlmParser:
    """Factory function to get the appropriate LLM parser based"""

    llm = llm.lower()
    if llm == "gemini":
        return GeminiParser(**kwargs)
    if llm == "ollama":
        return OllamaParser(**kwargs)

    raise ValueError("Could not identify broker for the provided PDF.")
