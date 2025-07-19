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
    title: str = "# Replication"
    role: ReplicationRole = ReplicationRole.MASTER  # role of the server
    connected_slaves: int = 0  # number of connected replicas
    master_replid: str = field(default_factory=replid)  # replication ID of the master
    master_repl_offset: int = 0  # replication offset of the master

