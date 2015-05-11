#ifndef CRACKER_HPP
#define CRACKER_HPP

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/stl_iterator.hpp>

#define  STRINGIFY(var) _STRINGIFY(var)
#define _STRINGIFY(var) #var

#define DEFAULT_TIMEOUT 10


namespace bp = boost::python;

class Cracker {
public:

    Cracker(bp::object& callback, const char * daddr, const uint16_t dport, const unsigned int timeout=DEFAULT_TIMEOUT)
        : socket_fd(-1), dst_port(dport), dst_addr(daddr)
        , timeout_limit(timeout), callback(callback) {};

    ~Cracker() {};

    void crack(bp::list, bp::list, bp::list);

protected:

    enum LoginResult {
        SUCCESS,
        FAILED,
        RECONNECT,
    };

    enum SocketState {
        READY,
        ERROR,
        TIMEOUT,
        NOSOCK
    };

    virtual LoginResult login(const char * username, const char * password) = 0;
    virtual SocketState wait(const unsigned int secs);
    virtual SocketState connect();
    virtual SocketState disconnect();

    int socket_fd;
    uint16_t     dst_port;
    const char * dst_addr;
    unsigned int timeout_limit;

private:
    const bp::object callback;
};

#endif