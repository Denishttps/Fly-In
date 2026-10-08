

class ParseError(Exception):
    def __init__(self, line_no: int, msg: str) -> None:
        self.line_no = line_no
        self.msg = msg
        if line_no > 0:
            super().__init__(f"Error at line {line_no}: {msg}")
        else:
            super().__init__(f"Error: {msg}")


class NoPlanFoundError(RuntimeError):
    pass


class MapNotFound(Exception):
    pass
