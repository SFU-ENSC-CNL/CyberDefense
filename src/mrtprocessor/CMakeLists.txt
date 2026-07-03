cmake_minimum_required(VERSION 3.26)
project(mrtprocessor)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_OSX_ARCHITECTURES "arm64")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer")
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-stack-check")

include_directories("$ENV{HOME}/.local/include")
include_directories("${PROJECT_SOURCE_DIR}/include")

add_executable(mrtprocessor main.cpp
        summarydata.cpp
        summarydata.h
        BS_thread_pool.hpp
        multibgpreader.cpp
        multibgpreader.h
        filters.cpp
        filters.h
        util.cpp
        util.h)
target_link_directories(mrtprocessor PUBLIC "$ENV{HOME}/.local/lib")
if (APPLE)
target_link_libraries(mrtprocessor -lbgpdump -lbz2 -lz)
else()
    target_link_libraries(mrtprocessor -lbgpdump -lbz2 -lz -lpthread)
endif()

add_subdirectory(unit_tests)
