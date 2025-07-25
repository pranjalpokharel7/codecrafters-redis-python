class ReplicationError(Exception):
    pass


class HandshakeFailed(ReplicationError):
    def __init__(self, err: str) -> None:
        super().__init__(f"failed handshake with master replica: {err}")
