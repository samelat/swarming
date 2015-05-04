#ifndef SSH_H
#define SSH_H

#include <memory>
#include <cstdint>

#include <libssh2.h>
#include <cracker.hpp>

/*
class Test : public Cracker {
public:
    Test(bp::object& callback) : Cracker(callback) {};

    Cracker::status_t login(const char * username, const char * password) override;
};
*/

/*
    static const int CONNECTION_ERROR = 1;
    static const int TIMEOUT_ERROR    = 2;
    static const int PROTOCOL_ERROR   = 3;
    
    static const int LOGIN_SUCCESSFUL = 0;
    static const int LOGIN_FAILED     = -18;
    
    static const int RETRY_LOGIN      = -9;
 */

class SSH : Cracker {
public:

    SSH2::SSH2(object callback, uint32_t ipv4);
    ~SSH2();
    
    Cracker::status_t SSH::login(const char * username, const char * password);

private:
    std::unique_ptr<LIBSSH2_SESSION, decltype(libssh2_session_free)> session;
    
    int sock;
    unsigned int timeout;

    uint16_t dst_port;
    uint32_t dst_ipv4;

    int  wait_socket();
    int  socket_connect();
    int  ssh2_start();
    void ssh2_finish();
};

#endif