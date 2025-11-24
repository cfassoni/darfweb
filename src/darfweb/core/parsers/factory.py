from typing import Any

from darfweb.core.parsers import IBrokerParser, GenialParser


def get_parser(broker: str, **kwargs: Any) -> IBrokerParser:
    """Factory function to get the appropriate broker parser based"""

    if broker.lower() == "genial":
        return GenialParser(**kwargs)

    raise ValueError("Could not identify broker for the provided PDF.")
