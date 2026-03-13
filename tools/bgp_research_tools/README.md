# BGP Research Tools

A toolkit to help researchers work with BGP data, providing a CLI, clients, parsers, and other tools.
The code present in this repository can be used on three different abstraction levels. 

* [SDK](./docs/sdk.md);
* [CLI](./docs/cli.md);
* Webapp

More information about using it is available depending on the desired abstraction level.

## Instaling

```bash
git clone https://github.com/luizsoliveira/bgp_research_tools
cd bgp_research_tools
apt -y install python3-pip
python3 -m pip install -r src/requirements.txt
```

## Instaling on HPC

```bash
# Downloading python code
git clone https://github.com/luizsoliveira/bgp_research_tools
cd bgp_research_tools
# Loading modules python3.11 and scipy-stack
module load python/3.11
module load scipy-stack
# Creating a virtual environment on the folder ENV
virtualenv --no-download ENV
# Activating the virtual environment created
source ENV/bin/activate
# Updating pip in the environment
python3.11 -m pip install --no-index --upgrade pip
# Installing the required python packages, 
python3.11 -m pip install -r src/requirements.txt --no-index
# The --no-index option tells pip to not install from PyPI, but instead to install only from locally available packages, i.e. CEDAR wheels.
```

## Instaling MRTprocessor on HPC (for feature extraction)
```bash
mkdir ~/bgp_research_tools/src/feature_extraction/mrtprocessor
cd ~/bgp_research_tools/src/feature_extraction/mrtprocessor
git clone https://github.com/RIPE-NCC/bgpdump tmp_bgpdump
cd tmp_bgpdump
# In case of Niagara:
# module load autotools
# module load gcc/13.2.0
# module load cmake
autoheader
autoconf
./configure --prefix ~/bgp_research_tools/src/feature_extraction/mrtprocessor
make
make install
cd ..
rm -fr tmp_bgpdump
ls -l
git clone https://github.com/zhida-li/CyberDefense repo
cd repo
git checkout dev-2.0
cd src/mrtprocessor/
#Edit file CMakeLists.txt
sed -i -e 's|$ENV{HOME}/.local|~/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt
sed -i -e 's|set(CMAKE_CXX_STANDARD 17)|set(CMAKE_CXX_STANDARD 20)|g' ./CMakeLists.txt
rm -fr CMakeFiles Makefile
cmake .
make
ln -sf ~/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor ~/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor

```

## Useful information about BGP anomaly events

### Slammer
* Beginning of the event: 25.01.2003 at 5:31 GMT
* End of the event: 25.01.2003 at 19:59 GMT

### Nimda
* Beginning of the event: 18.09.2001 at 13:19 GMT 
* End of the event: 20.09.2001 at 23:59 GMT 

### Code Red I
* Beginning of the event: 19.07.2001 at 13:20 GMT
* End of the event: 19.07.2001 at 23:19 GMT

### Moscow Blackout:
* Beginning of the event: 25.05.2005 at 04:00 GMT
* End of the event: 25.05.2005 at 07:59 GMT

### Pakistan Power Outage:
* Beginning of the event: 09.01.2005 at 18:40 GMT
* End of the event: 09.01.2005 at 23:59 GMT

### WannaCrypt Ransomware Attack

* Beginning of the event: 
* End of the event: 

### WestRock Ransomware Attack
* Beginning of the event: 23.01.2021 at 1:12 GMT
* End of the event: 29.01 2021 at 23:59 GMT
