# Module - Connection

This module enapsulates logic about handling connections for the Redis server.

## Client

The `client.py` contains logic to handle client connections. Each client request is spawned and handled in a separate thread.

## Replica

The `replica.py` contains logic related to a replica server connecting to another master server. This handles the initial logic on the replica side and spawns a thread listening for incoming bytes from the master server.

## Common

This contains logic common to responding to actual client requests, which includes,
1. Listening to incoming data,
2. Parsing and executing commands,
3. Responding with the results of command execution.
