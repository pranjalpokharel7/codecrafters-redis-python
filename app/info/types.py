from dataclasses import dataclass, fields

from app.resp.types.bulk_string import BulkString


@dataclass
class InfoSection:
    title: str

    def __bytes__(self) -> bytes:
        info = f"{self.title}\n"
        for field in fields(self):
            key = field.name
            value = getattr(self, key)
            info += f"{key}:{value}\n"
        return bytes(BulkString(info.encode()))
