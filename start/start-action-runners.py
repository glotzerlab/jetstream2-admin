# Copyright (c) 2022-2025 The Regents of the University of Michigan.
# Part of the Glotzerlab jetstream2 administration scripts, released under the
# BSD 3-Clause License.

"""Start actions runner instances in jetstream2."""

import argparse
import sys
import time

import openstack

NUM_ATTEMPTS = 8
TIME_BETWEEN_ATTEMPTS = 20


def bring_runners_online(connection, N, wait):
    """Bring N actions-runner servers online.

    When `wait` is False, assume that runners are available after requesting a start.

    Returns:
        (done, n_active): `done` is `True` when N (or all) actions-runner servers are online,
        `False` otherwise.
    """
    try:
        servers = list(connection.compute.servers())
    except Exception as e:
        print("::warning:: Failed to enumerate servers:", str(e), file=sys.stderr)
        return False

    total_runners = 0
    active_runners = 0

    servers.sort(key=lambda server: server.name)

    for server in servers:
        if server.name != "actions-runner-manager" and server.name.startswith("actions-runner"):
            if N > 0 and total_runners >= N:
                break

            total_runners += 1

            print(
                f"Server {server.name} is {server.status}({server.task_state}).",
                file=sys.stderr,
            )
            if server.status == "SHELVED_OFFLOADED" and server.task_state is None:
                print(f"... unshelving {server.name}.", file=sys.stderr)

                try:
                    connection.compute.unshelve_server(server)
                    if not wait:
                        active_runners += 1
                except Exception as e:
                    print(
                        f"::warning:: Failed to unshelve {server.name}:",
                        str(e),
                        file=sys.stderr,
                    )

            elif server.status == "SHUTOFF" and server.task_state is None:
                print(f"... starting {server.name}.", file=sys.stderr)

                try:
                    connection.compute.start_server(server)
                    if not wait:
                        active_runners += 1
                except Exception as e:
                    print(
                        f"::warning:: Failed to start server {server.name}:",
                        str(e),
                        file=sys.stderr,
                    )

            elif server.status == "ACTIVE":
                active_runners += 1

            elif server.status == "STARTING":
                active_runners += 1

    if active_runners >= total_runners:
        print(
            f"Success: {total_runners} actions-runner servers are active.",
            file=sys.stderr,
        )

    sys.stderr.flush()

    return (active_runners >= total_runners, active_runners)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start actions runner instances in jetstream2.")
    parser.add_argument(
        "N",
        type=int,
        nargs="?",
        default=-1,
        help="Number of instances to start (-1 starts all).",
    )
    parser.add_argument('--wait', action='store_true')

    args = parser.parse_args()

    # catch errors and return success so that this script doesn't stop the whole actions job
    try:
        connection = openstack.connect()
    except Exception as e:
        print("::warning:: Failed to connect to cloud:", str(e), file=sys.stderr)
        print(0)
        sys.exit(0)

    # attempt to bring the servers online several times before returning
    attempts = 0
    done, active_runners = bring_runners_online(connection, args.N, args.wait)
    while not done and attempts < NUM_ATTEMPTS:
        attempts += 1
        print(f"Waiting {TIME_BETWEEN_ATTEMPTS} seconds...", flush=True, file=sys.stderr)
        time.sleep(TIME_BETWEEN_ATTEMPTS)
        print("", flush=True, file=sys.stderr)
        done, active_runners = bring_runners_online(connection, args.N, args.wait)

    # Calling applications can redirect stdout to determine the number of active runners.
    print(active_runners)
