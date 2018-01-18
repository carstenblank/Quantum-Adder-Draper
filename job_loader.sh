#!/usr/bin/env bash
grep_query=$(ps aux | grep "job_runner.py -real" | grep -v "grep")
exists=${#grep_query}

if [[ "$exists" -gt "0" ]]; then
    echo "Job Runner process is running...";
else
    echo "Starting Job Runner...";
    screen -d -m -S job_runner bash -c "cd $HOME/PycharmProjects/quantum-adder-draper/jobs && /usr/local/bin/python3.6 job_runner.py -config=../job_config/draper.real.config &>> ../output/jobs.draper.real.log"
    screen -list
fi;
