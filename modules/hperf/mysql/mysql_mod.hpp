
#include <mysql/mysql.h>
#include <mysql/errmsg.h>
#include <mysql/mysqld_error.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>


class MySQL {
	private:
        
        unsigned int _timeout;
        unsigned short _port;
        std::string _hostname;
        std::string _database;
	
	public:
	
		static const int CONNECTION_ERROR = 1;
        static const int TIMEOUT_ERROR    = 2;
        
        static const int LOGIN_SUCCESSFUL = 0;
        static const int LOGIN_FAILED     = 3;
	
		MySQL(std::string hostname, unsigned short port, unsigned int timeout);
		
		int try_login(std::string username, std::string password);
};
