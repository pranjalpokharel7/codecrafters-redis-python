import threading
from typing import Any

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
        """Get an information section by name.

        Raises a ValueError if no section by the name exists.
        """
        with self._lock:
            section = self._sections.get(section_name)
            if section is None:
                raise ValueError(f"Unknown section: {section_name}")
            return section

    def get_sections(self, section_names: list[str]) -> dict[str, InfoSection]:
        """Gets a dict of section names and section based on the list of names
        to filter from."""
        with self._lock:
            return {
                name: self._sections[name]
                for name in section_names
                if name in self._sections
            }

    def get_all_sections(self) -> dict[str, InfoSection]:
        """
        Returns all information sections.
        """
        with self._lock:
            return self._sections

    def get_value(self, section_name: str, attr_name: str):
        # should we make this section agnostic? 
        # using section names make this a bit more difficult to use api
        with self._lock:
            if section := self._sections.get(section_name):
                return getattr(section, attr_name)

    def update_value(self, section_name: str, attr_name: str, value: Any):
        with self._lock:
            if section := self._sections.get(section_name):
                return setattr(section, attr_name, value)

    # utility methods relevant to replication info
    # it is advised to use general methods above as the ones below
    # are for smoother experience with frequently required info
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
