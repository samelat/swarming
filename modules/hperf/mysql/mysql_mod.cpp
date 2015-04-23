#include <iostream>
#include <vector>

#include <mysql_mod.hpp>

/*
 * 
 */
const int MySQL::CONNECTION_ERROR;
const int MySQL::TIMEOUT_ERROR;

const int MySQL::LOGIN_SUCCESSFUL;
const int MySQL::LOGIN_FAILED;


/*
 * 
 */
MySQL::MySQL(std::string hostname, unsigned short port, unsigned int timeout) {
	
	this->_hostname = hostname;
    this->_port     = port;
    this->_timeout  = timeout;
    
    this->_database = "information_schema";
}


/*
 * 
 */
int MySQL::try_login(std::string username, std::string password) {

    unsigned int err;
    MYSQL * _mysql = mysql_init(NULL);

    mysql_options(_mysql, MYSQL_OPT_CONNECT_TIMEOUT, (const char *)&this->_timeout);

    if (!mysql_real_connect(_mysql,
                            this->_hostname.c_str(),
                            username.c_str(),
                            password.c_str(),
                            this->_database.c_str(),
                            this->_port,
                            NULL,
                            0))
        
        err = mysql_errno(_mysql);
        
        switch(err) {
            case ER_BAD_DB_ERROR: // 1049
                return LOGIN_SUCCESSFUL;
            
            case CR_SERVER_LOST: // 2013
                return CONNECTION_ERROR;
            
            case ER_ACCESS_DENIED_ERROR: // 1045
                return LOGIN_FAILED;
            
            default:
                return err;
        }

    mysql_close(_mysql);
    
    return LOGIN_SUCCESSFUL;
}
