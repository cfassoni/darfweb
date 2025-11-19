import pdfplumber

from darfweb.core.parsers.base import IBrokerStatementParser
from darfweb.core.models import BrokerageStatement


class BtgParser(IBrokerStatementParser):
    def get_broker_name(self) -> str:
        return "XP Investimentos"

    def parse(self, pdf: pdfplumber.PDF) -> BrokerageStatement:
        page_one_text = pdf.pages[0].extract_text()

        # --- This is the fragile, necessary logic ---

        # Logic to find customer name (e.g., text after "Cliente:")
        customer_name = self._find_text_after_anchor(page_one_text, "Cliente:")

        # Logic to find trades (using .extract_tables() is best!)
        trades_table = pdf.pages[0].extract_tables(table_settings={})
        parsed_trades = self._parse_trade_table(trades_table)

        # ... more logic ...

        return BrokerageStatement(
            broker_name=self.get_broker_name(),
            customer_name=customer_name,
            trades=parsed_trades,
            # ... etc
        )

    def _find_text_after_anchor(self, text: str, anchor: str) -> str:
        # Simple regex or string splitting logic
        pass

    def _parse_trade_table(self, table: list) -> list:
        # Logic to loop through the table rows
        pass
