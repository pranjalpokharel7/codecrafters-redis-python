#!/usr/bin/bash

for port in {5000..5003}; do
  gnome-terminal -- ./your_program.sh --port "$port" --replicaof "localhost 6379"
done

