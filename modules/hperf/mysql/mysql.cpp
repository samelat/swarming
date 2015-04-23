#include <boost/python.hpp>

#include <mysql_mod.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(mysql)
{
    class_<MySQL>("MySQLCPP", init<std::string, unsigned short, unsigned int>())
        .def("try_login", &MySQL::try_login)
        .def_readonly("CONNECTION_ERROR", &MySQL::CONNECTION_ERROR)
		.def_readonly("TIMEOUT_ERROR"   , &MySQL::TIMEOUT_ERROR)
		.def_readonly("LOGIN_SUCCESSFUL", &MySQL::LOGIN_SUCCESSFUL)
		.def_readonly("LOGIN_FAILED"    , &MySQL::LOGIN_FAILED)
    ;
}
