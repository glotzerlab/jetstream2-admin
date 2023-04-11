# Copyright (c) 2022-2023 The Regents of the University of Michigan.
# Part of the Glotzerlab jetstream2 administration scripts, released under the
# BSD 3-Clause License.

"""Start actions runner instances in jetstream2."""

import argparse
import openstack
import sys
import time

NUM_ATTEMPTS = 8
TIME_BETWEEN_ATTEMPTS = 20


def bring_runners_online(connection, N):
    """Bring N actions-runner servers online.

    Returns:
        True when N (or all) actions-runner servers are online, False otherwise.
    """
    try:
        servers = list(connection.compute.servers())
    except Exception as e:
        print('::warning:: Failed to enumerate servers:', str(e))
        return False

    total_runners = 0
    active_runners = 0

    servers.sort(key=lambda server: server.name)

    for server in servers:
        if server.name.startswith('actions-runner'):
            if N > 0 and total_runners >= N:
                break

            total_runners += 1

            print(
                f'Server {server.name} is {server.status}({server.task_state}).'
            )
            if (server.status == 'SHELVED_OFFLOADED'
                    and server.task_state is None):
                print(f'... unshelving {server.name}.')

                try:
                    connection.compute.unshelve_server(server)
                except Exception as e:
                    print(f'::warning:: Failed to unshelve {server.name}:',
                          str(e))

            elif server.status == 'SHUTOFF' and server.task_state is None:
                print(f'... starting {server.name}.')

                try:
                    connection.compute.start_server(server)
                except Exception as e:
                    print(f'::warning:: Failed to start server {server.name}:',
                          str(e))

            elif server.status == 'ACTIVE':
                active_runners += 1

    if total_runners == active_runners:
        print(f"Success: {total_runners} actions-runner servers are active.")

    sys.stdout.flush()

    return total_runners == active_runners


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Start actions runner instances in jetstream2.')
    parser.add_argument('N',
                        type=int,
                        nargs='?',
                        default=-1,
                        help='Number of instances to start (-1 starts all).')

    args = parser.parse_args()

    # catch errors and return success so that this script doesn't stop the whole
    # actions job
    try:
        connection = openstack.connect()
    except Exception as e:
        print('::warning:: Failed to connect to cloud:', str(e))
        sys.exit(0)

    # attempt to bring the servers online several times before returning
    attempts = 0
    while (not bring_runners_online(connection, args.N)
           and attempts < NUM_ATTEMPTS):
        attempts += 1
        print(f'Waiting {TIME_BETWEEN_ATTEMPTS} seconds...', flush=True)
        time.sleep(TIME_BETWEEN_ATTEMPTS)
        print('', flush=True)
