
#include <iostream>
#include <vector>

#include "ssh.hpp"

/*
 * 
 */
Cracker::SocketState SSH::connect() override {
    
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
Cracker::SocketState SSH::disconnect() override {
    
    std::cout << "disconnecting\n";

    ssh_disconnect(session);

    return Cracker::SocketState::NOSOCK;
}

void SSH::set_username(const char * usr) override {
    Cracker::set_username(usr);
    disconnect();
    connect();
}

/*
 *
 */
Cracker::LoginResult SSH::login(const char * password) override {
    
    bool retry = true;
    int ssh_error;


    std::cout << "[!] " << username << " - " << password << std::endl;
    
    while(retry) {
        ssh_error = ssh_userauth_password(session, username, password);

        if(ssh_error != SSH_AUTH_AGAIN)
            break;
        
        switch(wait()) {
            case SocketState::READY:
                std::cout << "re-trying ..." << std::endl;
                break;

            case SocketState::TIMEOUT:
                std::cout << "Timeout Error" << std::endl;
                break;

            default:
                std::cout << "Socket Error" << std::endl;
                // We should raise an exception here
                retry = false;
                break;
        }
    }

    switch(ssh_error) {
        case SSH_AUTH_SUCCESS:
            std::cout << "login success\n";
            callback(username, password);  
            //disconnect();
            //connect();
            break;

        case SSH_AUTH_ERROR:
            std::cout << "login failed\n";
            break;

        /*
         * Here we should control the number of attempts and
         * report in case where Its value were greater than the limit.
         */
        case SSH_AUTH_AGAIN:
            std::cout << "login reconnect\n";
            //disconnect();
            //connect();
            std::cout << "reconnecting..." << std::endl;
            break;
    }

    if(ssh_error == SSH_AUTH_SUCCESS)
        return LoginResult::SUCCESS;

    return LoginResult::FAILED;
}