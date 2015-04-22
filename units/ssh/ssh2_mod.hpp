
#include <libssh2.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>


using namespace std;



class SSH2 {
	
    private:
        LIBSSH2_SESSION * _session;
        
        int _sock;
        unsigned int _timeout;
        short _port;
        string _hostname;
    
    public:
    
		static const int CONNECTION_ERROR = 1;
        static const int SESSION_ERROR    = 2;
        static const int HANDSHAKE_ERROR  = 3;
        static const int TIMEOUT_ERROR    = 4;
        
        static const int LOGIN_SUCCESSFUL = 0;
        
        static const int CONTINUE_ERROR   = -9;
        static const int AUTH_ERROR       = -18;
    
		int _wait_socket();
        int _socket_connect();
        int _ssh2_start();
        int _ssh2_finish();
    
        SSH2(string hostname, short port, int timeout);
        ~SSH2();
        
        int try_login(string username, string password);
};

