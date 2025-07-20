class ReplicationError(Exception):
    pass

class HandshakeFailed(ReplicationError):
    def __init__(self, *args: object) -> None:
        super().__init__("failed handshake with master replica")


