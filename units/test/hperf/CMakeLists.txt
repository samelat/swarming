cmake_minimum_required (VERSION 2.8)

project (test)

#include(CheckCXX11Features)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX11_COMPILER_FLAGS}")

set(Python_ADDITIONAL_VERSIONS 3.4)
find_package(PythonLibs REQUIRED)

find_package(Boost COMPONENTS python-py34 REQUIRED)

message(${PYTHON_LIBRARIES})
message(${Boost_LIBRARIES})

if(UNIX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall")
endif()

INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_DIRS})
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})

set( CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../)

# add_executable(test test.cpp)
add_library(test SHARED test.cpp)

set_target_properties(test PROPERTIES PREFIX "")

target_link_libraries(test ${Boost_LIBRARIES})