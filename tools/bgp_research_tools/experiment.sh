#!/bin/zsh
rm sequential.txt
rm ripe_stats*.log
echo "job; user_time; system_time; percentage_cpu; elapsed_time"
TIMEFMT=$'%J; %U; %S; %P; %E'
# for thread in 256 128 64 32 16 8 4 2 1
for thread in 1
do
    eval "time python3 example_sequential_download_and_parse.py $thread"
done