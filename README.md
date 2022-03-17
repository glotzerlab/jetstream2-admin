# jetstream2 administration scripts

Use these scripts to administer the jetstream2 VMs.

* Create and manage VMs at: https://jetstream2.exosphere.app/exosphere/home
* Add VMs to the inventory in `hosts.yaml`.

## Configure GitHub action runners

Use ansible to install GitHub Actions on the VMs::

    ansible-playbook configure-runners.yaml -i hosts.yaml

* `configure-runners.yaml` will ask for a token from [GitHub's add runner page](https://github.com/organizations/glotzerlab/settings/actions/runners/new?arch=x64&os=linux).
* [View the active runners on GitHub](https://github.com/organizations/glotzerlab/settings/actions/runners).

## Style

Use `pre-commit` to check for code style and formatting.

