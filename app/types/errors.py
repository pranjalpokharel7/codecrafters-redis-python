class ParsingError(Exception):
    pass


class InvalidStartingByte(ParsingError):
    def __init__(self, byte: int):
        super().__init__(
            f"invalid starting byte: {byte} - couldn't map to any internal type"
        )


class EmptyBuffer(ParsingError):
    def __init__(self):
        super().__init__("tried to parse empty buffer")

