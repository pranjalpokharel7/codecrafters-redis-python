import threading
from abc import ABC, abstractmethod

from app.info.sections.info_replication import InfoReplication, ReplicationRole
from app.info.types import InfoSection


# it is yet to be decided how this class will be constructed?
# for one, all nodes should have the same view of the information
# so it should be a part of the execution context, but it also
# must be something that can be changed on the fly (read/write)
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
        # unused for now since we aren't updating the info across threads
        self._lock = threading.Lock() 

        # init with default values for now
        self._sections = {
            "replication": info_replication or InfoReplication(),
        }

    def get_section(self, section_name: str) -> InfoSection:
        section = self._sections.get(section_name)
        if section is None:
            raise ValueError(f"Unknown section: {section_name}")
        return section

    def get_sections(self, section_names: list[str]) -> dict[str, InfoSection]:
        return {
            name: self._sections[name]
            for name in section_names
            if name in self._sections
        }

    def get_all_sections(self) -> dict[str, InfoSection]:
        return self._sections

    def server_role(self) -> ReplicationRole:
        return getattr(self._sections["replication"], "role")
