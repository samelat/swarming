
#include <module.hpp>

#include <iostream>


/*
 * The idea behind using an external socket insted native libraries
 * connections is to provide the basis for the use of socks.
 */
void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<const char *>;

    for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
        set_username(*usr);
        for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++) {
            if(login_wrapper(*pwd))
                break;
        }
    }

    for(bp::stl_input_iterator<bp::tuple> p(pairs); p != bp::stl_input_iterator<bp::tuple>(); p++) {
        set_username(bp::extract<const char *>((*p)[0])());
        login_wrapper(bp::extract<const char *>((*p)[1])());
    }
}


bool Cracker::login_wrapper(const char * password) {

    unsigned int attempt = 0;
    LoginResult result = RETRY;

    do {
        try {
            result = login(password);
        } catch(standard_error &e) {
            std::cout << "Error: " << e.what() << std::endl;
            disconnect();
            if(!retry_callback(++attempt))
                throw;
        }
    } while(result == RETRY);

    if(result == SUCCESS) {
        success_callback(username, password);
        // Continue with the next username.
        return true;
    }

    return false;
}

/*
 *
 */
void Cracker::connect() {

    struct sockaddr_in sin;
 
    socket_fd = socket(AF_INET, SOCK_STREAM, 0);

    fcntl(socket_fd, F_SETFL, O_NONBLOCK);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    inet_pton(AF_INET, dst_addr, &sin.sin_addr.s_addr);

    while(::connect(socket_fd, reinterpret_cast<struct sockaddr*>(&sin), sizeof(struct sockaddr_in))) {

        std::cout << "Connect Errno: " << errno << std::endl;

        switch(errno) {
            case EINPROGRESS: wait(); break;

            case ENETUNREACH:
            case EHOSTUNREACH:
                throw fatal_error(strerror(errno));

            default:
                throw standard_error(strerror(errno));
        }
    }
}

/*
 *
 */
void Cracker::wait() {

    std::cout << "waiting" << std::endl;

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

    if(!count_fds)
        throw standard_error("timeout error");

    if(count_fds < 0) {

        getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &so_error, &option_len);

        std::cout << "so_error == " << so_error << " - " << strerror(so_error) << std::endl;
        std::cout << "count_fds == " << count_fds << std::endl;
        
        throw standard_error("wait error");
    }
}

/* Code Smell:
 *     Is there a better way to do this? :S
 */
PyObject * fatal_error::python_type = PyErr_NewException("ssh.FatalError", NULL, NULL);
PyObject * standard_error::python_type = PyErr_NewException("ssh.StandardError", NULL, NULL);

/*
 *
 */
BOOST_PYTHON_MODULE(MODULE_NAME)
{
    bp::class_<CLASS_NAME,boost::noncopyable>
    main_class(STRINGIFY(CLASS_NAME), bp::init<bp::object&, bp::object&, const char *, uint16_t>());

    main_class.def("crack",
                   &CLASS_NAME::crack,
                   (bp::arg("usernames"), bp::arg("passwords"), bp::arg("pairs")));

    boost::python::register_exception_translator<fatal_error>(&translate_exception<fatal_error>);
    boost::python::register_exception_translator<standard_error>(&translate_exception<standard_error>);
}