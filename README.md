# jetstream2 administration scripts

Use these scripts to administer the jetstream2 VMs. They provide resources to GitHub Actions to
perform expensive build and test options more quickly.

## Using the runnings in GitHub Actions

Use the runner `[self-hosted,jetstream2,CPU]` to select these runners for GitHub Actions jobs.

The VMs shutdown automatically after a period of inactivity. Start the runners as part of the
workflow with this job:

```
    steps:
      - uses: glotzerlab/jetstream2-admin/start@v1.2.0
        with:
          OS_APPLICATION_CREDENTIAL_ID: ${{ secrets.OS_APPLICATION_CREDENTIAL_ID }}
          OS_APPLICATION_CREDENTIAL_SECRET: ${{ secrets.OS_APPLICATION_CREDENTIAL_SECRET }}
```

Optionally request only a certain number of runners. Use this when your GitHub Actions workflow
only runs a small number of jobs:
```
    steps:
      - uses: glotzerlab/jetstream2-admin/start@v1.2.0
        with:
          OS_APPLICATION_CREDENTIAL_ID: ${{ secrets.OS_APPLICATION_CREDENTIAL_ID }}
          OS_APPLICATION_CREDENTIAL_SECRET: ${{ secrets.OS_APPLICATION_CREDENTIAL_SECRET }}
          number: 1
```

## To adminster the VMs

* Create and manage VMs at: https://jetstream2.exosphere.app/exosphere/home
* Add VMs to the inventory in `hosts.yaml`.

## Configure GitHub action runners

Use ansible to install GitHub Actions on the VMs::

    ansible-playbook configure-runners.yaml -i hosts.yaml

* `configure-runners.yaml` will ask for a token from [GitHub's add runner page](https://github.com/organizations/glotzerlab/settings/actions/runners/new?arch=x64&os=linux).
* `update-instances.yaml` will update the apt packages.
* [View the active runners on GitHub](https://github.com/organizations/glotzerlab/settings/actions/runners).

## Manage action runners

* `auto-shutdown.sh` automatically shuts down instances when the actions-runner service is idle for
  some time.
* `shelve-action-runners.py` shelves actions-runner instances that are powered down.
* `start-action-runners.py` starts actions-runner instances.

HOOMD's GitHub Actions scripts run `start-action-runners.py` when needed. This repository runs
`shelve-action-runners.py` periodically in GitHub Actions to shelve the instances when not needed.
Both of these scripts may be run locally with the proper authentication token (see
https://docs.jetstream-cloud.org/ui/cli/overview/).

## Check on action runner usage

Use ansible to download usage data::

    ansible-playbook fetch-activity-logs.yaml -i hosts.yaml

Then, run the `usage-details.ipynb` notebook in Jupyter.

## Style

Use `pre-commit` to check for code style and formatting.

## License

Tihe jetstream2 administration scripts are available under the [3-clause BSD license](LICENSE).
