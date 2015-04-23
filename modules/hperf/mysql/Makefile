CXX          = g++
FLAGS        = -std=c++0x -I/usr/include/python3.2mu -I ./
CFLAGS       = -fPIC -shared -I/usr/include/mysql -DBIG_JOINS=1  -fno-strict-aliasing  -g
LIBS         = -lssh2 -lboost_python-py32  -L/usr/lib -lpython3.2mu -L/usr/lib/x86_64-linux-gnu -lmysqlclient -lpthread -lz -lm -lrt -ldl

TARGET  = mysql.so
SOURCES = mysql.cpp mysql_mod.cpp

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CFLAGS) $(SOURCES) $(CFLAGS) -o $(TARGET) $(FLAGS) $(LIBS)
	mv $(TARGET) ../../
