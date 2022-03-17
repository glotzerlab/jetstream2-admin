"""Shelve powered down actions runner instances in jetstream2."""

import openstack
import sys


def shelve_runners(connection):
    """Shelve runners that are powered down."""
    try:
        servers = list(connection.compute.servers())
    except Exception as e:
        print('::warning:: Failed to enumerate servers:', str(e))
        return False

    for server in servers:
        if server.name.startswith('actions-runner'):

            print(
                f'Server {server.name} is {server.status}({server.task_state}).'
            )
            if server.status == 'SHUTOFF' and server.task_state is None:
                print(f'... shelving {server.name}.')

                try:
                    connection.compute.shelve_server(server)
                except Exception as e:
                    print(f'::warning:: Failed to shelve server {server.name}:',
                          str(e))

    sys.stdout.flush()


if __name__ == '__main__':
    # catch errors and return success so that this script doesn't stop the whole
    # actions job
    try:
        connection = openstack.connect()
    except Exception as e:
        print('::warning:: Failed to connect to cloud:', str(e))
        sys.exit(0)

    shelve_runners(connection)
