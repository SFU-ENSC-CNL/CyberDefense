#!/bin/zsh
dst_folder=/tmp/mrt_test

mkdir -p $dst_folder

wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0000.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0005.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0010.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0015.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0020.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0025.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0030.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0035.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0040.gz
wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0045.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0050.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0055.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0100.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0105.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0110.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0115.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0120.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0125.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0130.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0135.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0140.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0145.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0150.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0155.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0200.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0205.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0210.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0215.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0220.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0225.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0230.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0235.gz
# wget -c -P $dst_folder https://data.ris.ripe.net/rrc04/2024.01/updates.20240101.0240.gz

export DYLD_LIBRARY_PATH=/opt/bgp_research_tools/src/feature_extraction/mrtprocessor/lib
./mrtprocessor/bin/mrtprocessor -T -o output513.csv -asnfilt "513" -f $dst_folder/updates*

