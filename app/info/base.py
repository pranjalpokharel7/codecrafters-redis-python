import threading

from app.info.sections.info_replication import InfoReplication, ReplicationRole
from app.info.types import InfoSection


class Info:
    """This class will contain logic to retrieve information and statistics
    about the server, which are classified as follows.

    server: General information about the Redis server
    clients: Client connections section
    memory: Memory consumption related information
    persistence: RDB and AOF related information
    threads: I/O threads information
    stats: General statistics
    replication: Master/replica replication information
    cpu: CPU consumption statistics
    commandstats: Redis command statistics
    latencystats: Redis command latency percentile distribution statistics
    sentinel: Redis Sentinel section (only applicable to Sentinel instances)
    cluster: Redis Cluster section
    modules: Modules section
    keyspace: Database related statistics
    errorstats: Redis error statistics
    """

    _sections: dict[str, InfoSection]

    def __init__(self, info_replication: InfoReplication | None = None) -> None:
        # required when we need to update the info
        self._lock = threading.Lock()

        # init with default values for now
        self._sections = {
            "replication": info_replication or InfoReplication(),
        }

    def get_section(self, section_name: str) -> InfoSection:
        with self._lock:
            section = self._sections.get(section_name)
            if section is None:
                raise ValueError(f"Unknown section: {section_name}")
            return section

    def get_sections(self, section_names: list[str]) -> dict[str, InfoSection]:
        with self._lock:
            return {
                name: self._sections[name]
                for name in section_names
                if name in self._sections
            }

    def get_all_sections(self) -> dict[str, InfoSection]:
        with self._lock:
            return self._sections

    def server_role(self) -> ReplicationRole:
        with self._lock:
            return getattr(self._sections["replication"], "role")

    def get_offset(self) -> int:
        with self._lock:
            return getattr(self._sections["replication"], "master_repl_offset")

    def add_to_offset(self, delta: int) -> int:
        with self._lock:
            current_offset = getattr(
                self._sections["replication"], "master_repl_offset"
            )
            updated_offset = current_offset + delta
            setattr(self._sections["replication"], "master_repl_offset", updated_offset)
            return updated_offset

    def get_value(self, section_name: str, attr_name: str):
        with self._lock:
            return getattr(self._sections[section_name], attr_name)
