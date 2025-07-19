from dataclasses import dataclass, fields

from app.resp.types.bulk_string import BulkString


@dataclass
class InfoSection:
    title: str

    def __bytes__(self) -> bytes:
        info = f"{self.title}\r\n"
        for field in fields(self):
            key = field.name
            if key == "title":
                continue # do not re-encode title field
            value = getattr(self, key)
            info += f"{key}:{value}\r\n"
        return info.encode()
