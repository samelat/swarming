
#include <iostream>
#include <vector>

#include "ssh.hpp"

/*
 * 
 */
void SSH::connect() {
    
    std::cout << "SSH::connect()\n";

    session.reset(ssh_new());

    Cracker::connect();

    ssh_options_set(session.get(), SSH_OPTIONS_FD, &socket_fd);

    if(ssh_connect(session.get()) != SSH_OK)
        throw standard_error("ssh_connect error");

    ssh_set_blocking(session.get(), 0); //nonblocking
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
        wait();
        std::cout << "re-trying ..." << std::endl;
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