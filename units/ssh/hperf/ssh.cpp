
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>

#include <iostream>
#include <vector>

#include "ssh.hpp"

/*
 * 
 */
SSH::SSH(bp::object callback/*, uint32_t ipv4*/)
    : Cracker(callback)
    , sock(-1), timeout(0), dst_port(22)
    , dst_ipv4(0) {

}


int SSH::wait_socket() {
    /*
    int so_error, dir, count_fds;
    socklen_t len = sizeof(so_error);
    
    fd_set fdset;
    fd_set *readfd = NULL;
    fd_set *writefd = NULL;
    struct timeval tv;

    FD_ZERO(&fdset);
    FD_SET(sock, &fdset);
    tv.tv_sec = timeout;
    tv.tv_usec = 0;
    
    if(this->_session) {
        dir = libssh2_session_block_directions(session);
     
        if(dir & LIBSSH2_SESSION_BLOCK_INBOUND)
            readfd = &fdset;
        
        if(dir & LIBSSH2_SESSION_BLOCK_OUTBOUND)
            writefd = &fdset;
    } else
        writefd = &fdset;
    
    count_fds = select(sock + 1, readfd, writefd, NULL, &tv);
    
    getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
    
    if(!so_error) {
        if(!count_fds)
            return TIMEOUT_ERROR;
    } else
        
        return abs(so_error);
    */
    return 0;
}


int SSH::socket_connect() {
    /*
    struct sockaddr_in sin;
 
    sock = socket(AF_INET, SOCK_STREAM, 0);
 
    fcntl(this->_sock, F_SETFL, O_NONBLOCK);
 
    sin.sin_family = AF_INET;
    sin.sin_port = htons(dsp_port);
    sin.sin_addr.s_addr = (struct in_addr)dst_ipv4;
    
    connect(this->_sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in));
    
    */
    return wait_socket();
}

/*
 * 
 */
int SSH::ssh2_start() {
    /*
    int ssh2_error, so_error;
    
    //this->_session = libssh2_session_init();
    session = std::unique_ptr<LIBSSH2_SESSION, decltype(libssh2_session_free)>(libssh2_session_init(), libssh2_session_free);

    if (!session)
        return PROTOCOL_ERROR;
 
    libssh2_session_set_blocking(session.get(), 0);
    
    while ((ssh2_error = libssh2_session_handshake(session.get(), this->_sock)) == LIBSSH2_ERROR_EAGAIN) {
        so_error = wait_socket();
        
        if(so_error)
            return so_error;
    };
    
    if (ssh2_error)
        return PROTOCOL_ERROR;
    */
    return 0;
}

/*
 * 
 */
void SSH::ssh2_finish() {
    /*
    libssh2_session_disconnect(session.get(), "");
    session = nullptr;

    close(sock);*/
}
