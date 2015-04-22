SHELL = /bin/sh
CC    = g++
FLAGS        = -std=c++0x -I /usr/include/python2.7/ -I ./
CFLAGS       = -fPIC -shared
LIBS         = -lssh2 -lboost_python

TARGET  = ssh2.so
SOURCES = ssh2.cpp ssh2_mod.cpp

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(SOURCES) $(CFLAGS) -o $(TARGET) $(FLAGS) $(LIBS)
	mv ssh2.so ../

clean:
	rm *.so
