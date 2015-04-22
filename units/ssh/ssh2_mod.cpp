#include <iostream>
#include <vector>

#include <ssh2_mod.hpp>

/*
 * 
 */
const int SSH2::CONNECTION_ERROR;
const int SSH2::SESSION_ERROR;
const int SSH2::HANDSHAKE_ERROR;
const int SSH2::TIMEOUT_ERROR;

const int SSH2::LOGIN_SUCCESSFUL;

const int SSH2::CONTINUE_ERROR;
const int SSH2::AUTH_ERROR;


/*
 * 
 */
SSH2::SSH2(string hostname, short port, int timeout) {
	
	/*
	 * TODO: Generate an exception in case of libssh2_init error.
	 */
	libssh2_init(0);
	
	this->_hostname = hostname;
    this->_port     = port;
    this->_timeout  = timeout;
    
    this->_sock = -1;
    this->_session = NULL;
}

SSH2::~SSH2() {
	libssh2_exit();
}

/*
 * Espera a que el socket tenga respuesta
 */
int SSH2::_wait_socket() {
	int so_error, dir, count_fds;
    socklen_t len = sizeof(so_error);
    
    fd_set fdset;
    fd_set *readfd = NULL;
    fd_set *writefd = NULL;
    struct timeval tv;

    FD_ZERO(&fdset);
    FD_SET(this->_sock, &fdset);
    tv.tv_sec = this->_timeout;
    tv.tv_usec = 0;
    
    if(this->_session) {
        dir = libssh2_session_block_directions(this->_session);
     
        if(dir & LIBSSH2_SESSION_BLOCK_INBOUND)
            readfd = &fdset;
        
        if(dir & LIBSSH2_SESSION_BLOCK_OUTBOUND)
            writefd = &fdset;
    } else
        writefd = &fdset;
    
    count_fds = select(this->_sock + 1, readfd, writefd, NULL, &tv);
    
    getsockopt(this->_sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
    
    if(!so_error) {
        if(!count_fds)
            return TIMEOUT_ERROR;
    } else
		/*
		 * TODO: Esto por ahi haya que desglosarlo en mas errores
		 * No es muy correcto, pero mas adelante se vera, si es que
		 * causa problemas
		 */
        return abs(so_error);
    
    return 0;
}

/*
 * Realizamos la conexion
 */
int SSH2::_socket_connect() {
    int sock;
	unsigned long hostaddr;
    struct sockaddr_in sin;
	
	hostaddr = inet_addr(this->_hostname.c_str());
 
    this->_sock = socket(AF_INET, SOCK_STREAM, 0);
 
	/*
     * Ponemos el socket como no-bloqueante y hacemos connect contra
     * el host destino.
     */
    fcntl(this->_sock, F_SETFL, O_NONBLOCK);
 
    sin.sin_family = AF_INET;
    sin.sin_port = htons(this->_port);
    sin.sin_addr.s_addr = hostaddr;
    
    connect(this->_sock, (struct sockaddr*)(&sin), sizeof(struct sockaddr_in));
    
    return _wait_socket();
}

/*
 * 
 */
int SSH2::_ssh2_start() {
	int ssh2_error, so_error;
    
    /* Create a session instance */ 
    this->_session = libssh2_session_init();

    if (!this->_session)
        return SESSION_ERROR;
 
    libssh2_session_set_blocking(this->_session, 0);
    
    while ((ssh2_error = libssh2_session_handshake(this->_session, this->_sock)) == LIBSSH2_ERROR_EAGAIN) {
		so_error = this->_wait_socket();
		
		if(so_error)
			return so_error;
	};
	
    if (ssh2_error)
        return HANDSHAKE_ERROR;
        
    cout << libssh2_session_banner_get(this->_session) << endl;
    
    return 0;
}

/*
 * 
 */
int SSH2::_ssh2_finish() {
	libssh2_session_disconnect(this->_session, "");
    libssh2_session_free(this->_session);

    close(this->_sock);
    
    this->_sock = -1;
    this->_session = NULL;
}

/*
 * 
 */
int SSH2::try_login(string username, string password) {
    
    int ssh_error;
	int so_error = 0;
	socklen_t len = sizeof(so_error);
	
	/*
	 * Controlamos que la session sea valida
	 * TODO: Controlar el error!!!
	 */
	if(this->_sock < 0) {

        /*
         * 1 - Connection error
         */
		if(_socket_connect()) {
			this->_sock = -1;
			return CONNECTION_ERROR;
		}
		
		/*
		 * 2 - Session creation error
		 * 3 - Handshake error
		 */
		if(ssh_error = _ssh2_start()) {
			_ssh2_finish();
			return ssh_error;
		}
	}
	
	/*
	 * 
	 */
	while ((ssh_error = libssh2_userauth_password(this->_session, username.c_str(), password.c_str())) == LIBSSH2_ERROR_EAGAIN) {
		so_error = this->_wait_socket();
		
		if(so_error)
			return so_error;
	}
	
	if (ssh_error != LIBSSH2_ERROR_AUTHENTICATION_FAILED)
		_ssh2_finish();
	
	return ssh_error;
}
