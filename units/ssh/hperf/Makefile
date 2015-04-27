CXX          = g++
FLAGS        = -std=c++0x -I/usr/include/python3.3 -I ./
CFLAGS       = -fPIC -shared
LIBS         = -lssh2 -lboost_python-py33  -L/usr/lib/x86_64-linux-gnu/ -lpython3.3m

TARGET  = ssh2.so
SOURCES = ssh2.cpp ssh2_mod.cpp

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CFLAGS) $(SOURCES) $(CFLAGS) -o $(TARGET) $(FLAGS) $(LIBS)
	mv $(TARGET) ../../
