#!/usr/bin/env bash
grep_query=$(ps aux | grep "draper_benchmark.py -real" | grep -v "grep")
exists=${#grep_query}

if [[ "$exists" -gt "0" ]]; then
    echo "Draper Benchmark process is running...";
else
    echo "Starting Draper Benchmark test...";
    screen -d -m -S draper_benchmark bash -c "cd $HOME/PycharmProjects/quantum-adder-draper/jobs && python3.6 draper_benchmark.py -real &>> ../output/draper.log"
    screen -list
fi;
