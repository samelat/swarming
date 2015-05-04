
#include "ssh.hpp"

Cracker::status_t SSH::login(const char * username, const char * password) {
    std::cout << "[!] " << username << " - " << password << std::endl;
    return Cracker::status_t::FAILED;
}
 /*
Cracker::status_t SSH::login(const char * username, const char * password) {
    std::cout << "[!] " << username << " - " << password << std::endl;
    return Cracker::status_t::FAILED;
    
    int ssh_error;
    int so_error = 0;
    socklen_t len = sizeof(so_error);
    
    if(this->_sock < 0) {

        // 1 - Connection error
        if(_socket_connect()) {
            this->_sock = -1;
            return CONNECTION_ERROR;
        }
        
        // 2 - Session creation error
        // 3 - Handshake error
        if(ssh_error = _ssh2_start()) {
            _ssh2_finish();
            return ssh_error;
        }
    }
    
    while ((ssh_error = libssh2_userauth_password(session.get(), username, password)) == LIBSSH2_ERROR_EAGAIN) {
        so_error = wait_socket();
        
        if(so_error)
            return so_error;
    }
    
    if (ssh_error != LIBSSH2_ERROR_AUTHENTICATION_FAILED)
        _ssh2_finish();
    
    return ssh_error;
}*/