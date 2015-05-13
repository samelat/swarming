
#include <iostream>
#include <vector>

#include "ssh.hpp"

/*
 * 
 */
Cracker::SocketState SSH::connect() {
    
    std::cout << "SSH::connect()\n";

    session.reset(ssh_new());

    if(Cracker::connect() == Cracker::SocketState::ERROR)
        return Cracker::SocketState::ERROR;

    ssh_options_set(session.get(), SSH_OPTIONS_FD, &socket_fd);

    if(ssh_connect(session.get()) != SSH_OK)
        return Cracker::SocketState::ERROR;

    ssh_set_blocking(session.get(), 0); //nonblocking

    return Cracker::SocketState::READY;
}

/*
 *
 */
void SSH::set_username(const char * usr) {
    Cracker::set_username(usr);
    session = nullptr;
}

/*
 *
 */
Cracker::LoginResult SSH::login(const char * password) {
    
    LoginResult result = FAILED;
    int ssh_error;

    std::cout << "[!] " << username << " - " << password << std::endl;

    if(!session)
        connect();
    
    while((ssh_error = ssh_userauth_password(session.get(), username, password)) == SSH_AUTH_AGAIN) {
        
        switch(wait()) {
            case SocketState::READY:
                std::cout << "re-trying ..." << std::endl;
                break;

            case SocketState::TIMEOUT:
                std::cout << "Timeout Error" << std::endl;
                throw cracker_abort(TIMEOUT, "timeout error");

            default:
                std::cout << "Socket Error" << std::endl;
                session = nullptr;
                return RETRY;
        }
    }

    switch(ssh_error) {
        case SSH_AUTH_SUCCESS:
            std::cout << "login success\n";
            session = nullptr;
            result = SUCCESS;
            break;

        case SSH_AUTH_DENIED:
            std::cout << "login failed\n";
            break;

        default:
            std::cout << "UKNOWN SSH Return Value :S" << std::endl;
            break;
    }

    return result;
}