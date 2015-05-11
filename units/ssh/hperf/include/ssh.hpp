#ifndef SSH_H
#define SSH_H

#include <memory>
#include <cstdint>

#include <libssh/libssh.h>

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

class SSH : public Cracker {
public:

    SSH(bp::object& callback, const char * daddr, const uint16_t dport, const unsigned int timeout=DEFAULT_TIMEOUT)
        : Cracker(callback, daddr, dport, timeout), session(ssh_new()) {};

    ~SSH(){ssh_free(session);};


private:

    ssh_session session;

    Cracker::SocketState connect() override ;
    Cracker::SocketState disconnect() override ;
    Cracker::SocketState set_username(const char * usr) override ;
    Cracker::LoginResult login(const char * password) override ;
};

#endif