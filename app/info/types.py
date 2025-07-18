from abc import ABC, abstractmethod


class InfoSection(ABC):
    @abstractmethod
    def __bytes__(self) -> bytes:
        raise NotImplementedError
