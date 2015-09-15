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

#include <exceptions.hpp>

#define  STRINGIFY(var) _STRINGIFY(var)
#define _STRINGIFY(var) #var

#define DEFAULT_TIMEOUT  10
#define DEFAULT_ATTEMPTS 3


namespace bp = boost::python;

class Cracker {
public:

    Cracker(bp::object& success_cb, bp::object& retry_cb, const char * daddr, const uint16_t dport)
        : socket_fd(-1), dst_port(dport), dst_addr(daddr)
        , retry_callback(retry_cb), success_callback(success_cb) {};

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

    int socket_fd;
    unsigned int timeout  = DEFAULT_TIMEOUT;
    unsigned int attempts = DEFAULT_ATTEMPTS;

    const char *     username;
    const uint16_t   dst_port;
    const char *     dst_addr;

    const bp::object retry_callback;
    const bp::object success_callback;

    virtual void wait();
    virtual void connect();
    virtual void disconnect() {close(socket_fd);}
    virtual void set_username(const char *usr) {username = usr;}

    virtual LoginResult login(const char * password) = 0;

private:
    bool login_wrapper(const char * password);
};

#endif