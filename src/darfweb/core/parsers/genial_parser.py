import json
import re

from enum import Enum, auto
from typing import Any

from darfweb.core.parsers.base import IBrokerParser
from darfweb.core.models import BrokerageStatement
from .search import SearchTool


class ParserState(Enum):
    IDLE = auto()  # Looking for the start of a block
    READING_BLOCK = auto()  # Inside a block, extracting data


class GenialParser(IBrokerParser):
    def __init__(self, **kwargs: Any):
        """Initialize the Genial broker parser."""
        super().__init__()

    def get_broker_name(self) -> str:
        return "Genial"

    def get_parsed_data(self):
        """
        Takes a loaded pdf text and returns the structured data.
        """
        for i, page_text in enumerate(self.pages):
            if i >= len(self.data["paginas"]):
                super().start_new_page()

            self.current_page = self.data["paginas"][i]
            self.current_nota = self.current_page["nota"]

            st = SearchTool(page_text)

            self.current_page["pagina"] = i + 1
            self.current_page["tipo"] = (
                "BOVESPA"  # TODO: esse tipo tem q vir de algum lugar
            )

            # Search 'Nr.Nota Folha Data pregão'
            st.fsearch("Nr.Nota")
            st.next()
            var = st.current_row.split()
            current_nota = int(var[0])
            self.current_nota["nr_nota"] = current_nota
            self.current_nota["folha"] = int(var[1])
            self.current_nota["data_pregao"] = "-".join(var[2].split("/")[::-1])

            # TODO: it's unnecessary retrieve broker and customer for every page
            # Searching for broker info
            st.next()
            self.current_nota["corretora"]["nome_social"] = st.current_row.strip()
            st.next(4)
            var = st.current_row.split()
            self.current_nota["corretora"]["cnpj"] = var[1]

            # Searching for customer info
            st.fsearch("Cliente")
            st.next()
            pattern = r"(\S+)\s+(.+)\s+(\S+)"
            var = self._find_pattern(pattern, st.current_row)
            if var:
                self.current_nota["cliente"]["codigo_cliente"] = var[0]
                self.current_nota["cliente"]["nome"] = var[1]
                self.current_nota["cliente"]["cpf_cnpj"] = var[2]
            st.next(2)
            pattern = r"([\d.-]+)\s+([\d.-]+)(?:\s+(\d+))?$"
            var = self._find_pattern(pattern, st.current_row)
            if var:
                self.current_nota["corretora"]["codigo"] = var[0]
                self.current_nota["cliente"]["assessor"] = var[
                    2
                ]  # assessor may be emppty

            # Search for Trades
            st.fsearch("Negócios realizados")
            st.next(2)
            pattern = r"^.*?[CV]\s+(?!LISTADO)(?:\S+)\s+(.+?)\s+(?:#\S+\s+)?(\d+)\s+([\d,]+)\s+([\d.,]+)\s+([CD])$"
            while "Resumo" not in st.current_row:
                var = self._find_pattern(pattern, st.current_row)
                if var:
                    current_trade = super().add_trade()
                    current_trade["especificacao_do_titulo"] = var[0]
                    current_trade["quantidade"] = int(var[1])
                    current_trade["preco_ajuste"] = self._float_br(var[2])
                    current_trade["valor_operacao_ajuste"] = self._float_br(var[3])
                    current_trade["dc"] = var[4]
                    current_trade["cv"] = "C" if var[4] == "D" else "V"
                    current_trade["tipo_mercado"] = "VISTA"
                    current_trade["negociacao"] = "BOVESPA"
                    st.next()
                    if st.eof:  # an EOF here means something went wrong
                        raise Exception(
                            f"Cannot retrieve trades on brokerage note '{current_nota}'"
                        )

            # continuing with financial summary
            st.next()
            var = st.current_row.split()
            self.current_nota["resumo_dos_negocios"]["debentures"] = self._float_br(
                var[1]
            )
            st.next()
            pattern = r"^(.+?)\s+([\d.,]+)\s+(.+?)\s+([\d.,]+)\s+([CD])$"
            var = self._find_pattern(pattern, st.current_row)
            self.current_nota["resumo_dos_negocios"]["vendas_a_vista"] = self._float_br(
                var[1]
            )
            self.current_nota["resumo_financeiro"]["clearing"][
                "valor_liquido_das_operacoes"
            ] = self._float_br(var[3], var[4])

    def _find_pattern(self, pattern: str, text: str) -> list[str]:
        match = re.search(pattern, text)
        if match:
            return list(match.groups())
        return [""]

    # Helper function to convert Brazilian currency strings to floats
    def _float_br(self, value_str: str, signal: str = "C") -> float:
        """Convert Brazilian currency string to float with optional debit/credit signal."""
        # 1. Remove thousands separator (.)
        # 2. Replace decimal separator (,) with (.)
        cleaned = value_str.replace(".", "").replace(",", ".")
        result = float(cleaned) * (-1 if signal == "D" else 1)
        return result
