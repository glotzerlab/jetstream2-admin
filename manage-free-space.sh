#!/bin/bash

# remove unused docker images when the system free space is low
free_space=$(stat -fc '%f * %S' / | bc)

echo $(date): Free disk space: ${free_space} bytes.

if (( $free_space < 25769803776 )); then
    echo "... delete log files."
    journalctl --vacuum-size=200M

    echo "... prune docker images."
    docker image prune -a -f
fi
