
#include <module.hpp>

#include <iostream>

/*
 * The idea behind using an external socket insted native libraries
 * connections is to provide the basis for the use of socks.
 */
void Cracker::crack(bp::list usernames, bp::list passwords, bp::list pairs) {
    
    using string_iterator = bp::stl_input_iterator<const char *>;

    try {

        for(string_iterator usr(usernames); usr != string_iterator(); usr++) {
            set_username(*usr);
            for(string_iterator pwd(passwords); pwd != string_iterator(); pwd++)
                if(login(*pwd) == LoginResult::SUCCESS)
                    callback(username, *pwd);
        }

        for(bp::stl_input_iterator<bp::tuple> p(pairs); p != bp::stl_input_iterator<bp::tuple>(); p++) {
            set_username(bp::extract<const char *>((*p)[0])());
            if(login(bp::extract<const char *>((*p)[1])()) == LoginResult::SUCCESS)
                callback(username, bp::extract<const char *>((*p)[1])());
        }

    } catch(...) {
        std::cout << "Exception!!!" << std::endl;
    }
}

/*
 *
 */
Cracker::SocketState Cracker::connect() {

    std::cout << "Cracker::connect()\n";

    int error;
    struct sockaddr_in sin;
 
    socket_fd = socket(AF_INET, SOCK_STREAM, 0);

    //fcntl(sock, F_SETFL, O_NONBLOCK);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    inet_pton(AF_INET, dst_addr, &sin.sin_addr.s_addr);
    
    error = ::connect(socket_fd, reinterpret_cast<struct sockaddr*>(&sin), sizeof(struct sockaddr_in));
    if(!error)
        return SocketState::READY;

    return SocketState::ERROR;
}

/*
 *
 */
Cracker::SocketState Cracker::wait(const unsigned int secs) {

    int so_error, count_fds;
    socklen_t option_len = sizeof(so_error);
    
    fd_set read_set;
    struct timeval timeout;

    FD_ZERO(&read_set);
    FD_SET(socket_fd, &read_set);
    timeout.tv_sec  = secs;
    timeout.tv_usec = 0;
    
    std::cout << "esperando\n";
    count_fds = select(socket_fd + 1, &read_set, NULL, NULL, &timeout);
    std::cout << "listo\n";
    if(count_fds > 0)
        return SocketState::READY;
    
    getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &so_error, &option_len);

    std::cout << "so_error  == " << so_error  << std::endl;
    std::cout << "count_fds == " << count_fds << std::endl;
    std::cout << "errno == " << errno << std::endl;
    
    if(!(so_error || count_fds))
        return SocketState::TIMEOUT;
    
    return SocketState::ERROR;
}

/*
 *
 */
BOOST_PYTHON_MODULE(MODULE_NAME)
{
    bp::class_<CLASS_NAME>(STRINGIFY(CLASS_NAME), bp::init<bp::object&, const char *, uint16_t, const unsigned int>())
        .def("crack",
             &CLASS_NAME::crack,
             (bp::arg("usernames"), bp::arg("passwords"), bp::arg("pairs")));
}