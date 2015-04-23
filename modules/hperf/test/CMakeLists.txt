cmake_minimum_required (VERSION 2.8.11)

project (test)

#include(CheckCXX11Features)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX11_COMPILER_FLAGS}")

if(UNIX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall")
endif()

# add_executable(test test.cpp)
add_library(test SHARED test.cpp)
