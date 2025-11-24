class SearchTool:
    def __init__(self, text: str) -> None:
        if len(text) == 0:
            raise ValueError("Text cannot be empty")

        self.text = text
        self.rows = text.splitlines()
        self.length = len(self.rows)
        self.index = 0

    def fsearch(self, text: str) -> int:
        """Search foward text"""
        row = self.index
        while row < self.length:
            if text in self.rows[row]:
                self.index = row
                return self.rows[row].index(text)
            row += 1
        return -1

    def bsearch(self, text: str) -> int:
        """Search backward text"""
        row = self.index
        while row >= 0:
            if text in self.rows[row]:
                self.index = row
                return self.rows[row].index(text)
            row -= 1
        return -1

    def next(self, inc: int = 1) -> str:
        """Next row"""
        self.index += inc
        if self.index >= self.length:
            self.index = self.length - 1
        return self.rows[self.index]

    def prev(self, dec: int = 1) -> str:
        """Previous row"""
        self.index -= dec
        if self.index < 0:
            self.index = 0
        return self.rows[self.index]

    @property
    def eof(self) -> bool:
        return self.index >= self.length - 1

    @property
    def bof(self) -> bool:
        return self.index <= 0

    @property
    def current_row(self) -> str:
        return self.rows[self.index]
