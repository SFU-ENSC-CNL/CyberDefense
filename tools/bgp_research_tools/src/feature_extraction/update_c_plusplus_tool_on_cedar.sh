cd ~/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/
git switch dev-2.0 -f
# git checkout c100c21 -f
git stash
git pull
#sed -i -e 's|$ENV{HOME}/.local|/opt/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt
sed -i -e 's|set(CMAKE_CXX_STANDARD 17)|set(CMAKE_CXX_STANDARD 20)|g' ./CMakeLists.txt
#cmake .
rm -fr CMakeFiles Makefile
cmake -D CMAKE_C_COMPILER=/cvmfs/soft.computecanada.ca/gentoo/2020/usr/bin/gcc-11.3.0 -D CMAKE_CXX_COMPILER=/cvmfs/soft.computecanada.ca/gentoo/2020/usr/bin/g++-11.3.0 .
make
ln -sf ~/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor ~/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor
export DYLD_LIBRARY_PATH=~/bgp_research_tools/src/feature_extraction/mrtprocessor/lib
~/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor --help
