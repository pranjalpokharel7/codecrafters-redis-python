from typing import Iterator


def cr_parse(buf) -> Iterator[tuple[bytes, int]]:
    """
    Generator that returns all bytes until a carriage return is found.
    Additionally returns the index to the next character to parse 
    (can be more than the buffer length).
    """
    pos = 0
    while pos < len(buf):
        # find the index of the first \r byte which is follwed by an \n byte
        end = buf.find(b"\r\n", pos)

        # return if no carriage return found
        if end == -1:
            break

        yield buf[pos:end], end + 2
        pos = end + 2 # advance position to the start of next element

