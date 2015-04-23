#include <boost/python.hpp>

#include <ssh2_mod.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(ssh2)
{
    class_<SSH2>("SSH2CPP", init<std::string, short, int>())
        .def("try_login", &SSH2::try_login)
        .def_readonly("banner"           , &SSH2::banner)
        .def_readonly("CONNECTION_ERROR" , &SSH2::CONNECTION_ERROR)
		.def_readonly("TIMEOUT_ERROR"    , &SSH2::TIMEOUT_ERROR)
		.def_readonly("PROTOCOL_ERROR"   , &SSH2::PROTOCOL_ERROR)
		.def_readonly("LOGIN_SUCCESSFUL" , &SSH2::LOGIN_SUCCESSFUL)
		.def_readonly("LOGIN_FAILED"     , &SSH2::LOGIN_FAILED)
		.def_readonly("RETRY_LOGIN"      , &SSH2::RETRY_LOGIN)
    ;
}

