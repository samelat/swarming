cmake_minimum_required (VERSION 2.8)

project(ssh)

#include(CheckCXX11Features)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX11_COMPILER_FLAGS}")

set(Python_ADDITIONAL_VERSIONS 3.4)
find_package(PythonLibs REQUIRED)

find_package(Boost COMPONENTS python-py34 REQUIRED)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake/)
find_package(LibSSH REQUIRED)

message(${PYTHON_LIBRARIES})
message(${Boost_LIBRARIES})

if(UNIX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall")
endif()

include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(${Boost_INCLUDE_DIRS})
include_directories($(LibSSH_INCLUDE_DIRS))

#add_subdirectory(modules/hperf)
include_directories(include)
include_directories(${CMAKE_SOURCE_DIR}/modules/hperf/include)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../)

#message("HPERF BASE DIR: " ${HPERF_BASE_CLASS_DIR})
#message(${HPERF_BASE_CLASS_DIR}/cracker.cpp)

add_library(hperf_ssh SHARED ssh.cpp ${CMAKE_SOURCE_DIR}/modules/hperf/cracker.cpp)

set_target_properties(hperf_ssh PROPERTIES PREFIX "")

target_link_libraries(hperf_ssh ${Boost_LIBRARIES})
target_link_libraries(hperf_ssh ${PYTHON_LIBRARIES})
target_link_libraries(hperf_ssh ${LIBSSH_LIBRARIES})
