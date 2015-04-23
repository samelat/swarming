CXX          = g++
FLAGS        = -std=c++0x -I/usr/include/python3.2mu -I ./
CFLAGS       = -fPIC -shared
LIBS         = -lcrypto -lboost_python-py32  -L/usr/lib -lpython3.2mu

TARGET  = smb.so
SOURCES = smb.cpp smb_mod.cpp ntlm.cpp hmac_md5.cpp smb_response.cpp

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CFLAGS) $(SOURCES) $(CFLAGS) -o $(TARGET) $(FLAGS) $(LIBS)
	mv $(TARGET) ../../
