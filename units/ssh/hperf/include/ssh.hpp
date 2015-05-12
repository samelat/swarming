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
extern "C" {
typedef struct ssh_session_struct ssh_session_t;
}
/*
void disconnect(ssh_session_t *) {


}*/

class SSH : public Cracker {
public:

    SSH(bp::object& callback, const char * daddr, const uint16_t dport, const unsigned int timeout=DEFAULT_TIMEOUT)
        : Cracker(callback, daddr, dport, timeout), session(nullptr) {};

    ~SSH(){};


private:

    //std::unique_ptr<ssh_session_t, void (*)(ssh_session_t *)> session;
    ssh_session session;

    //void disconnect(ssh_session_t *);

    void set_username(const char * usr) override ;
    Cracker::SocketState connect() override ;
    Cracker::LoginResult login(const char * password) override ;
};

#endif