# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/samelat/code/swarming

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/samelat/code/swarming

# Include any dependencies generated for this target.
include units/test/hperf/CMakeFiles/test.dir/depend.make

# Include the progress variables for this target.
include units/test/hperf/CMakeFiles/test.dir/progress.make

# Include the compile flags for this target's objects.
include units/test/hperf/CMakeFiles/test.dir/flags.make

units/test/hperf/CMakeFiles/test.dir/test.cpp.o: units/test/hperf/CMakeFiles/test.dir/flags.make
units/test/hperf/CMakeFiles/test.dir/test.cpp.o: units/test/hperf/test.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /home/samelat/code/swarming/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object units/test/hperf/CMakeFiles/test.dir/test.cpp.o"
	cd /home/samelat/code/swarming/units/test/hperf && /usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/test.dir/test.cpp.o -c /home/samelat/code/swarming/units/test/hperf/test.cpp

units/test/hperf/CMakeFiles/test.dir/test.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/test.dir/test.cpp.i"
	cd /home/samelat/code/swarming/units/test/hperf && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/samelat/code/swarming/units/test/hperf/test.cpp > CMakeFiles/test.dir/test.cpp.i

units/test/hperf/CMakeFiles/test.dir/test.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/test.dir/test.cpp.s"
	cd /home/samelat/code/swarming/units/test/hperf && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/samelat/code/swarming/units/test/hperf/test.cpp -o CMakeFiles/test.dir/test.cpp.s

units/test/hperf/CMakeFiles/test.dir/test.cpp.o.requires:
.PHONY : units/test/hperf/CMakeFiles/test.dir/test.cpp.o.requires

units/test/hperf/CMakeFiles/test.dir/test.cpp.o.provides: units/test/hperf/CMakeFiles/test.dir/test.cpp.o.requires
	$(MAKE) -f units/test/hperf/CMakeFiles/test.dir/build.make units/test/hperf/CMakeFiles/test.dir/test.cpp.o.provides.build
.PHONY : units/test/hperf/CMakeFiles/test.dir/test.cpp.o.provides

units/test/hperf/CMakeFiles/test.dir/test.cpp.o.provides.build: units/test/hperf/CMakeFiles/test.dir/test.cpp.o

# Object files for target test
test_OBJECTS = \
"CMakeFiles/test.dir/test.cpp.o"

# External object files for target test
test_EXTERNAL_OBJECTS =

units/test/test.so: units/test/hperf/CMakeFiles/test.dir/test.cpp.o
units/test/test.so: units/test/hperf/CMakeFiles/test.dir/build.make
units/test/test.so: /usr/lib/x86_64-linux-gnu/libboost_python-py34.so
units/test/test.so: units/test/hperf/CMakeFiles/test.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX shared library ../test.so"
	cd /home/samelat/code/swarming/units/test/hperf && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/test.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
units/test/hperf/CMakeFiles/test.dir/build: units/test/test.so
.PHONY : units/test/hperf/CMakeFiles/test.dir/build

units/test/hperf/CMakeFiles/test.dir/requires: units/test/hperf/CMakeFiles/test.dir/test.cpp.o.requires
.PHONY : units/test/hperf/CMakeFiles/test.dir/requires

units/test/hperf/CMakeFiles/test.dir/clean:
	cd /home/samelat/code/swarming/units/test/hperf && $(CMAKE_COMMAND) -P CMakeFiles/test.dir/cmake_clean.cmake
.PHONY : units/test/hperf/CMakeFiles/test.dir/clean

units/test/hperf/CMakeFiles/test.dir/depend:
	cd /home/samelat/code/swarming && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/samelat/code/swarming /home/samelat/code/swarming/units/test/hperf /home/samelat/code/swarming /home/samelat/code/swarming/units/test/hperf /home/samelat/code/swarming/units/test/hperf/CMakeFiles/test.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : units/test/hperf/CMakeFiles/test.dir/depend

