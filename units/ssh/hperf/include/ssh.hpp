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

    class ssh_deleter {
    public:
        void operator()(ssh_session s) {
            ssh_disconnect(s);
            ssh_free(s);
        };
    };

    SSH(bp::object& success_cb, bp::object& retry_cb, const char * daddr, const uint16_t dport)
        : Cracker(success_cb, retry_cb, daddr, dport) {};

    ~SSH(){};


private:

    std::unique_ptr<struct ssh_session_struct, ssh_deleter> session;

    void connect() override;
    void disconnect() override {session = nullptr;}
    void set_username(const char * usr) override;

    Cracker::LoginResult login(const char * password) override ;
};

#endif