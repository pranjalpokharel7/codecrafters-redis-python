import inspect
import logging
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

    _name_to_section_map: dict[str, InfoSection]

    def __init__(self, info_replication: InfoReplication | None = None) -> None:
        # required when we need to update the info
        self._lock = threading.RLock()
        self.replication = info_replication or InfoReplication()
        self._name_to_section_map = {
            name: attr
            for name, attr in inspect.getmembers(self)
            if isinstance(attr, InfoSection)
        }

    def _get_section_by_name(self, section_name: str) -> InfoSection:
        """Get an information section by name.

        Returns None if no such section exists.
        """
        try:
            return self._name_to_section_map[section_name]
        except KeyError:
            raise ValueError(f"unknown section: {section_name}")

    # the design choice to serialize to bytes here is made to
    # not allow users to modify the section through get methods
    # of course they can access attributes directly,
    # but the get methods hide the implementation well
    def get_sections_by_names(self, section_names: list[str]) -> dict[str, bytes]:
        """Gets a dict of section names and serialized sections based on the
        list of names to filter from."""
        with self._lock:
            return {
                name: bytes(self._get_section_by_name(name))
                for name in section_names
                if name in self._name_to_section_map
            }

    def get_all_sections(self) -> dict[str, bytes]:
        """Returns all information sections serialized as bytes."""
        with self._lock:
            return {
                name: bytes(section)
                for name, section in self._name_to_section_map.items()
            }

    def server_role(self) -> ReplicationRole:
        """Returns whether the server is running as master or slave replica
        (replication)."""
        with self._lock:
            return self.replication.role

    def add_to_connected_replica_count(self, delta: int):
        """Add to current connected replica count (replication)."""
        with self._lock:
            new_value = max(0, self.replication.connected_slaves + delta)
            self.replication.connected_slaves = new_value

    def get_offset(self) -> int:
        """Get current offset (replication)."""
        with self._lock:
            return self.replication.master_repl_offset

    def add_to_offset(self, delta: int) -> int:
        """Add to current offset (replication)."""
        with self._lock:
            updated_offset = self.replication.master_repl_offset + delta
            logging.info(f"updating offset to {updated_offset}")

            self.replication.master_repl_offset = updated_offset
            return updated_offset
