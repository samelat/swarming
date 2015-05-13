#ifndef CRACKER_HPP
#define CRACKER_HPP

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>

#include <exception>

#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <boost/python/stl_iterator.hpp>

#define  STRINGIFY(var) _STRINGIFY(var)
#define _STRINGIFY(var) #var

#define DEFAULT_TIMEOUT  10
#define DEFAULT_ATTEMPTS 3


namespace bp = boost::python;

class Cracker {
public:

    Cracker(bp::object& callback, const char * daddr, const uint16_t dport)
        : socket_fd(-1), dst_port(dport), dst_addr(daddr)
        , callback(callback) {};

    ~Cracker() {};

    void crack(bp::list, bp::list, bp::list);

    // These methods will have to use a mutex
    void set_timeout(const unsigned int secs) {timeout = secs;};
    void set_attempts(const unsigned int num) {attempts = num;};

protected:

    enum LoginResult {
        SUCCESS,
        FAILED,
        RETRY
    };

    enum SocketState {
        READY,
        ERROR,
        TIMEOUT
    };

    class socket_error : public std::runtime_error {
    public:
        socket_error(std::string what) : std::runtime_error(what) {};
    };

    class abort_task : public std::runtime_error {
    public:
        socket_error(std::string what) : std::runtime_error(what) {};
    };

    int socket_fd;
    unsigned int timeout  = DEFAULT_TIMEOUT;
    unsigned int attempts = DEFAULT_ATTEMPTS;

    const char * username;
    const uint16_t     dst_port;
    const char *       dst_addr;
    const bp::object   callback;

    virtual LoginResult login(const char * password) = 0;
    virtual SocketState wait();
    virtual SocketState connect();
    virtual void        set_username(const char *usr) {username = usr;};

};

#endif