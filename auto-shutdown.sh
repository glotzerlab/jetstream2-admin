#!/bin/bash

# clean up and shutdown when the actions runner is idle, there are no users logged in
# and the system has been up for at least an hour.
uptime=$(</proc/uptime)
uptime=${uptime%%.*}

num_users=$(who | wc -l)
num_notty_logins=$(pgrep -ai sshd | grep "@notty" | wc -l)

# Ensure that the system remains up after boot.
if (( $uptime < 1800 )); then
    echo $(date): Skipping auto-shutdown, system up for $uptime seconds.
    exit 0
fi

# Don't shut down when users are logged in.
if (( $num_users > 0 )); then
    echo $(date): Skipping auto-shutdown, $num_users users logged in.
    exit 0
fi

if (( $num_notty_logins > 0 )); then
    echo $(date): Skipping auto-shutdown, $num_notty_logins notty connections.
    exit 0
fi

runner_id=$(hostname | cut -d\- -f4)
recent_minutes=60

num_recently_modified=$(find /home/exouser/actions-runner/_diag -name "Worker*" -mmin -${recent_minutes} | wc -l)
echo $(date): $num_recently_modified files in _diag were modified in the last ${recent_minutes} minutes

if [ "$num_recently_modified" -eq "0" ]; then
    echo $(date): Cleaning up and shutting down.
    echo "... stop actions-runner service."
    cd /home/exouser/actions-runner
    ./svc.sh stop

    # clear up disk space
    echo "... delete log files."
    find /home/exouser/actions-runner/_diag/ -name "*.log" -delete
    journalctl --vacuum-size=200M

    echo "... prune docker images."
    docker system prune -a -f

    # shut down
    echo "... shut down"
    /usr/sbin/shutdown now -h
    echo ""
fi
