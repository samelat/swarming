
#include <module.hpp>

#include <iostream>


PyObject * connection_error::python_type = PyErr_NewException("ssh.ConnectionError", NULL, NULL);

/*
 * The idea behind using an external socket insted native libraries
 * connections is to provide the basis for the use of socks.
 */
void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<const char *>;

    unsigned int attempt = 0;
    LoginResult result;

    for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
        set_username(*usr);
        for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++) {
            attempt = 1;
            do {
                try {
                    result = login(*pwd);
                    attempt = 0;
                } catch(...) {
                    disconnect();
                    if(++attempt > attempts)
                        throw;
                }
            } while(attempt);

            if(result == SUCCESS) {
                callback(username, *pwd);
                // Continue with the next username.
                break;
            }
        }
    }

    for(bp::stl_input_iterator<bp::tuple> p(pairs); p != bp::stl_input_iterator<bp::tuple>(); p++) {
        set_username(bp::extract<const char *>((*p)[0])());
        attempt = 1;
        do {
            try {
                result = login(bp::extract<const char *>((*p)[1])());
                attempt = 0;
            } catch(...) {
                disconnect();
                if(++attempt > attempts)
                    throw;
            }
        } while(attempt);

        if(result == SUCCESS) {
            callback(username, bp::extract<const char *>((*p)[1])());
            // Continue with the next username.
            break;
        }
    }
}

/*
 *
 */
void Cracker::connect() {

    struct sockaddr_in sin;
 
    socket_fd = socket(AF_INET, SOCK_STREAM, 0);

    //fcntl(sock, F_SETFL, O_NONBLOCK);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    inet_pton(AF_INET, dst_addr, &sin.sin_addr.s_addr);
    
    while(::connect(socket_fd, reinterpret_cast<struct sockaddr*>(&sin), sizeof(struct sockaddr_in)) == EINPROGRESS)
        wait();
}

/*
 *
 */
void Cracker::wait() {

    unsigned int ticks = 1;
    int count_fds, so_error;
    socklen_t option_len = sizeof(so_error);
    
    fd_set read_set;
    struct timeval quantum;
    
    // The idea of this is to control for an interruption
    do {
        FD_ZERO(&read_set);
        FD_SET(socket_fd, &read_set);
        quantum.tv_sec  = 1;
        quantum.tv_usec = 0;

        count_fds = select(socket_fd + 1, &read_set, NULL, NULL, &quantum);
        if(count_fds)
           break;
    } while(++ticks < timeout);

    if(count_fds < 0) {

        getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &so_error, &option_len);

        std::cout << "so_error == " << so_error << " - " << strerror(so_error) << std::endl;
        std::cout << "count_fds == " << count_fds << std::endl;

        if(!count_fds)
            throw connection_error("timeout error");

        std::cout << "count_fds == " << count_fds << std::endl;
        std::cout << "errno == " << errno << std::endl;
        
        throw connection_error("wait error");
    }
}

/*
 *
 */
BOOST_PYTHON_MODULE(MODULE_NAME)
{
    bp::class_<CLASS_NAME,boost::noncopyable>(STRINGIFY(CLASS_NAME),
                                              bp::init<bp::object&,
                                              const char *, uint16_t>())
        .def("crack",
             &CLASS_NAME::crack,
             (bp::arg("usernames"), bp::arg("passwords"), bp::arg("pairs")));

    boost::python::register_exception_translator<connection_error>(&translate_exception<connection_error>);
}