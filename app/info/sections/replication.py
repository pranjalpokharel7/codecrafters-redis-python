import uuid
from dataclasses import dataclass, field, fields
from enum import Enum

from app.info.types import InfoSection
from app.resp.types import Array, BulkString


def replid() -> str:
    """Returns a unique replid."""
    # Using uuids since we can have more confidence in non-collision (if there
    # is a standard library or a specification to generate random replid we can
    # follow that convention).
    return (uuid.uuid4().hex + uuid.uuid4().hex)[:40]


class ReplicationRole(Enum):
    MASTER = "master"
    SLAVE = "slave"

    def __str__(self) -> str:
        return self.value


@dataclass
class InfoReplication(InfoSection):
    """
    Master/replica replication information.
    """

    role: ReplicationRole = ReplicationRole.MASTER  # role of the server
    connected_slaves: int = 0  # number of connected replicas
    master_replid: str = field(default_factory=replid)  # replication ID of the master
    master_repl_offset: int = 0  # replication offset of the master

    def __bytes__(self) -> bytes:
        # get all methods of this class, encode them as method:value
        # for eg, BulkString(b"role:master") and add them to a list
        info = "# Replication\n"
        for field in fields(self):
            key = field.name
            value = getattr(self, key)
            info += f"{key}:{value}\n"
        return bytes(BulkString(info.encode()))
    
