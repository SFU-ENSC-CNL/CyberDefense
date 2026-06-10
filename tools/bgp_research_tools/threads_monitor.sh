#/bin/bash
htop -p `{ python3 example_sequential_download_and_parse.py 128 > slammer_128.txt & } && echo $!`