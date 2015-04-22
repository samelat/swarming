#include <boost/python.hpp>

#include <ssh2_mod.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(ssh2) {
    class_<SSH2>("SSH2", init<std::string, short, int>())
        .def("try_login", &SSH2::try_login)
        .def_readonly("CONNECTION_ERROR", &SSH2::CONNECTION_ERROR)
		.def_readonly("SESSION_ERROR"   , &SSH2::SESSION_ERROR)
		.def_readonly("HANDSHAKE_ERROR" , &SSH2::HANDSHAKE_ERROR)
		.def_readonly("TIMEOUT_ERROR"   , &SSH2::TIMEOUT_ERROR)
		.def_readonly("LOGIN_SUCCESSFUL", &SSH2::LOGIN_SUCCESSFUL)
		.def_readonly("CONTINUE_ERROR"  , &SSH2::CONTINUE_ERROR)
		.def_readonly("AUTH_ERROR"      , &SSH2::AUTH_ERROR)
    ;
}
