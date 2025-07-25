# Module - Replica

This contains server logic related to replication.

- `pool.py` - Defines connection pool that is used by the master replica to store persistent connections and send messages to slave replicas.
- `handshake.py` - Handles the initial handshake logic (from the replica side) and parses relevant server information.
