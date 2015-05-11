
#include <iostream>
#include <vector>

#include "ssh.hpp"

/*
 * 
 */
Cracker::SocketState SSH::connect() {
    
    std::cout << "SSH::connect()\n";

    if(Cracker::connect() == Cracker::SocketState::ERROR)
        return Cracker::SocketState::ERROR;

    ssh_options_set(session, SSH_OPTIONS_FD, &socket_fd);

    if(ssh_connect(session) != SSH_OK)
        return Cracker::SocketState::ERROR;

    ssh_set_blocking(session, 0); //nonblocking

    return Cracker::SocketState::READY;
}

/*
 * 
 */
Cracker::SocketState SSH::disconnect() {
    
    std::cout << "disconnecting\n";

    ssh_disconnect(session);

    return Cracker::SocketState::NOSOCK;
}

/*
 *
 */
Cracker::LoginResult SSH::login(const char * username, const char * password) {
    
    bool retry = true;
    int ssh_error;

    std::cout << "[!] " << username << " - " << password << std::endl;
    
    while(retry) {
        ssh_error = ssh_userauth_password(session, username, password);

        if(ssh_error != SSH_AUTH_AGAIN)
            break;
        
        switch(wait(10)) {
            case SocketState::READY:
                std::cout << "re-trying ..." << std::endl;
                break;

            case SocketState::TIMEOUT:
                std::cout << "Timeout Error" << std::endl;
                break;

            default:
                std::cout << "Socket Error" << std::endl;
                retry = false;
                break;
        }
    }

    if(ssh_error == SSH_AUTH_SUCCESS)
        return LoginResult::SUCCESS;

    return LoginResult::FAILED;
}