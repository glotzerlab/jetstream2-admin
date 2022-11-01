# Copyright (c) 2022 The Regents of the University of Michigan.
# Part of the Glotzerlab jetstream2 administration scripts, released under the
# BSD 3-Clause License.

"""List actions runner instances in jetstream2."""

import openstack


def list_runners(connection):
    """List runners by their state and id.
    """
    try:
        servers = list(connection.compute.servers())
    except Exception as e:
        print('::warning:: Failed to enumerate servers:', str(e))
        return False

    servers.sort(key=lambda server: server.name)

    for server in servers:
        if server.name.startswith('actions-runner'):
            print(
                f'{server.id} is {server.status}({server.task_state}).'
            )


if __name__ == '__main__':
    connection = openstack.connect()
    list_runners(connection)
